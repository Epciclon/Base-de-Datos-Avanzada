from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import random
import string

from app.database import get_db
from app.models.models import RetiroSinTarjeta, Cuenta, Condiciones, Transaccion, Retiro, Cajero, Tarjeta, TarjetaDebito, TarjetaCredito
from app.schemas.schemas import CodigoRetiroRequest, CodigoRetiroResponse, ValidarCodigoRequest
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/retiros-sin-tarjeta",
    tags=["retiros-sin-tarjeta"]
)

def generar_codigo_unico(db: Session) -> str:
    """Genera un código único de 6 dígitos"""
    while True:
        codigo = ''.join(random.choices(string.digits, k=6))
        # Verificar que el código no existe ya
        codigo_existente = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.RETS_CODIGO == codigo,
            RetiroSinTarjeta.RETS_ESTADO_CODIGO == 'Pendiente'
        ).first()
        if not codigo_existente:
            return codigo

def obtener_siguiente_id(db: Session, tabla) -> int:
    """Obtiene el siguiente ID disponible para una tabla"""
    max_id = db.query(func.max(tabla.TRAN_ID)).scalar()
    return 1 if max_id is None else max_id + 1

def obtener_siguiente_ret_id(db: Session) -> int:
    """Obtiene el siguiente RET_ID disponible"""
    max_ret_id = db.query(func.max(Retiro.RET_ID)).scalar()
    return 1 if max_ret_id is None else max_ret_id + 1

def obtener_o_crear_cajero_defecto(db: Session) -> int:
    """Obtiene o crea un cajero por defecto para transacciones online"""
    cajero = db.query(Cajero).filter(Cajero.CAJ_ID == 1).first()
    
    if not cajero:
        # Crear cajero por defecto
        nuevo_cajero = Cajero(
            CAJ_ID=1,
            CAJ_UBICACION="Sistema Online",
            CAJ_ESTADO="Activo",
            CAJ_TIPO="ATM",
            CAJ_SUCURSAL="Digital"
        )
        db.add(nuevo_cajero)
        db.commit()
        db.refresh(nuevo_cajero)
        
    return 1

