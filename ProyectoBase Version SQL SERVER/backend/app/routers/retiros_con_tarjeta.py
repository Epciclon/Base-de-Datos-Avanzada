from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from decimal import Decimal

from app.database import get_db
from app.models.models import (
    Cuenta, Cajero, Transaccion, Retiro, RetiroConTarjeta, 
    Tarjeta, BoucherCabecera, BoucherCuerpo
)
from app.schemas.schemas import RetiroCreate, RetiroResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/retiros-con-tarjeta")

def obtener_siguiente_id(db: Session, tabla) -> int:
    """Obtiene el siguiente ID disponible para una tabla"""
    max_id = db.query(func.max(tabla.TRAN_ID)).scalar()
    return 1 if max_id is None else max_id + 1

def obtener_siguiente_ret_id(db: Session) -> int:
    """Obtiene el siguiente RET_ID disponible"""
    max_ret_id = db.query(func.max(Retiro.RET_ID)).scalar()
    return 1 if max_ret_id is None else max_ret_id + 1

def obtener_siguiente_bouc_id(db: Session) -> int:
    """Obtiene el siguiente BOUC_ID disponible"""
    max_bouc_id = db.query(func.max(BoucherCuerpo.BOUC_ID)).scalar()
    return 1 if max_bouc_id is None else max_bouc_id + 1

def obtener_o_crear_cabecera_boucher(db: Session) -> str:
    """Obtiene o crea la cabecera del boucher por defecto"""
    cabecera = db.query(BoucherCabecera).first()
    
    if not cabecera:
        # Crear cabecera por defecto
        cabecera = BoucherCabecera(
            BAN_AID="BP001",
            BAN_NOMBRE="Banco Pichincha S.A.",
            BAN_DIRECCION="Av. Amazonas y Naciones Unidas, Quito",
            BAN_RUC="1790010937001",
            BAN_MENSAJE="Gracias por confiar en Banco Pichincha. Para consultas: 1800-PICHINCHA"
        )
        db.add(cabecera)
        db.flush()
    
    return cabecera.BAN_AID

