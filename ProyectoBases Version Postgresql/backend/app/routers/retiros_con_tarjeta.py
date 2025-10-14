from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from decimal import Decimal
import pytz

from app.database import get_db
from app.models.models import (
    Cuenta, Cajero, Transaccion, Retiro, RetiroConTarjeta, 
    Tarjeta, BoucherCabecera, BoucherCuerpo
)
from app.schemas.schemas import RetiroCreate, RetiroResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/retiros-con-tarjeta")

def obtener_fecha_ecuador():
    """Obtiene la fecha y hora actual en zona horaria de Ecuador (UTC-5)"""
    ecuador_tz = pytz.timezone('America/Guayaquil')
    return datetime.now(ecuador_tz).replace(tzinfo=None)

def obtener_siguiente_id(db: Session, tabla) -> int:
    """Obtiene el siguiente ID disponible para una tabla"""
    max_id = db.query(func.max(tabla.tran_id)).scalar()
    return 1 if max_id is None else max_id + 1

def obtener_siguiente_ret_id(db: Session) -> int:
    """Obtiene el siguiente RET_ID disponible"""
    max_ret_id = db.query(func.max(Retiro.ret_id)).scalar()
    return 1 if max_ret_id is None else max_ret_id + 1

def obtener_siguiente_bouc_id(db: Session) -> int:
    """Obtiene el siguiente BOUC_ID disponible"""
    max_bouc_id = db.query(func.max(BoucherCuerpo.bouc_id)).scalar()
    return 1 if max_bouc_id is None else max_bouc_id + 1

def obtener_o_crear_cabecera_boucher(db: Session) -> str:
    """Obtiene o crea la cabecera del boucher por defecto"""
    cabecera = db.query(BoucherCabecera).first()
    
    if not cabecera:
        # Crear cabecera por defecto
        cabecera = BoucherCabecera(
            ban_aid="BP001",
            ban_nombre="Banco Pichincha S.A.",
            ban_direccion="Av. Amazonas y Naciones Unidas, Quito",
            ban_ruc="1790010937001",
            ban_mensaje="Gracias por confiar en Banco Pichincha. Para consultas: 1800-PICHINCHA"
        )
        db.add(cabecera)
        db.flush()
    
    return cabecera.ban_aid

