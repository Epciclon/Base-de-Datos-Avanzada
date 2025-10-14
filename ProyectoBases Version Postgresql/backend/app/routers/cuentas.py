from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import (
    CuentaCreate, CuentaAhorroCreate, CuentaCorrienteCreate, 
    CuentaResponse, ConsultaSaldoResponse, MessageResponse
)
from app.services.services import CuentaService
from app.routers.auth import get_current_user
from app.models.models import Cuenta
from datetime import datetime

router = APIRouter()

@router.post("/ahorro", response_model=CuentaResponse)
async def crear_cuenta_ahorro(
    cuenta_data: CuentaAhorroCreate,
    per_id: int,
    cli_id: int,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva cuenta de ahorros para un cliente
    """
    try:
        cuenta = CuentaService.crear_cuenta(db, cuenta_data, per_id, cli_id)
        return cuenta
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cuenta: {str(e)}"
        )

@router.post("/corriente", response_model=CuentaResponse)
async def crear_cuenta_corriente(
    cuenta_data: CuentaCorrienteCreate,
    per_id: int,
    cli_id: int,
    db: Session = Depends(get_db)
):
    """
    Crear una nueva cuenta corriente para un cliente
    """
    try:
        cuenta = CuentaService.crear_cuenta(db, cuenta_data, per_id, cli_id)
        return cuenta
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cuenta: {str(e)}"
        )

@router.get("/saldo", response_model=ConsultaSaldoResponse)
async def consultar_saldo(
    current_user: Cuenta = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Consultar el saldo de la cuenta del usuario autenticado
    """
    return {
        "numero_cuenta": current_user.cuen_numero_cuenta,
        "saldo": current_user.cuen_saldo,
        "tipo_cuenta": current_user.cuen_tipo,
        "estado": current_user.cuen_estado,
        "fecha_consulta": datetime.now()
    }

@router.get("/mis-cuentas", response_model=List[CuentaResponse])
async def obtener_mis_cuentas(
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Obtener todas las cuentas del usuario autenticado
    """
    try:
        # Obtener cuentas por PER_ID y CLI_ID del usuario autenticado
        cuentas = db.query(Cuenta).filter(
            Cuenta.per_id == current_user.per_id,
            Cuenta.cli_id == current_user.cli_id
        ).all()
        return cuentas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cuentas: {str(e)}"
        )

@router.get("/{cuenta_id}", response_model=CuentaResponse)
async def obtener_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Obtener información de una cuenta específica
    """
    cuenta = db.query(Cuenta).filter(Cuenta.cuen_id == cuenta_id).first()
    if not cuenta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuenta no encontrada"
        )
    return cuenta
