from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Tarjeta, TarjetaDebito, TarjetaCredito, Cuenta
from app.services.services import TarjetaService, CuentaService
from pydantic import BaseModel

router = APIRouter()

class ValidarTarjetaRequest(BaseModel):
    numero_tarjeta: str
    pin: str

class ValidarTarjetaResponse(BaseModel):
    valida: bool
    usuario: dict = None
    mensaje: str = ""

@router.post("/validar", response_model=ValidarTarjetaResponse)
async def validar_tarjeta(request: ValidarTarjetaRequest, db: Session = Depends(get_db)):
    """
    Validar tarjeta y PIN para uso en cajero ATM
    """
    try:
        # Buscar tarjeta por número
        tarjeta = db.query(Tarjeta).filter(Tarjeta.TAR_NUMERO_TARJETA == request.numero_tarjeta).first()
        
        if not tarjeta:
            return ValidarTarjetaResponse(
                valida=False,
                mensaje="Número de tarjeta no encontrado"
            )
        
        # Verificar estado de la tarjeta
        if tarjeta.TAR_ESTADO_TARJETA != 'ACTIVA':
            return ValidarTarjetaResponse(
                valida=False,
                mensaje="Tarjeta inactiva o bloqueada"
            )
        
        # Validar PIN (comparación directa ya que está en texto plano según el esquema)
        if tarjeta.TAR_PIN != request.pin:
            return ValidarTarjetaResponse(
                valida=False,
                mensaje="PIN incorrecto"
            )
        
        # Obtener información de la cuenta asociada
        cuenta = db.query(Cuenta).filter(Cuenta.CUEN_ID == tarjeta.CUEN_ID).first()
        
        if not cuenta:
            return ValidarTarjetaResponse(
                valida=False,
                mensaje="Cuenta asociada no encontrada"
            )
        
        # Crear respuesta exitosa
        usuario_info = {
            "usuario": cuenta.CUEN_USUARIO,
            "cuenta_id": cuenta.CUEN_ID,
            "tipo_cuenta": cuenta.CUEN_TIPO,
            "saldo": float(cuenta.CUEN_SALDO)
        }
        
        return ValidarTarjetaResponse(
            valida=True,
            usuario=usuario_info,
            mensaje="Autenticación exitosa"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

class GenerarCodigoRetiroRequest(BaseModel):
    celular: str
    monto: float
    cuenta_id: int

class GenerarCodigoRetiroResponse(BaseModel):
    codigo: str
    expiracion: str
    mensaje: str

@router.post("/generar-codigo-retiro", response_model=GenerarCodigoRetiroResponse)
async def generar_codigo_retiro(request: GenerarCodigoRetiroRequest, db: Session = Depends(get_db)):
    """
    Generar código para retiro sin tarjeta
    """
    try:
        from datetime import datetime, timedelta
        import random
        
        # Validar monto
        if request.monto < 10 or request.monto > 300:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El monto debe estar entre $10 y $300"
            )
        
        # Generar código de 6 dígitos
        codigo = str(random.randint(100000, 999999))
        
        # Calcular fecha de expiración (15 minutos)
        expiracion = datetime.now() + timedelta(minutes=15)
        
        # TODO: Aquí se debería guardar el código en una tabla temporal
        # Por ahora solo devolvemos el código generado
        
        return GenerarCodigoRetiroResponse(
            codigo=codigo,
            expiracion=expiracion.isoformat(),
            mensaje="Código generado exitosamente. Válido por 15 minutos."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

class ValidarCodigoRetiroRequest(BaseModel):
    codigo: str
    celular: str

class ValidarCodigoRetiroResponse(BaseModel):
    valido: bool
    mensaje: str
    datos_retiro: dict = None

@router.post("/validar-codigo-retiro", response_model=ValidarCodigoRetiroResponse)
async def validar_codigo_retiro(request: ValidarCodigoRetiroRequest, db: Session = Depends(get_db)):
    """
    Validar código de retiro sin tarjeta
    """
    try:
        # TODO: Implementar validación real del código desde base de datos temporal
        # Por ahora, simulamos la validación
        
        return ValidarCodigoRetiroResponse(
            valido=True,
            mensaje="Código válido",
            datos_retiro={
                "monto": 50.0,
                "cuenta": "Cuenta de prueba"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
