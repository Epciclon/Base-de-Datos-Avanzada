from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import random
import string
import pytz

from app.database import get_db
from app.models.models import RetiroSinTarjeta, Cuenta, Condiciones, Transaccion, Retiro, Cajero, Tarjeta, TarjetaDebito, TarjetaCredito
from app.schemas.schemas import CodigoRetiroRequest, CodigoRetiroResponse, ValidarCodigoRequest
from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/retiros-sin-tarjeta",
    tags=["retiros-sin-tarjeta"]
)

def obtener_fecha_ecuador():
    """Obtiene la fecha y hora actual en zona horaria de Ecuador (UTC-5)"""
    ecuador_tz = pytz.timezone('America/Guayaquil')
    return datetime.now(ecuador_tz).replace(tzinfo=None)

def generar_codigo_unico(db: Session) -> str:
    """Genera un código único de 6 dígitos"""
    while True:
        codigo = ''.join(random.choices(string.digits, k=6))
        # Verificar que el código no existe ya
        codigo_existente = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.rets_codigo == codigo,
            RetiroSinTarjeta.rets_estado_codigo == 'Pendiente'
        ).first()
        if not codigo_existente:
            return codigo

def obtener_siguiente_id(db: Session, tabla) -> int:
    """Obtiene el siguiente ID disponible para una tabla"""
    max_id = db.query(func.max(tabla.tran_id)).scalar()
    return 1 if max_id is None else max_id + 1

def obtener_siguiente_ret_id(db: Session) -> int:
    """Obtiene el siguiente RET_ID disponible"""
    max_ret_id = db.query(func.max(Retiro.ret_id)).scalar()
    return 1 if max_ret_id is None else max_ret_id + 1

