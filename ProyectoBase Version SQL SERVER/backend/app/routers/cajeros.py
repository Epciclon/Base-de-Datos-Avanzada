from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import CajeroCreate, CajeroResponse, MessageResponse
from app.routers.auth import get_current_user
from app.models.models import Cuenta, Cajero

router = APIRouter()

@router.post("/", response_model=CajeroResponse)
async def crear_cajero(
    cajero_data: CajeroCreate,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Registrar un nuevo cajero automático
    """
    # Generar nuevo CAJ_ID
    max_cajero = db.query(Cajero).order_by(Cajero.CAJ_ID.desc()).first()
    new_caj_id = (max_cajero.CAJ_ID + 1) if max_cajero else 1
    
    cajero = Cajero(
        CAJ_ID=new_caj_id,
        CAJ_UBICACION=cajero_data.CAJ_UBICACION,
        CAJ_ESTADO=cajero_data.CAJ_ESTADO,
        CAJ_TIPO=cajero_data.CAJ_TIPO,
        CAJ_SUCURSAL=cajero_data.CAJ_SUCURSAL
    )
    
    db.add(cajero)
    db.commit()
    db.refresh(cajero)
    
    return cajero

@router.get("/", response_model=List[CajeroResponse])
async def listar_cajeros(
    estado: str = None,
    sucursal: str = None,
    db: Session = Depends(get_db)
):
    """
    Listar todos los cajeros automáticos disponibles
    """
    query = db.query(Cajero)
    
    if estado:
        query = query.filter(Cajero.CAJ_ESTADO == estado)
    
    if sucursal:
        query = query.filter(Cajero.CAJ_SUCURSAL.contains(sucursal))
    
    cajeros = query.all()
    return cajeros

@router.get("/activos", response_model=List[CajeroResponse])
async def listar_cajeros_activos(db: Session = Depends(get_db)):
    """
    Listar solo los cajeros automáticos activos
    """
    cajeros = db.query(Cajero).filter(Cajero.CAJ_ESTADO == "ACTIVO").all()
    return cajeros

@router.get("/{cajero_id}", response_model=CajeroResponse)
async def obtener_cajero(
    cajero_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener información de un cajero específico
    """
    cajero = db.query(Cajero).filter(Cajero.CAJ_ID == cajero_id).first()
    if not cajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cajero no encontrado"
        )
    return cajero

@router.put("/{cajero_id}/estado")
async def cambiar_estado_cajero(
    cajero_id: int,
    nuevo_estado: str,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Cambiar el estado de un cajero (ACTIVO, INACTIVO, MANTENIMIENTO)
    """
    cajero = db.query(Cajero).filter(Cajero.CAJ_ID == cajero_id).first()
    if not cajero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cajero no encontrado"
        )
    
    estados_validos = ["ACTIVO", "INACTIVO", "MANTENIMIENTO"]
    if nuevo_estado not in estados_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}"
        )
    
    cajero.CAJ_ESTADO = nuevo_estado
    db.commit()
    
    return {"mensaje": f"Estado del cajero actualizado a {nuevo_estado}"}