@router.post("/procesar", response_model=dict)
def procesar_retiro_con_tarjeta(
    request: RetiroCreate,
    db: Session = Depends(get_db)
):
    """Procesa un retiro con tarjeta desde cajero ATM (sin autenticación)"""
    try:
        # Validar que es retiro con tarjeta
        if request.tipo_retiro != "CON_TARJETA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este endpoint es solo para retiros con tarjeta"
            )
        
        if not request.TAR_NUMERO_TARJETA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de tarjeta es requerido"
            )
        
        # Buscar tarjeta y obtener cuenta asociada
        tarjeta = db.query(Tarjeta).filter(
            Tarjeta.TAR_NUMERO_TARJETA == request.TAR_NUMERO_TARJETA,
            Tarjeta.TAR_ESTADO_TARJETA == "ACTIVA"
        ).first()
        
        if not tarjeta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarjeta no encontrada o inactiva"
            )
        
        # Obtener cuenta asociada a la tarjeta
        cuenta = db.query(Cuenta).filter(
            Cuenta.CUEN_ID == tarjeta.CUEN_ID
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta asociada no encontrada"
            )
        
        if cuenta.CUEN_ESTADO != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cuenta no está activa"
            )
        
        # Verificar saldo suficiente (monto + costo boucher si aplica)
        monto_retiro = Decimal(str(request.RET_MONTO))
        costo_boucher = Decimal('0.36') if request.IMPRIMIR_BOUCHER == "SI" else Decimal('0.00')
        monto_total = monto_retiro + costo_boucher
        
        # Convertir saldo a Decimal para comparación consistente
        saldo_actual = Decimal(str(cuenta.CUEN_SALDO))
        if saldo_actual < monto_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Saldo disponible: ${cuenta.CUEN_SALDO}"
            )
        
        # Verificar cajero
        cajero = db.query(Cajero).filter(Cajero.CAJ_ID == request.CAJ_ID).first()
        if not cajero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cajero no encontrado"
            )
        
        # Obtener IDs únicos
        tran_id = obtener_siguiente_id(db, Transaccion)
        ret_id = obtener_siguiente_ret_id(db)
        
        # 1. Crear la transacción principal (tabla padre)
        nueva_transaccion = Transaccion(
            TRAN_ID=tran_id,
            CUEN_ID=cuenta.CUEN_ID,
            CAJ_ID=request.CAJ_ID
        )
        db.add(nueva_transaccion)
        db.flush()
        
        # 2. Crear registro en RETIRO (tabla hija de TRANSACCION)
        nuevo_retiro = Retiro(
            TRAN_ID=tran_id,
            RET_ID=ret_id,
            CUEN_ID=cuenta.CUEN_ID,
            CAJ_ID=request.CAJ_ID,
            RET_FECHA=datetime.now(),
            RET_MONTO=int(request.RET_MONTO),
            RET_CAJERO="ONLINE",
            RET_NUMERO_TRAN=str(tran_id)[-4:].zfill(4),
        )
        db.add(nuevo_retiro)
        db.flush()
        
        # 3. Crear registro en RETIRO_CONTARJETA (tabla hija de RETIRO)
        nuevo_retiro_con_tarjeta = RetiroConTarjeta(
            TRAN_ID=tran_id,
            RET_ID=ret_id,
            CUEN_ID=cuenta.CUEN_ID,
            CAJ_ID=request.CAJ_ID,
            RET_FECHA=datetime.now(),
            RET_MONTO=int(request.RET_MONTO),
            RET_CAJERO="ONLINE",
            RET_NUMERO_TRAN=str(tran_id)[-4:].zfill(4),
            RETT_IMPRIMIR=request.IMPRIMIR_BOUCHER,
            RETT_MONTOMAX=500,  # Siempre 500 como especificaste
        )
        db.add(nuevo_retiro_con_tarjeta)
        db.flush()
        
        # 4. Crear boucher si se solicita imprimir
        boucher_creado = False
        costo_boucher_fijo = Decimal('0.36')  # Siempre 0.36
        
        if request.IMPRIMIR_BOUCHER == "SI":
            total_debitado = monto_retiro + costo_boucher_fijo  # monto + 0.36
            
            # Obtener o crear cabecera
            ban_aid = obtener_o_crear_cabecera_boucher(db)
            
            # Crear cuerpo del boucher
            bouc_id = obtener_siguiente_bouc_id(db)
            
            # Debug para verificar valores
            print(f"DEBUG - costo_boucher_fijo: {costo_boucher_fijo}, tipo: {type(costo_boucher_fijo)}")
            print(f"DEBUG - total_debitado: {total_debitado}, tipo: {type(total_debitado)}")
            
            nuevo_boucher = BoucherCuerpo(
                BOUC_ID=bouc_id,
                RETT_IMPRIMIR=request.IMPRIMIR_BOUCHER,
                RETT_MONTOMAX=500,
                TRAN_ID=tran_id,
                RET_ID=ret_id,
                CUEN_ID=cuenta.CUEN_ID,
                CAJ_ID=request.CAJ_ID,
                RET_FECHA=datetime.now(),
                RET_MONTO=int(request.RET_MONTO),
                RET_CAJERO="ONLINE",
                RET_NUMERO_TRAN=str(tran_id)[-4:].zfill(4),
                BAN_AID=ban_aid,
                BOUC_COSTO=costo_boucher_fijo,  # Valor decimal directo (0.36)
                BOUC_TOTALDEBITADO=total_debitado,  # Valor decimal directo (ej: 10.36)
            )
            print(f"DEBUG - Valores para insertar - BOUC_COSTO: {nuevo_boucher.BOUC_COSTO}, BOUC_TOTALDEBITADO: {nuevo_boucher.BOUC_TOTALDEBITADO}")
            print(f"DEBUG - Tipos de valores - BOUC_COSTO: {type(nuevo_boucher.BOUC_COSTO)}, BOUC_TOTALDEBITADO: {type(nuevo_boucher.BOUC_TOTALDEBITADO)}")
            
            db.add(nuevo_boucher)
            print(f"DEBUG - Después de add() - BOUC_COSTO: {nuevo_boucher.BOUC_COSTO}, BOUC_TOTALDEBITADO: {nuevo_boucher.BOUC_TOTALDEBITADO}")
            
            # Hacer flush para forzar la inserción y ver si hay errores
            try:
                db.flush()
                print(f"DEBUG - Después de flush() - BOUC_COSTO: {nuevo_boucher.BOUC_COSTO}, BOUC_TOTALDEBITADO: {nuevo_boucher.BOUC_TOTALDEBITADO}")
                
            except Exception as flush_error:
                print(f"ERROR en flush: {flush_error}")
                raise
            boucher_creado = True
        else:
            # Si no hay boucher, el total debitado es solo el monto
            total_debitado = monto_retiro
        
        # Actualizar saldo de la cuenta - siempre descontar el total calculado
        # Convertir saldo actual a Decimal para operaciones consistentes
        saldo_actual = Decimal(str(cuenta.CUEN_SALDO))
        nuevo_saldo = saldo_actual - total_debitado
        cuenta.CUEN_SALDO = nuevo_saldo
        
        # Confirmar todos los cambios
        db.commit()
        
        # Debug final: verificar qué se guardó realmente en la base de datos
        if boucher_creado:
            # Refrescar el objeto desde la base de datos
            db.refresh(nuevo_boucher)
            print(f"DEBUG FINAL - Valores guardados en BD - BOUC_COSTO: {nuevo_boucher.BOUC_COSTO}, BOUC_TOTALDEBITADO: {nuevo_boucher.BOUC_TOTALDEBITADO}")
            print(f"DEBUG FINAL - Tipos después de commit - BOUC_COSTO: {type(nuevo_boucher.BOUC_COSTO)}, BOUC_TOTALDEBITADO: {type(nuevo_boucher.BOUC_TOTALDEBITADO)}")
            
            # Consulta directa SQL para verificar valores reales en la base de datos
            sql_check = text("""
                SELECT BOUC_COSTO, BOUC_TOTALDEBITADO 
                FROM BOUCHER_CUERPO 
                WHERE BOUC_ID = :bouc_id AND TRAN_ID = :tran_id AND RET_ID = :ret_id
            """)
            result = db.execute(sql_check, {
                "bouc_id": bouc_id,
                "tran_id": tran_id, 
                "ret_id": ret_id
            }).fetchone()
            if result:
                print(f"DEBUG SQL DIRECTO - BOUC_COSTO: {result[0]}, BOUC_TOTALDEBITADO: {result[1]}")
                print(f"DEBUG SQL DIRECTO - Tipos: {type(result[0])}, {type(result[1])}")
        
        mensaje = "Retiro con tarjeta procesado exitosamente"
        if boucher_creado:
            mensaje += f" - Boucher impreso (Costo: $0.36 - Total debitado: ${float(total_debitado):.2f})"
        else:
            mensaje += f" - Total debitado: ${float(total_debitado):.2f}"
        
        return {
            "mensaje": mensaje,
            "tran_id": tran_id,
            "ret_id": ret_id,
            "monto_retirado": float(monto_retiro),
            "nuevo_saldo": float(cuenta.CUEN_SALDO),
            "numero_transaccion": str(tran_id)[-4:].zfill(4),
            "fecha_transaccion": datetime.now().isoformat(),
            "boucher_impreso": boucher_creado,
            "costo_boucher": float(costo_boucher_fijo) if boucher_creado else 0.0,
            "total_debitado": float(total_debitado)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error procesando retiro con tarjeta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar el retiro"
        )