@router.post("/procesar", response_model=dict)
def procesar_retiro_con_tarjeta(
    request: RetiroCreate,
    db: Session = Depends(get_db)
):
    """Procesa un retiro con tarjeta desde cajero ATM (sin autenticación)"""
    try:
        print(f"Datos recibidos: {request}")
        print(f"cuen_id tipo: {type(request.cuen_id)}, valor: {request.cuen_id}")
        print(f"caj_id tipo: {type(request.caj_id)}, valor: {request.caj_id}")
        print(f"ret_monto tipo: {type(request.ret_monto)}, valor: {request.ret_monto}")
        print(f"tar_numero_tarjeta: {request.tar_numero_tarjeta}")
        
        # Validaciones específicas
        if request.cuen_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cuen_id no puede ser nulo"
            )
            
        if request.caj_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="caj_id no puede ser nulo"
            )
        
        # Validar que es retiro con tarjeta
        if request.tipo_retiro != "CON_TARJETA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este endpoint es solo para retiros con tarjeta"
            )
        
        if not request.tar_numero_tarjeta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Número de tarjeta es requerido"
            )
        
        # Buscar tarjeta y obtener cuenta asociada
        tarjeta = db.query(Tarjeta).filter(
            Tarjeta.tar_numero_tarjeta == request.tar_numero_tarjeta,
            Tarjeta.tar_estado_tarjeta == "ACTIVA"
        ).first()
        
        if not tarjeta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarjeta no encontrada o inactiva"
            )
        
        # Obtener cuenta asociada a la tarjeta
        cuenta = db.query(Cuenta).filter(
            Cuenta.cuen_id == tarjeta.cuen_id
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta asociada no encontrada"
            )
        
        if cuenta.cuen_estado != "ACTIVA":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cuenta no está activa"
            )
        
        # Verificar saldo suficiente (monto + costo boucher si aplica)
        monto_retiro = Decimal(str(request.ret_monto))
        costo_boucher = Decimal('0.36') if request.imprimir_boucher == "SI" else Decimal('0.00')
        monto_total = monto_retiro + costo_boucher
        
        # Convertir saldo a Decimal para comparación consistente
        saldo_actual = Decimal(str(cuenta.cuen_saldo))
        if saldo_actual < monto_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Saldo disponible: ${cuenta.cuen_saldo}"
            )
        
        # Verificar cajero
        cajero = db.query(Cajero).filter(Cajero.caj_id == request.caj_id).first()
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
            tran_id=tran_id,
            cuen_id=cuenta.cuen_id,
            caj_id=request.caj_id
        )
        db.add(nueva_transaccion)
        db.flush()
        
        # 2. Crear registro en RETIRO (tabla hija de TRANSACCION)
        nuevo_retiro = Retiro(
            tran_id=tran_id,
            ret_id=ret_id,
            cuen_id=cuenta.cuen_id,
            caj_id=request.caj_id,
            ret_fecha=obtener_fecha_ecuador(),
            ret_monto=int(request.ret_monto),
            ret_cajero="ONLINE",
            ret_numero_tran=str(tran_id)[-4:].zfill(4),
        )
        db.add(nuevo_retiro)
        db.flush()
        
        # 3. Crear registro en RETIRO_CONTARJETA (tabla hija de RETIRO)
        nuevo_retiro_con_tarjeta = RetiroConTarjeta(
            tran_id=tran_id,
            ret_id=ret_id,
            cuen_id=cuenta.cuen_id,
            caj_id=request.caj_id,
            ret_fecha=obtener_fecha_ecuador(),
            ret_monto=int(request.ret_monto),
            ret_cajero="ONLINE",
            ret_numero_tran=str(tran_id)[-4:].zfill(4),
            rett_imprimir=request.imprimir_boucher,
            rett_montomax=500,  # Siempre 500 como especificaste
        )
        db.add(nuevo_retiro_con_tarjeta)
        db.flush()
        
        # 4. Crear boucher si se solicita imprimir
        boucher_creado = False
        costo_boucher_fijo = Decimal('0.36')  # Siempre 0.36
        
        if request.imprimir_boucher == "SI":
            total_debitado = monto_retiro + costo_boucher_fijo  # monto + 0.36
            
            # Obtener o crear cabecera
            ban_aid = obtener_o_crear_cabecera_boucher(db)
            
            # Crear cuerpo del boucher
            bouc_id = obtener_siguiente_bouc_id(db)
            
            # Debug para verificar valores
            print(f"DEBUG - costo_boucher_fijo: {costo_boucher_fijo}, tipo: {type(costo_boucher_fijo)}")
            print(f"DEBUG - total_debitado: {total_debitado}, tipo: {type(total_debitado)}")
            
            nuevo_boucher = BoucherCuerpo(
                bouc_id=bouc_id,
                rett_imprimir=request.imprimir_boucher,
                rett_montomax=500,
                tran_id=tran_id,
                ret_id=ret_id,
                cuen_id=cuenta.cuen_id,
                caj_id=request.caj_id,
                ret_fecha=obtener_fecha_ecuador(),
                ret_monto=int(request.ret_monto),
                ret_cajero="ONLINE",
                ret_numero_tran=str(tran_id)[-4:].zfill(4),
                ban_aid=ban_aid,
                bouc_costo=costo_boucher_fijo,  # Valor decimal directo (0.36)
                bouc_totaldebitado=total_debitado,  # Valor decimal directo (ej: 10.36)
            )
            print(f"DEBUG - Valores para insertar - BOUC_COSTO: {nuevo_boucher.bouc_costo}, BOUC_TOTALDEBITADO: {nuevo_boucher.bouc_totaldebitado}")
            print(f"DEBUG - Tipos de valores - BOUC_COSTO: {type(nuevo_boucher.bouc_costo)}, BOUC_TOTALDEBITADO: {type(nuevo_boucher.bouc_totaldebitado)}")
            
            db.add(nuevo_boucher)
            print(f"DEBUG - Después de add() - BOUC_COSTO: {nuevo_boucher.bouc_costo}, BOUC_TOTALDEBITADO: {nuevo_boucher.bouc_totaldebitado}")
            
            # Hacer flush para forzar la inserción y ver si hay errores
            try:
                db.flush()
                print(f"DEBUG - Después de flush() - BOUC_COSTO: {nuevo_boucher.bouc_costo}, BOUC_TOTALDEBITADO: {nuevo_boucher.bouc_totaldebitado}")
                
            except Exception as flush_error:
                print(f"ERROR en flush: {flush_error}")
                raise
            boucher_creado = True
        else:
            # Si no hay boucher, el total debitado es solo el monto
            total_debitado = monto_retiro
        
        # Actualizar saldo de la cuenta - siempre descontar el total calculado
        # Convertir saldo actual a Decimal para operaciones consistentes
        saldo_actual = Decimal(str(cuenta.cuen_saldo))
        nuevo_saldo = saldo_actual - total_debitado
        cuenta.cuen_saldo = nuevo_saldo
        
        # Confirmar todos los cambios
        db.commit()
        
        # Debug final: verificar qué se guardó realmente en la base de datos
        if boucher_creado:
            # Refrescar el objeto desde la base de datos
            db.refresh(nuevo_boucher)
            print(f"DEBUG FINAL - Valores guardados en BD - BOUC_COSTO: {nuevo_boucher.bouc_costo}, BOUC_TOTALDEBITADO: {nuevo_boucher.bouc_totaldebitado}")
            print(f"DEBUG FINAL - Tipos después de commit - BOUC_COSTO: {type(nuevo_boucher.bouc_costo)}, BOUC_TOTALDEBITADO: {type(nuevo_boucher.bouc_totaldebitado)}")
            
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
            "nuevo_saldo": float(cuenta.cuen_saldo),
            "numero_transaccion": str(tran_id)[-4:].zfill(4),
            "fecha_transaccion": obtener_fecha_ecuador().isoformat(),
            "boucher_impreso": boucher_creado,
            "costo_boucher": float(costo_boucher_fijo) if boucher_creado else 0.0,
            "total_debitado": float(total_debitado)
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        db.rollback()
        print(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        print(f"Error procesando retiro con tarjeta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar el retiro"
        )