def obtener_o_crear_cajero_defecto(db: Session) -> int:
    """Obtiene o crea un cajero por defecto para transacciones online"""
    cajero = db.query(Cajero).filter(Cajero.caj_id == 1).first()
    
    if not cajero:
        # Crear cajero por defecto
        nuevo_cajero = Cajero(
            caj_id=1,
            caj_ubicacion="Sistema Online",
            caj_estado="Activo",
            caj_tipo="ATM",
            caj_sucursal="Digital"
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
            Condiciones.cond_descripcion.ilike('%retiro sin tarjeta%'),
            Condiciones.cond_estado.ilike('%activo%')
        ).first()
        
        # Si no hay condiciones específicas, crear condiciones por defecto
        if not condicion:
            # Crear condiciones por defecto con los nuevos valores
            condicion_defecto = Condiciones(
                cond_descripcion='Retiro sin Tarjeta',
                cond_horas=4,  # Código válido por 4 horas
                cond_intentos=5,  # Máximo 5 códigos por día
                cond_monto=300,  # Monto máximo $300
                cond_estado='ACTIVO'
            )
            db.add(condicion_defecto)
            db.flush()
            condicion = condicion_defecto
            print(f"Condiciones por defecto creadas: ID {condicion.cond_id} - Monto: ${condicion.cond_monto}, Intentos diarios: {condicion.cond_intentos}, Válido por: {condicion.cond_horas} horas")
        
        print(f"Condiciones encontradas: {condicion.cond_descripcion}, Monto: {condicion.cond_monto}")
        
        # Validar monto máximo según condiciones
        if request.monto > condicion.cond_monto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El monto máximo permitido es ${condicion.cond_monto}"
            )
        
        # Verificar que la cuenta pertenece al usuario actual
        cuenta = db.query(Cuenta).filter(
            Cuenta.cuen_id == request.cuen_id,
            Cuenta.cli_id == current_user.cli_id
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada o no pertenece al usuario"
            )
        
        # Verificar saldo suficiente
        if cuenta.cuen_saldo < request.monto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente"
            )
        
        # Verificar si ya existe un código activo para esta cuenta
        fecha_limite = obtener_fecha_ecuador() - timedelta(hours=condicion.cond_horas)
        codigo_activo = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.cuen_id == request.cuen_id,
            RetiroSinTarjeta.rets_estado_codigo == 'ACTIVO',
            RetiroSinTarjeta.ret_fecha >= fecha_limite
        ).first()
        
        if codigo_activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un código activo para esta cuenta. Espere a que expire o úselo. Válido por {condicion.cond_horas} horas."
            )
        
        # Verificar límite de intentos diarios (códigos generados por día, independiente del estado)
        fecha_hoy = obtener_fecha_ecuador().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_manana = fecha_hoy + timedelta(days=1)
        
        intentos_hoy = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.cuen_id == request.cuen_id,
            RetiroSinTarjeta.ret_fecha >= fecha_hoy,
            RetiroSinTarjeta.ret_fecha < fecha_manana
        ).count()
        
        if intentos_hoy >= condicion.cond_intentos:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Ha alcanzado el límite diario de {condicion.cond_intentos} códigos de retiro. Intente mañana."
            )
        
        # Generar código único
        codigo = generar_codigo_unico(db)
        
        # Verificar que el cajero existe
        cajero = db.query(Cajero).filter(Cajero.caj_id == request.caj_id).first()
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
            tran_id=tran_id,
            cuen_id=cuenta.cuen_id,
            caj_id=request.caj_id
        )
        db.add(nueva_transaccion)
        db.flush()
        
        # 2. Crear el registro en RETIRO (tabla padre)
        nuevo_retiro = Retiro(
            tran_id=tran_id,
            ret_id=ret_id,
            cuen_id=cuenta.cuen_id,
            caj_id=request.caj_id,
            ret_fecha=obtener_fecha_ecuador(),
            ret_monto=int(request.monto),
            ret_cajero="ONLINE",
            ret_numero_tran=str(tran_id)[-4:].zfill(4),
        )
        db.add(nuevo_retiro)
        db.flush()
        
        # 3. Crear registro en RETIRO_SINTARJETA (tabla hija)
        nuevo_retiro_sin_tarjeta = RetiroSinTarjeta(
            tran_id=tran_id,
            ret_id=ret_id,
            cuen_id=cuenta.cuen_id,
            caj_id=request.caj_id,
            ret_fecha=obtener_fecha_ecuador(),
            ret_monto=int(request.monto),
            ret_cajero="ONLINE",
            ret_numero_tran=str(tran_id)[-4:].zfill(4),
            cond_id=condicion.cond_id,
            rets_codigo=codigo,
            rets_telefono_asociado=request.telefono,
            rets_estado_codigo="ACTIVO"
        )
        db.add(nuevo_retiro_sin_tarjeta)
        
        # Confirmar todos los cambios
        db.commit()
        db.refresh(nuevo_retiro_sin_tarjeta)
        
        return CodigoRetiroResponse(
            codigo=codigo,
            fecha_expiracion=obtener_fecha_ecuador() + timedelta(hours=condicion.cond_horas),
            monto=float(request.monto),
            mensaje=f"Código generado exitosamente. Válido por {condicion.cond_horas} horas."
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
            RetiroSinTarjeta.rets_codigo == request.codigo,
            RetiroSinTarjeta.rets_telefono_asociado == request.telefono
        ).first()
        
        if not codigo_registro:
            return {
                "valido": False,
                "mensaje": "Código no encontrado o teléfono incorrecto",
                "codigo_existe": False
            }
        
        # Obtener las condiciones para verificar tiempo límite
        condicion = db.query(Condiciones).filter(
            Condiciones.cond_id == codigo_registro.cond_id
        ).first()
        
        if not condicion:
            return {
                "valido": False,
                "mensaje": "Condiciones del retiro no encontradas",
                "codigo_existe": True
            }
        
        # Verificar que no haya expirado usando RET_FECHA
        tiempo_limite = codigo_registro.ret_fecha + timedelta(hours=condicion.cond_horas)
        
        if obtener_fecha_ecuador() > tiempo_limite:
            # Marcar como NO USADO si pasó el tiempo límite
            codigo_registro.rets_estado_codigo = 'NO USADO'
            db.commit()
            
            return {
                "valido": False,
                "mensaje": f"Código expirado. El tiempo límite era de {condicion.cond_horas} horas.",
                "codigo_existe": True
            }
        
        # Verificar que el código esté activo
        if codigo_registro.rets_estado_codigo != 'ACTIVO':
            return {
                "valido": False,
                "mensaje": f"Código ya usado o inválido. Estado: {codigo_registro.rets_estado_codigo}",
                "codigo_existe": True
            }
        
        # Si llega aquí, el código es válido
        return {
            "valido": True,
            "codigo_id": f"{codigo_registro.tran_id}_{codigo_registro.ret_id}",
            "monto": float(codigo_registro.ret_monto),
            "fecha_expiracion": tiempo_limite,
            "intentos_maximos": condicion.cond_intentos,
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
            RetiroSinTarjeta.rets_codigo == request.codigo,
            RetiroSinTarjeta.rets_telefono_asociado == request.telefono
        ).first()
        
        if not codigo_registro:
            return {
                "mensaje": "Código no encontrado en la base de datos. 3 intentos fallidos completados.",
                "codigo": request.codigo,
                "codigo_encontrado": False
            }
        
        # Marcar como NO USADO
        codigo_registro.rets_estado_codigo = 'NO USADO'
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
            RetiroSinTarjeta.tran_id == tran_id,
            RetiroSinTarjeta.ret_id == ret_id,
            RetiroSinTarjeta.rets_estado_codigo == 'ACTIVO'
        ).first()
        
        if not codigo_registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Código no encontrado o ya procesado"
            )
        
        # Verificar que no haya expirado usando RET_FECHA
        condicion = db.query(Condiciones).filter(
            Condiciones.cond_id == codigo_registro.cond_id
        ).first()
        
        if not condicion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Condiciones del retiro no encontradas"
            )
        
        tiempo_limite = codigo_registro.ret_fecha + timedelta(hours=condicion.cond_horas)
        
        if obtener_fecha_ecuador() > tiempo_limite:
            codigo_registro.rets_estado_codigo = 'NO USADO'
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Código expirado. El tiempo límite era de {condicion.cond_horas} horas."
            )
        
        # Obtener información de la cuenta
        cuenta = db.query(Cuenta).filter(
            Cuenta.cuen_id == codigo_registro.cuen_id
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada"
            )
        
        # Verificar saldo suficiente SOLO si es tarjeta DEBITO o si no tiene tarjeta (retiro directo de cuenta)
        # Verificar si la cuenta tiene tarjetas asociadas
        tarjeta_debito = db.query(TarjetaDebito).filter(
            TarjetaDebito.cuen_id == codigo_registro.cuen_id,
            TarjetaDebito.tar_estado_tarjeta == 'ACTIVA'
        ).first()
        
        tarjeta_credito = db.query(TarjetaCredito).filter(
            TarjetaCredito.cuen_id == codigo_registro.cuen_id,
            TarjetaCredito.tar_estado_tarjeta == 'ACTIVA'
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
        if debe_descontar_saldo and cuenta.cuen_saldo < codigo_registro.ret_monto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Saldo insuficiente en la cuenta"
            )

        # Actualizar el estado del código a USADO
        codigo_registro.rets_estado_codigo = 'USADO'
        
        # Descontar el saldo SOLO si corresponde (DEBITO o retiro directo)
        nuevo_saldo = cuenta.cuen_saldo
        if debe_descontar_saldo:
            cuenta.cuen_saldo -= codigo_registro.ret_monto
            nuevo_saldo = cuenta.cuen_saldo        # Confirmar todos los cambios
        db.commit()
        
        return {
            "mensaje": "Retiro procesado exitosamente",
            "monto": float(codigo_registro.ret_monto),
            "tipo_tarjeta": tipo_tarjeta,
            "saldo_descontado": debe_descontar_saldo,
            "nuevo_saldo": float(nuevo_saldo),
            "numero_transaccion": str(tran_id).zfill(4),
            "fecha_transaccion": codigo_registro.ret_fecha.isoformat()
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
            Cuenta.cli_id == current_user.cli_id
        ).all()
        
        cuentas_ids = [cuenta.cuen_id for cuenta in cuentas_usuario]
        
        # Obtener códigos de las últimas 24 horas
        fecha_limite = obtener_fecha_ecuador() - timedelta(hours=24)
        
        codigos = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.cuen_id.in_(cuentas_ids),
            RetiroSinTarjeta.ret_fecha >= fecha_limite
        ).order_by(RetiroSinTarjeta.ret_fecha.desc()).all()
        
        resultado = []
        for codigo in codigos:
            # Obtener condiciones para calcular fecha de expiración
            condicion = db.query(Condiciones).filter(
                Condiciones.cond_id == codigo.cond_id
            ).first()
            
            horas_limite = condicion.cond_horas if condicion else 4  # Por defecto 4 horas
            
            resultado.append({
                "codigo": codigo.rets_codigo,
                "monto": float(codigo.ret_monto),
                "fecha_creacion": codigo.ret_fecha.isoformat(),
                "estado": codigo.rets_estado_codigo,
                "telefono": codigo.rets_telefono_asociado,
                "fecha_expiracion": (codigo.ret_fecha + timedelta(hours=horas_limite)).isoformat(),
                "horas_limite": horas_limite
            })
        
        return resultado
        
    except Exception as e:
        print(f"Error obteniendo códigos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/limites-diarios/{cuen_id}")
