from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import RetiroCreate, RetiroResponse, MessageResponse
from app.services.services import TransaccionService
from app.routers.auth import get_current_user
from app.models.models import Cuenta, Transaccion, Retiro, Tarjeta, TarjetaDebito, TarjetaCredito, Cajero, RetiroSinTarjeta
from datetime import datetime

router = APIRouter()

@router.post("/retiro", response_model=RetiroResponse)
async def procesar_retiro(
    retiro_data: RetiroCreate,
    db: Session = Depends(get_db)
):
    """
    Procesar un retiro con tarjeta o sin tarjeta
    """
    try:
        resultado = TransaccionService.procesar_retiro(db, retiro_data)
        return resultado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar retiro: {str(e)}"
        )

@router.get("/mis-transacciones")
async def obtener_mis_transacciones(
    limit: int = 20,
    current_user: Cuenta = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener las transacciones del usuario autenticado
    """
    transacciones = db.query(Transaccion).filter(
        Transaccion.CUEN_ID == current_user.CUEN_ID
    ).order_by(Transaccion.TRAN_ID.desc()).limit(limit).all()
    
    resultado = []
    for trans in transacciones:
        # Buscar detalles del retiro si existe
        retiro = db.query(Retiro).filter(Retiro.TRAN_ID == trans.TRAN_ID).first()
        if retiro:
            resultado.append({
                "transaccion_id": trans.TRAN_ID,
                "tipo": "RETIRO",
                "fecha": retiro.RET_FECHA,
                "monto": retiro.RET_MONTO,
                "numero_transaccion": retiro.RET_NUMERO_TRAN,
                "cajero": retiro.RET_CAJERO
            })
    
    return resultado

@router.get("/retiros/{transaccion_id}")
async def obtener_detalle_retiro(
    transaccion_id: int,
    db: Session = Depends(get_db),
    current_user: Cuenta = Depends(get_current_user)
):
    """
    Obtener el detalle de un retiro específico
    """
    transaccion = db.query(Transaccion).filter(
        Transaccion.TRAN_ID == transaccion_id,
        Transaccion.CUEN_ID == current_user.CUEN_ID
    ).first()
    
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )
    
    retiro = db.query(Retiro).filter(Retiro.TRAN_ID == transaccion_id).first()
    if not retiro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retiro no encontrado"
        )
    
    return {
        "transaccion_id": transaccion.TRAN_ID,
        "retiro_id": retiro.RET_ID,
        "fecha": retiro.RET_FECHA,
        "monto": retiro.RET_MONTO,
        "numero_transaccion": retiro.RET_NUMERO_TRAN,
        "cajero": retiro.RET_CAJERO,
        "cuenta_id": retiro.CUEN_ID,
        "cajero_id": retiro.CAJ_ID
    }

@router.get("/movimientos")
async def obtener_movimientos(
    limit: int = 50,
    current_user: Cuenta = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener movimientos (retiros completados) del usuario autenticado con información de tarjetas
    """
    try:
        # Obtener retiros completados de la cuenta del usuario
        # Solo retiros que tienen TRAN_ID (fueron procesados completamente)
        retiros = db.query(Retiro).join(Transaccion).filter(
            Retiro.CUEN_ID == current_user.CUEN_ID,
            Retiro.TRAN_ID.isnot(None)  # Solo retiros que tienen transacción asociada (completados)
        ).order_by(Retiro.RET_FECHA.desc()).limit(limit).all()
        
        movimientos = []
        for retiro in retiros:
            # Obtener información del cajero
            cajero = db.query(Cajero).filter(Cajero.CAJ_ID == retiro.CAJ_ID).first()
            cajero_info = {
                "ubicacion": cajero.CAJ_UBICACION if cajero else "N/A",
                "tipo": cajero.CAJ_TIPO if cajero else "N/A"
            }
            
            # Buscar si fue un retiro con tarjeta
            tarjeta_info = None
            metodo = "SIN TARJETA"  # Por defecto
            estado_codigo = None
            
            # Primero verificar si es un retiro sin tarjeta
            retiro_sin_tarjeta = db.query(RetiroSinTarjeta).filter(
                RetiroSinTarjeta.TRAN_ID == retiro.TRAN_ID,
                RetiroSinTarjeta.RET_ID == retiro.RET_ID
            ).first()
            
            if retiro_sin_tarjeta:
                # Es un retiro sin tarjeta
                metodo = "SIN TARJETA"
                estado_codigo = retiro_sin_tarjeta.RETS_ESTADO_CODIGO
                # Solo mostrar retiros sin tarjeta que se completaron (USADO)
                if estado_codigo != 'USADO':
                    continue  # Saltar este retiro si no está completado
            elif retiro.RET_NUMERO_TRAN:  # Si tiene número de transacción, es con tarjeta
                metodo = "CON TARJETA"
                # Buscar en tarjetas de débito
                tarjeta_debito = db.query(TarjetaDebito).join(Tarjeta).filter(
                    Tarjeta.CUEN_ID == current_user.CUEN_ID
                ).first()
                
                if tarjeta_debito:
                    tarjeta = db.query(Tarjeta).filter(
                        Tarjeta.TAR_ID == tarjeta_debito.TAR_ID
                    ).first()
                    if tarjeta:
                        tarjeta_info = {
                            "numero": f"****-****-****-{tarjeta.TAR_NUMERO_TARJETA[-4:]}",
                            "tipo": "DÉBITO"
                        }
                
                # Si no se encontró débito, buscar en crédito
                if not tarjeta_info:
                    tarjeta_credito = db.query(TarjetaCredito).join(Tarjeta).filter(
                        Tarjeta.CUEN_ID == current_user.CUEN_ID
                    ).first()
                    
                    if tarjeta_credito:
                        tarjeta = db.query(Tarjeta).filter(
                            Tarjeta.TAR_ID == tarjeta_credito.TAR_ID
                        ).first()
                        if tarjeta:
                            tarjeta_info = {
                                "numero": f"****-****-****-{tarjeta.TAR_NUMERO_TARJETA[-4:]}",
                                "tipo": "CRÉDITO"
                            }
            else:
                # Retiro sin número de transacción ni retiro sin tarjeta - probablemente inconsistencia
                continue
            
            movimiento = {
                "id": retiro.RET_ID,
                "transaccion_id": retiro.TRAN_ID,
                "fecha": retiro.RET_FECHA.strftime("%Y-%m-%d %H:%M:%S"),
                "monto": float(retiro.RET_MONTO),
                "tipo_movimiento": "RETIRO",
                "numero_transaccion": retiro.RET_NUMERO_TRAN,
                "cajero": cajero_info,
                "tarjeta": tarjeta_info,
                "metodo": metodo,
                "estado_codigo": estado_codigo  # Solo para retiros sin tarjeta
            }
            
            movimientos.append(movimiento)
        
        return {
            "movimientos": movimientos,
            "total": len(movimientos)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener movimientos: {str(e)}"
        )
