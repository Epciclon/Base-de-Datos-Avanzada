from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.schemas import LoginRequest, LoginResponse, TokenData
from app.services.services import CuentaService
from app.models.models import Cuenta
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = CuentaService.obtener_cuenta_por_usuario(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Iniciar sesión con usuario y contraseña de cuenta bancaria
    """
    cuenta = CuentaService.obtener_cuenta_por_usuario(db, login_data.usuario)
    
    if not cuenta or not CuentaService.verificar_password(login_data.password, cuenta.cuen_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if cuenta.cuen_estado != "ACTIVA":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta no está activa"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": cuenta.cuen_usuario}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": cuenta.cuen_usuario,
        "cuenta_id": cuenta.cuen_id
    }

@router.get("/me")
async def read_users_me(current_user: Cuenta = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado
    """
    return {
        "usuario": current_user.cuen_usuario,
        "cuenta_id": current_user.cuen_id,
        "numero_cuenta": current_user.cuen_numero_cuenta,
        "tipo_cuenta": current_user.cuen_tipo,
        "estado": current_user.cuen_estado,
        "saldo": current_user.cuen_saldo
    }
