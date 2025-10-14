from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import ClienteCreate, ClienteResponse, MessageResponse
from app.services.services import ClienteService
from app.routers.auth import get_current_user
from app.models.models import Cuenta

router = APIRouter()

@router.post("/", response_model=ClienteResponse)
async def crear_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo cliente en el banco o obtener cliente existente
    """
    try:
        # Primero verificar si ya existe un cliente con estos datos
        cliente_existente = ClienteService.obtener_cliente_por_identificacion(
            db,
            identificacion=cliente_data.identificacion,
            ruc=cliente_data.ruc,
            correo=cliente_data.per_correo
        )
        
        if cliente_existente:
            # Si el cliente ya existe, devolver sus datos
            return cliente_existente
        
        # Si no existe, crear nuevo cliente
        cliente = ClienteService.crear_cliente(db, cliente_data)
        return cliente
    except ValueError as e:
        # Error de validación específico (duplicados)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear cliente: {str(e)}"
        )

@router.get("/", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Listar todos los clientes (requiere autenticación)
    """
    clientes = ClienteService.listar_clientes(db, skip=skip, limit=limit)
    return clientes

@router.get("/{per_id}/{cli_id}", response_model=ClienteResponse)
async def obtener_cliente(
    per_id: int,
    cli_id: int,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Obtener información de un cliente específico
    """
    cliente = ClienteService.obtener_cliente_por_id(db, per_id, cli_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente no encontrado"
        )
    return cliente