@router.post("/generar-codigo", response_model=CodigoRetiroResponse)
def generar_codigo_retiro(
    request: CodigoRetiroRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Genera un código temporal para retiro sin tarjeta"""
    try:
        # Obtener condiciones vigentes para retiro sin tarjeta
        condicion = db.query(Condiciones).filter(
            Condiciones.COND_DESCRIPCION == 'Retiro sin tarjeta',
            Condiciones.COND_ESTADO == 'Activo'
        ).first()
        
        if not condicion:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servicio de retiro sin tarjeta no disponible temporalmente"
            )
        
        # Validar monto máximo según condiciones
        if request.monto > condicion.COND_MONTO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El monto máximo permitido es ${condicion.COND_MONTO}"
            )
        
        # Verificar que la cuenta pertenece al usuario actual
        cuenta = db.query(Cuenta).filter(
            Cuenta.CUEN_ID == request.CUEN_ID,
            Cuenta.CLI_ID == current_user.CLI_ID
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada o no pertenece al usuario"
            )
        
        # Verificar saldo suficiente
        if cuenta.CUEN_SALDO < request.monto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente"
            )
        
        # Verificar si ya existe un código activo para esta cuenta
        codigo_activo = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.CUEN_ID == request.CUEN_ID,
            RetiroSinTarjeta.RETS_ESTADO_CODIGO == 'ACTIVO',
            RetiroSinTarjeta.RET_FECHA > datetime.now() - timedelta(hours=condicion.COND_HORAS)
        ).first()
        
        if codigo_activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un código activo para esta cuenta. Espere a que expire o úselo. Válido por {condicion.COND_HORAS} horas."
            )
        
        # Generar código único
        codigo = generar_codigo_unico(db)
        
        # Verificar que el cajero existe
        cajero = db.query(Cajero).filter(Cajero.CAJ_ID == request.CAJ_ID).first()
        if not cajero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cajero no encontrado"
            )
        
        # Obtener IDs únicos para las transacciones
        tran_id = obtener_siguiente_id(db, Transaccion)
        ret_id = obtener_siguiente_ret_id(db)
        
        # 1. Crear la transacción principal
        nueva_transaccion = Transaccion(
            TRAN_ID=tran_id,
            CUEN_ID=cuenta.CUEN_ID,
            CAJ_ID=request.CAJ_ID
        )
        db.add(nueva_transaccion)
        db.flush()
        
        # 2. Crear el registro en RETIRO (tabla padre)
        nuevo_retiro = Retiro(
            TRAN_ID=tran_id,
            RET_ID=ret_id,
            CUEN_ID=cuenta.CUEN_ID,
            CAJ_ID=request.CAJ_ID,
            RET_FECHA=datetime.now(),
            RET_MONTO=int(request.monto),
            RET_CAJERO="ONLINE",
            RET_NUMERO_TRAN=str(tran_id)[-4:].zfill(4),
        )
        db.add(nuevo_retiro)
        db.flush()
        
        # 3. Crear registro en RETIRO_SINTARJETA (tabla hija)
        nuevo_retiro_sin_tarjeta = RetiroSinTarjeta(
            TRAN_ID=tran_id,
            RET_ID=ret_id,
            CUEN_ID=cuenta.CUEN_ID,
            CAJ_ID=request.CAJ_ID,
            RET_FECHA=datetime.now(),
            RET_MONTO=int(request.monto),
            RET_CAJERO="ONLINE",
            RET_NUMERO_TRAN=str(tran_id)[-4:].zfill(4),
            COND_ID=condicion.COND_ID,
            RETS_CODIGO=codigo,
            RETS_TELEFONO_ASOCIADO=request.telefono,
            RETS_ESTADO_CODIGO="ACTIVO"
        )
        db.add(nuevo_retiro_sin_tarjeta)
        
        # Confirmar todos los cambios
        db.commit()
        db.refresh(nuevo_retiro_sin_tarjeta)
        
        return CodigoRetiroResponse(
            codigo=codigo,
            fecha_expiracion=datetime.now() + timedelta(hours=condicion.COND_HORAS),
            monto=float(request.monto),
            mensaje=f"Código generado exitosamente. Válido por {condicion.COND_HORAS} horas."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/validar-codigo")
def validar_codigo_retiro(
    request: ValidarCodigoRequest,
    db: Session = Depends(get_db)
):
    """Valida un código de retiro sin tarjeta - Simple validación"""
    try:
        # Buscar el código en la base de datos
        codigo_registro = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.RETS_CODIGO == request.codigo,
            RetiroSinTarjeta.RETS_TELEFONO_ASOCIADO == request.telefono
        ).first()
        
        if not codigo_registro:
            return {
                "valido": False,
                "mensaje": "Código no encontrado o teléfono incorrecto",
                "codigo_existe": False
            }
        
        # Obtener las condiciones para verificar tiempo límite
        condicion = db.query(Condiciones).filter(
            Condiciones.COND_ID == codigo_registro.COND_ID
        ).first()
        
        if not condicion:
            return {
                "valido": False,
                "mensaje": "Condiciones del retiro no encontradas",
                "codigo_existe": True
            }
        
        # Verificar que no haya expirado usando RET_FECHA
        tiempo_limite = codigo_registro.RET_FECHA + timedelta(hours=condicion.COND_HORAS)
        
        if datetime.now() > tiempo_limite:
            # Marcar como NO USADO si pasó el tiempo límite
            codigo_registro.RETS_ESTADO_CODIGO = 'NO USADO'
            db.commit()
            
            return {
                "valido": False,
                "mensaje": f"Código expirado. El tiempo límite era de {condicion.COND_HORAS} horas.",
                "codigo_existe": True
            }
        
        # Verificar que el código esté activo
        if codigo_registro.RETS_ESTADO_CODIGO != 'ACTIVO':
            return {
                "valido": False,
                "mensaje": f"Código ya usado o inválido. Estado: {codigo_registro.RETS_ESTADO_CODIGO}",
                "codigo_existe": True
            }
        
        # Si llega aquí, el código es válido
        return {
            "valido": True,
            "codigo_id": f"{codigo_registro.TRAN_ID}_{codigo_registro.RET_ID}",
            "monto": float(codigo_registro.RET_MONTO),
            "fecha_expiracion": tiempo_limite,
            "intentos_maximos": condicion.COND_INTENTOS,
            "codigo_existe": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/marcar-codigo-no-usado")
def marcar_codigo_no_usado(
    request: ValidarCodigoRequest,
    db: Session = Depends(get_db)
):
    """Marca un código como NO USADO después de 3 intentos fallidos en el cajero"""
    try:
        # Buscar el código en la base de datos
        codigo_registro = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.RETS_CODIGO == request.codigo,
            RetiroSinTarjeta.RETS_TELEFONO_ASOCIADO == request.telefono
        ).first()
        
        if not codigo_registro:
            return {
                "mensaje": "Código no encontrado en la base de datos. 3 intentos fallidos completados.",
                "codigo": request.codigo,
                "codigo_encontrado": False
            }
        
        # Marcar como NO USADO
        codigo_registro.RETS_ESTADO_CODIGO = 'NO USADO'
        db.commit()
        
        return {
            "mensaje": "Código marcado como NO USADO por exceder 3 intentos fallidos",
            "codigo": request.codigo,
            "codigo_encontrado": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/procesar-retiro")
def procesar_retiro_sin_tarjeta(
    codigo_id: str,
    db: Session = Depends(get_db)
):
    """Procesa un retiro sin tarjeta usando el código validado"""
    try:
        # Extraer TRAN_ID y RET_ID del codigo_id
        tran_id, ret_id = map(int, codigo_id.split('_'))
        
        # Buscar el registro del retiro
        codigo_registro = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.TRAN_ID == tran_id,
            RetiroSinTarjeta.RET_ID == ret_id,
            RetiroSinTarjeta.RETS_ESTADO_CODIGO == 'ACTIVO'
        ).first()
        
        if not codigo_registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código no encontrado o ya procesado"
            )
        
        # Verificar que no haya expirado usando RET_FECHA
        condicion = db.query(Condiciones).filter(
            Condiciones.COND_ID == codigo_registro.COND_ID
        ).first()
        
        if not condicion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Condiciones del retiro no encontradas"
            )
        
        tiempo_limite = codigo_registro.RET_FECHA + timedelta(hours=condicion.COND_HORAS)
        
        if datetime.now() > tiempo_limite:
            codigo_registro.RETS_ESTADO_CODIGO = 'NO USADO'
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Código expirado. El tiempo límite era de {condicion.COND_HORAS} horas."
            )
        
        # Obtener información de la cuenta
        cuenta = db.query(Cuenta).filter(
            Cuenta.CUEN_ID == codigo_registro.CUEN_ID
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada"
            )
        
        # Verificar saldo suficiente SOLO si es tarjeta DEBITO o si no tiene tarjeta (retiro directo de cuenta)
        # Verificar si la cuenta tiene tarjetas asociadas
        tarjeta_debito = db.query(TarjetaDebito).filter(
            TarjetaDebito.CUEN_ID == codigo_registro.CUEN_ID,
            TarjetaDebito.TAR_ESTADO_TARJETA == 'ACTIVA'
        ).first()
        
        tarjeta_credito = db.query(TarjetaCredito).filter(
            TarjetaCredito.CUEN_ID == codigo_registro.CUEN_ID,
            TarjetaCredito.TAR_ESTADO_TARJETA == 'ACTIVA'
        ).first()
        
        # Determinar si debe descontar del saldo de la cuenta
        debe_descontar_saldo = True
        tipo_tarjeta = "DIRECTA"  # Por defecto, retiro directo de cuenta
        
        if tarjeta_credito and not tarjeta_debito:
            # Solo tiene tarjeta de crédito - NO descuentar de la cuenta
            debe_descontar_saldo = False
            tipo_tarjeta = "CREDITO"
        elif tarjeta_debito:
            # Tiene tarjeta de débito - SÍ descuentar de la cuenta
            debe_descontar_saldo = True
            tipo_tarjeta = "DEBITO"
        
        # Verificar saldo solo si va a descontar
        if debe_descontar_saldo and cuenta.CUEN_SALDO < codigo_registro.RET_MONTO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente en la cuenta"
            )

        # Actualizar el estado del código a USADO
        codigo_registro.RETS_ESTADO_CODIGO = 'USADO'
        
        # Descontar el saldo SOLO si corresponde (DEBITO o retiro directo)
        nuevo_saldo = cuenta.CUEN_SALDO
        if debe_descontar_saldo:
            cuenta.CUEN_SALDO -= codigo_registro.RET_MONTO
            nuevo_saldo = cuenta.CUEN_SALDO        # Confirmar todos los cambios
        db.commit()
        
        return {
            "mensaje": "Retiro procesado exitosamente",
            "monto": float(codigo_registro.RET_MONTO),
            "tipo_tarjeta": tipo_tarjeta,
            "saldo_descontado": debe_descontar_saldo,
            "nuevo_saldo": float(nuevo_saldo),
            "numero_transaccion": str(tran_id).zfill(4),
            "fecha_transaccion": codigo_registro.RET_FECHA.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error procesando retiro: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar el retiro"
        )

@router.get("/mis-codigos")
def obtener_mis_codigos(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtiene los códigos de retiro del usuario actual"""
    try:
        # Obtener todas las cuentas del usuario
        cuentas_usuario = db.query(Cuenta).filter(
            Cuenta.CLI_ID == current_user.CLI_ID
        ).all()
        
        cuentas_ids = [cuenta.CUEN_ID for cuenta in cuentas_usuario]
        
        # Obtener códigos de las últimas 24 horas
        fecha_limite = datetime.now() - timedelta(hours=24)
        
        codigos = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.CUEN_ID.in_(cuentas_ids),
            RetiroSinTarjeta.RET_FECHA >= fecha_limite
        ).order_by(RetiroSinTarjeta.RET_FECHA.desc()).all()
        
        resultado = []
        for codigo in codigos:
            # Obtener condiciones para calcular fecha de expiración
            condicion = db.query(Condiciones).filter(
                Condiciones.COND_ID == codigo.COND_ID
            ).first()
            
            horas_limite = condicion.COND_HORAS if condicion else 4  # Por defecto 4 horas
            
            resultado.append({
                "codigo": codigo.RETS_CODIGO,
                "monto": float(codigo.RET_MONTO),
                "fecha_creacion": codigo.RET_FECHA.isoformat(),
                "estado": codigo.RETS_ESTADO_CODIGO,
                "telefono": codigo.RETS_TELEFONO_ASOCIADO,
                "fecha_expiracion": (codigo.RET_FECHA + timedelta(hours=horas_limite)).isoformat(),
                "horas_limite": horas_limite
            })
        
        return resultado
        
    except Exception as e:
        print(f"Error obteniendo códigos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/condiciones")
def obtener_condiciones_retiro_sin_tarjeta(
    db: Session = Depends(get_db)
):
    """Obtiene las condiciones vigentes para retiro sin tarjeta"""
    try:
        condicion = db.query(Condiciones).filter(
            Condiciones.COND_DESCRIPCION == 'Retiro sin tarjeta',
            Condiciones.COND_ESTADO == 'Activo'
        ).first()
        
        if not condicion:
            return {
                "disponible": False,
                "mensaje": "Servicio de retiro sin tarjeta no disponible temporalmente"
            }
        
        return {
            "disponible": True,
            "COND_ID": condicion.COND_ID,
            "descripcion": condicion.COND_DESCRIPCION,
            "monto_maximo": condicion.COND_MONTO,
            "horas_limite": condicion.COND_HORAS,
            "intentos_permitidos": condicion.COND_INTENTOS,
            "estado": condicion.COND_ESTADO
        }
        
    except Exception as e:
        print(f"Error obteniendo condiciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener condiciones"
        )