def obtener_limites_diarios(
    cuen_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtiene los límites diarios actuales para retiro sin tarjeta de una cuenta específica"""
    try:
        # Verificar que la cuenta pertenece al usuario actual
        cuenta = db.query(Cuenta).filter(
            Cuenta.cuen_id == cuen_id,
            Cuenta.cli_id == current_user.cli_id
        ).first()
        
        if not cuenta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada o no pertenece al usuario"
            )
        
        # Obtener condiciones vigentes
        condicion = db.query(Condiciones).filter(
            Condiciones.cond_descripcion == 'Retiro sin Tarjeta',
            Condiciones.cond_estado == 'ACTIVO'
        ).first()
        
        if not condicion:
            return {
                "limite_diario_monto": 300,
                "limite_diario_retiros": 5,
                "monto_usado_hoy": 0,
                "retiros_realizados_hoy": 0,
                "monto_disponible": 300,
                "retiros_disponibles": 5,
                "puede_retirar": False,
                "mensaje": "Servicio no disponible temporalmente"
            }
        
        # Calcular el rango del día actual en Ecuador
        fecha_hoy = obtener_fecha_ecuador().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_manana = fecha_hoy + timedelta(days=1)
        
        # Obtener todos los códigos generados hoy (para límite de intentos)
        codigos_generados_hoy = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.cuen_id == cuen_id,
            RetiroSinTarjeta.ret_fecha >= fecha_hoy,
            RetiroSinTarjeta.ret_fecha < fecha_manana
        ).count()
        
        # Obtener retiros del día actual que fueron USADOS (completados exitosamente)
        retiros_hoy = db.query(RetiroSinTarjeta).filter(
            RetiroSinTarjeta.cuen_id == cuen_id,
            RetiroSinTarjeta.ret_fecha >= fecha_hoy,
            RetiroSinTarjeta.ret_fecha < fecha_manana,
            RetiroSinTarjeta.rets_estado_codigo == 'USADO'
        ).all()
        
        # Calcular totales del día (solo los retiros completados)
        monto_usado_hoy = sum(float(retiro.ret_monto) for retiro in retiros_hoy)
        retiros_realizados_hoy = len(retiros_hoy)
        
        # Calcular disponible
        limite_monto = float(condicion.cond_monto)
        limite_retiros = condicion.cond_intentos
        
        monto_disponible = limite_monto - monto_usado_hoy
        retiros_disponibles = limite_retiros - codigos_generados_hoy  # Usar códigos generados para límite
        
        # Determinar si puede realizar más retiros
        puede_retirar = (monto_disponible > 0 and retiros_disponibles > 0)
        
        # Generar mensaje apropiado
        if not puede_retirar:
            if monto_disponible <= 0:
                mensaje = "Límite diario de monto alcanzado"
            elif retiros_disponibles <= 0:
                mensaje = "Límite diario de códigos alcanzado"
            else:
                mensaje = "Límites diarios alcanzados"
        else:
            mensaje = "Límites disponibles"
        
        return {
            "limite_diario_monto": limite_monto,
            "limite_diario_retiros": limite_retiros,
            "monto_usado_hoy": monto_usado_hoy,
            "retiros_realizados_hoy": retiros_realizados_hoy,
            "codigos_generados_hoy": codigos_generados_hoy,
            "monto_disponible": max(0, monto_disponible),
            "retiros_disponibles": max(0, retiros_disponibles),
            "puede_retirar": puede_retirar,
            "mensaje": mensaje
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error obteniendo límites diarios: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener límites diarios"
        )

@router.get("/condiciones")
def obtener_condiciones_retiro_sin_tarjeta(
    db: Session = Depends(get_db)
):
    """Obtiene las condiciones vigentes para retiro sin tarjeta"""
    try:
        condicion = db.query(Condiciones).filter(
            Condiciones.cond_descripcion == 'Retiro sin Tarjeta',
            Condiciones.cond_estado == 'ACTIVO'
        ).first()
        
        if not condicion:
            return {
                "disponible": False,
                "mensaje": "Servicio de retiro sin tarjeta no disponible temporalmente"
            }
        
        return {
            "disponible": True,
            "cond_id": condicion.cond_id,
            "descripcion": condicion.cond_descripcion,
            "monto_minimo": 10,
            "monto_maximo": condicion.cond_monto,
            "multiplo_requerido": 10,
            "horas_validez": condicion.cond_horas,
            "intentos_diarios": condicion.cond_intentos,
            "uso_por_codigo": 1,
            "estado": condicion.cond_estado
        }
        
    except Exception as e:
        print(f"Error obteniendo condiciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al obtener condiciones"
        )
