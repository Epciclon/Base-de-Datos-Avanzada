from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import TarjetaCreate, TarjetaResponse, MessageResponse
from app.services.services import TarjetaService
from app.routers.auth import get_current_user
from app.models.models import Cuenta, Tarjeta
from pydantic import BaseModel

class TarjetaValidacion(BaseModel):
    TAR_NUMERO_TARJETA: str
    TAR_PIN: str

router = APIRouter()

@router.post("/", response_model=TarjetaResponse)
async def crear_tarjeta(
    tarjeta_data: TarjetaCreate,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Crear una nueva tarjeta para una cuenta
    """
    # Verificar que la cuenta pertenece al usuario autenticado o es la cuenta del usuario
    if tarjeta_data.CUEN_ID != current_user.CUEN_ID:
        cuenta_destino = db.query(Cuenta).filter(Cuenta.CUEN_ID == tarjeta_data.CUEN_ID).first()
        if not cuenta_destino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada"
            )
        # Aquí podrías agregar lógica adicional para verificar permisos
    
    try:
        tarjeta = TarjetaService.crear_tarjeta(db, tarjeta_data)
        return tarjeta
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear tarjeta: {str(e)}"
        )

@router.get("/mis-tarjetas", response_model=List[TarjetaResponse])
async def obtener_mis_tarjetas(
    current_user: Cuenta = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las tarjetas del usuario autenticado
    """
    tarjetas = db.query(Tarjeta).filter(Tarjeta.CUEN_ID == current_user.CUEN_ID).all()
    return tarjetas

@router.get("/{tarjeta_id}", response_model=TarjetaResponse)
async def obtener_tarjeta(
    tarjeta_id: int,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Obtener información de una tarjeta específica
    """
    tarjeta = db.query(Tarjeta).filter(Tarjeta.TAR_ID == tarjeta_id).first()
    if not tarjeta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada"
        )
    
    # Verificar que la tarjeta pertenece al usuario autenticado
    if tarjeta.CUEN_ID != current_user.CUEN_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver esta tarjeta"
        )
    
    return tarjeta

@router.put("/{tarjeta_id}/estado")
async def cambiar_estado_tarjeta(
    tarjeta_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Cambiar el estado de una tarjeta (ACTIVA, BLOQUEADA, CANCELADA)
    """
    tarjeta = db.query(Tarjeta).filter(Tarjeta.TAR_ID == tarjeta_id).first()
    if not tarjeta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarjeta no encontrada"
        )
    
    # Verificar que la tarjeta pertenece al usuario autenticado
    if tarjeta.CUEN_ID != current_user.CUEN_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para modificar esta tarjeta"
        )
    
    estados_validos = ["ACTIVA", "BLOQUEADA", "CANCELADA"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}"
        )
    
    tarjeta.TAR_ESTADO_TARJETA = nuevo_estado
    db.commit()
    
    return {"mensaje": f"Estado de tarjeta actualizado a {nuevo_estado}"}

@router.post("/validar")
async def validar_tarjeta(
    validacion_data: TarjetaValidacion,
    db: Session = Depends(get_db)
):
    """
    Validar tarjeta y PIN para uso en cajero (sin autenticación)
    """
    try:
        # Buscar tarjeta por número
        tarjeta = db.query(Tarjeta).filter(
            Tarjeta.TAR_NUMERO_TARJETA == validacion_data.TAR_NUMERO_TARJETA
        ).first()
        
        if not tarjeta:
            return {"valida": False, "mensaje": "Tarjeta no encontrada"}
        
        # Verificar estado de la tarjeta
        if tarjeta.TAR_ESTADO_TARJETA != "ACTIVA":
            return {"valida": False, "mensaje": "Tarjeta no activa"}
        
        # Verificar PIN
        if tarjeta.TAR_PIN != validacion_data.TAR_PIN:
            return {"valida": False, "mensaje": "PIN incorrecto"}
        
        # Verificar fecha de vencimiento si está presente
        from datetime import datetime
        if tarjeta.TAR_FECHA_VENCIMIENTO and tarjeta.TAR_FECHA_VENCIMIENTO < datetime.now().date():
            return {"valida": False, "mensaje": "Tarjeta vencida"}
        
        return {
            "valida": True,
            "TAR_ID": tarjeta.TAR_ID,
            "CUEN_ID": tarjeta.CUEN_ID,
            "mensaje": "Tarjeta válida"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar tarjeta: {str(e)}"
        )
