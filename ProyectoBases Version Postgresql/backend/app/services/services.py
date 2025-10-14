from sqlalchemy.orm import Session
from app.models.models import (
    Persona, PersonaNatural, PersonaJuridica, Cliente, Cuenta, CuentaAhorro, 
    CuentaCorriente, Tarjeta, TarjetaDebito, TarjetaCredito, Cajero, Transaccion, Retiro,
    RetiroConTarjeta, RetiroSinTarjeta
)
from app.schemas.schemas import (
    ClienteCreate, CuentaCreate, CuentaAhorroCreate, CuentaCorrienteCreate,
    TarjetaCreate, RetiroCreate
)
from decimal import Decimal
from app.utils.id_generator import get_next_id
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class ClienteService:
    @staticmethod
    def crear_cliente(db: Session, cliente_data: ClienteCreate) -> Cliente:
        # Validaciones para evitar duplicados
        
        # 1. Verificar si ya existe una persona con el mismo correo
        persona_existente = db.query(Persona).filter(Persona.per_correo == cliente_data.per_correo).first()
        if persona_existente:
            raise ValueError(f"Ya existe una persona registrada con el correo electrónico: {cliente_data.per_correo}")
        
        # 2. Si es persona natural, verificar cédula
        if cliente_data.identificacion:
            persona_natural_existente = db.query(PersonaNatural).filter(
                PersonaNatural.pn_identificacion == cliente_data.identificacion
            ).first()
            if persona_natural_existente:
                raise ValueError(f"Ya existe una persona registrada con la cédula: {cliente_data.identificacion}")
        
        # 3. Si es persona jurídica, verificar RUC
        if cliente_data.ruc:
            persona_juridica_existente = db.query(PersonaJuridica).filter(
                PersonaJuridica.pj_ruc == cliente_data.ruc
            ).first()
            if persona_juridica_existente:
                raise ValueError(f"Ya existe una empresa registrada con el RUC: {cliente_data.ruc}")
        
        # Generar nuevos IDs usando la utilidad
        new_per_id = get_next_id(db, Persona, 'per_id')
        new_cli_id = get_next_id(db, Cliente, 'cli_id')
        
        # Determinar el tipo de persona
        per_tipo = "NATURAL" if cliente_data.identificacion else "JURIDICA"
        
        # Crear persona
        persona = Persona(
            per_id=new_per_id,
            per_nombres=cliente_data.per_nombres,
            per_apellidos=cliente_data.per_apellidos,
            per_fecha_nacimiento=cliente_data.per_fecha_nacimiento,
            per_genero=cliente_data.per_genero,
            per_telefono=cliente_data.per_telefono,
            per_correo=cliente_data.per_correo,
            per_direccion=cliente_data.per_direccion,
            per_tipo=per_tipo
        )
        db.add(persona)
        db.flush()
        
        # Si es persona natural, crear registro en PersonaNatural
        if cliente_data.identificacion:
            persona_natural = PersonaNatural(
                per_id=new_per_id,
                per_nombres=cliente_data.per_nombres,
                per_apellidos=cliente_data.per_apellidos,
                per_fecha_nacimiento=cliente_data.per_fecha_nacimiento,
                per_genero=cliente_data.per_genero,
                per_telefono=cliente_data.per_telefono,
                per_correo=cliente_data.per_correo,
                per_direccion=cliente_data.per_direccion,
                per_tipo="NATURAL",
                pn_identificacion=cliente_data.identificacion,
                pn_estado_civil=cliente_data.estado_civil or "SOLTERO",
                pn_profesion=cliente_data.profesion or "NO ESPECIFICADO"
            )
            db.add(persona_natural)
        
        # Si es persona jurídica, crear registro en PersonaJuridica
        elif cliente_data.ruc:
            persona_juridica = PersonaJuridica(
                per_id=new_per_id,
                per_nombres=cliente_data.per_nombres,
                per_apellidos=cliente_data.per_apellidos,
                per_fecha_nacimiento=cliente_data.per_fecha_nacimiento,
                per_genero=cliente_data.per_genero,
                per_telefono=cliente_data.per_telefono,
                per_correo=cliente_data.per_correo,
                per_direccion=cliente_data.per_direccion,
                per_tipo="JURIDICA",
                pj_ruc=cliente_data.ruc,
                pj_representante=cliente_data.representante_legal or "NO ESPECIFICADO",
                pj_tipo_entidad=cliente_data.tipo_entidad or "OTRA",
                pj_fecha_constitucion=cliente_data.fecha_constitucion or datetime.now(),
                pj_actividad=cliente_data.actividad_economica or "NO ESPECIFICADO"
            )
            db.add(persona_juridica)
        
        # Crear cliente
        cliente = Cliente(
            per_id=new_per_id,
            cli_id=new_cli_id,
            per_nombres=cliente_data.per_nombres,
            per_apellidos=cliente_data.per_apellidos,
            per_fecha_nacimiento=cliente_data.per_fecha_nacimiento,
            per_genero=cliente_data.per_genero,
            per_telefono=cliente_data.per_telefono,
            per_correo=cliente_data.per_correo,
            per_direccion=cliente_data.per_direccion,
            per_tipo=per_tipo,
            cli_fecha_ingresp=datetime.now(),
            cli_estado=cliente_data.cli_estado
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        
        return cliente
    
    @staticmethod
    def obtener_cliente_por_id(db: Session, per_id: int, cli_id: int) -> Cliente:
        return db.query(Cliente).filter(
            Cliente.per_id == per_id, 
            Cliente.cli_id == cli_id
        ).first()
    
    @staticmethod
    def obtener_cliente_por_identificacion(db: Session, identificacion: str = None, ruc: str = None, correo: str = None) -> Cliente:
        """
        Buscar cliente existente por identificación (cédula/RUC) o correo
        """
        if identificacion:
            # Buscar por cédula en PersonaNatural
            persona_natural = db.query(PersonaNatural).filter(
                PersonaNatural.pn_identificacion == identificacion
            ).first()
            if persona_natural:
                return db.query(Cliente).filter(Cliente.per_id == persona_natural.per_id).first()
        
        if ruc:
            # TODO: Buscar por RUC en PersonaJuridica cuando se implemente
            pass
            
        if correo:
            # Buscar por correo
            persona = db.query(Persona).filter(Persona.per_correo == correo).first()
            if persona:
                return db.query(Cliente).filter(Cliente.per_id == persona.per_id).first()
        
        return None
    
    @staticmethod
    def listar_clientes(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Cliente).offset(skip).limit(limit).all()

class CuentaService:
    @staticmethod
    def generar_numero_cuenta() -> str:
        """Genera un número de cuenta único de 10 dígitos"""
        return ''.join(random.choices('0123456789', k=10))
    
    @staticmethod
    def crear_cuenta(db: Session, cuenta_data: CuentaCreate, per_id: int, cli_id: int) -> Cuenta:
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(
            Cliente.per_id == per_id, 
            Cliente.cli_id == cli_id
        ).first()
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Verificar si el cliente ya tiene una cuenta del mismo tipo
        cuenta_existente = db.query(Cuenta).filter(
            Cuenta.per_id == per_id,
            Cuenta.cli_id == cli_id,
            Cuenta.cuen_tipo == cuenta_data.cuen_tipo
        ).first()
        
        if cuenta_existente:
            raise ValueError(f"El cliente ya tiene una cuenta de tipo {cuenta_data.cuen_tipo}. Un cliente solo puede tener una cuenta de cada tipo.")
        
        # Verificar unicidad del usuario de cuenta
        usuario_existente = db.query(Cuenta).filter(Cuenta.cuen_usuario == cuenta_data.cuen_usuario).first()
        if usuario_existente:
            raise ValueError(f"El nombre de usuario '{cuenta_data.cuen_usuario}' ya está en uso. Por favor elige otro.")
        
        # Generar número de cuenta único
        numero_cuenta = CuentaService.generar_numero_cuenta()
        while db.query(Cuenta).filter(Cuenta.cuen_numero_cuenta == numero_cuenta).first():
            numero_cuenta = CuentaService.generar_numero_cuenta()
        
        # Generar nuevo CUEN_ID
        new_cuen_id = get_next_id(db, Cuenta, 'cuen_id')
        
        # Crear cuenta principal
        cuenta = Cuenta(
            cuen_id=new_cuen_id,
            per_id=per_id,
            cli_id=cli_id,
            cuen_usuario=cuenta_data.cuen_usuario,
            cuen_password=pwd_context.hash(cuenta_data.cuen_password),
            cuen_tipo=cuenta_data.cuen_tipo,
            cuen_numero_cuenta=numero_cuenta,
            cuen_saldo=cuenta_data.cuen_saldo,
            cuen_estado=cuenta_data.cuen_estado
        )
        db.add(cuenta)
        db.flush()
        
        # Crear cuenta específica según el tipo
        if cuenta_data.cuen_tipo == "AHORRO":
            if isinstance(cuenta_data, CuentaAhorroCreate):
                cuenta_ahorro = CuentaAhorro(
                    cuen_id=new_cuen_id,
                    per_id=per_id,
                    cli_id=cli_id,
                    cuen_usuario=cuenta_data.cuen_usuario,
                    cuen_password=pwd_context.hash(cuenta_data.cuen_password),
                    cuen_tipo=cuenta_data.cuen_tipo,
                    cuen_numero_cuenta=numero_cuenta,
                    cuen_saldo=cuenta_data.cuen_saldo,
                    cuen_estado=cuenta_data.cuen_estado,
                    ca_interes=cuenta_data.ca_interes,
                    ca_limite_retiros=cuenta_data.ca_limite_retiros,
                    ca_min_saldo_remunerado=cuenta_data.ca_min_saldo_remunerado
                )
                db.add(cuenta_ahorro)
        elif cuenta_data.cuen_tipo == "CORRIENTE":
            if isinstance(cuenta_data, CuentaCorrienteCreate):
                cuenta_corriente = CuentaCorriente(
                    cuen_id=new_cuen_id,
                    per_id=per_id,
                    cli_id=cli_id,
                    cuen_usuario=cuenta_data.cuen_usuario,
                    cuen_password=pwd_context.hash(cuenta_data.cuen_password),
                    cuen_tipo=cuenta_data.cuen_tipo,
                    cuen_numero_cuenta=numero_cuenta,
                    cuen_saldo=cuenta_data.cuen_saldo,
                    cuen_estado=cuenta_data.cuen_estado,
                    cc_limite_descubierto=cuenta_data.cc_limite_descubierto,
                    cc_comision_mantenimiento=cuenta_data.cc_comision_mantenimiento,
                    cc_num_cheques=cuenta_data.cc_num_cheques
                )
                db.add(cuenta_corriente)
        
        db.commit()
        db.refresh(cuenta)
        return cuenta
    
    @staticmethod
    def obtener_cuenta_por_usuario(db: Session, usuario: str) -> Cuenta:
        return db.query(Cuenta).filter(Cuenta.cuen_usuario == usuario).first()
    
    @staticmethod
    def verificar_password(password_plano: str, password_hash: str) -> bool:
        return pwd_context.verify(password_plano, password_hash)

class TarjetaService:
    @staticmethod
    def generar_numero_tarjeta() -> str:
        """Genera un número de tarjeta de 16 dígitos"""
        return ''.join(random.choices('0123456789', k=16))
    
    @staticmethod
    def generar_cvv() -> str:
        """Genera un CVV de 3 dígitos"""
        return ''.join(random.choices('0123456789', k=3))
    
    @staticmethod
    def crear_tarjeta(db: Session, tarjeta_data: TarjetaCreate) -> Tarjeta:
        # Verificar que la cuenta existe
        cuenta = db.query(Cuenta).filter(Cuenta.cuen_id == tarjeta_data.cuen_id).first()
        if not cuenta:
            raise ValueError("Cuenta no encontrada")
        
        # Validar restricciones de tarjetas según tipo de cuenta
        if cuenta.cuen_tipo == "AHORRO" and tarjeta_data.tar_tipo == "CREDITO":
            raise ValueError("Las cuentas de ahorro solo pueden tener tarjetas de débito")
        
        # Para cuentas de ahorro (débito): sin límite de creación de tarjetas débito
        # Para cuentas corrientes: pueden tener ambos tipos
        
        # Verificar si ya existe una tarjeta del mismo tipo para esta cuenta
        # Solo aplicar límite para cuentas corrientes con tarjetas de crédito
        if cuenta.cuen_tipo == "CORRIENTE" and tarjeta_data.tar_tipo == "CREDITO":
            tarjeta_existente = db.query(Tarjeta).filter(
                Tarjeta.cuen_id == tarjeta_data.cuen_id,
                Tarjeta.tar_tipo == "CREDITO"
            ).first()
            
            if tarjeta_existente:
                raise ValueError("La cuenta corriente ya tiene una tarjeta de crédito. Solo se permite una tarjeta de crégito por cuenta corriente.")
        
        # Las cuentas de ahorro pueden tener múltiples tarjetas de débito sin límite
        
        # Generar número de tarjeta único
        numero_tarjeta = TarjetaService.generar_numero_tarjeta()
        while db.query(Tarjeta).filter(Tarjeta.tar_numero_tarjeta == numero_tarjeta).first():
            numero_tarjeta = TarjetaService.generar_numero_tarjeta()
        
        # Generar nuevo TAR_ID
        new_tar_id = get_next_id(db, Tarjeta, 'tar_id')
        
        fecha_emision = datetime.now()
        fecha_expiracion = fecha_emision + timedelta(days=365*4)  # 4 años
        cvv = TarjetaService.generar_cvv()
        
        # Crear registro en tabla base TARJETA (con PIN encriptado)
        tarjeta_base = Tarjeta(
            tar_id=new_tar_id,
            cuen_id=tarjeta_data.cuen_id,
            tar_numero_tarjeta=numero_tarjeta,
            tar_fecha_emision=fecha_emision,
            tar_fecha_expiracion=fecha_expiracion,
            tar_estado_tarjeta=tarjeta_data.tar_estado_tarjeta,
            tar_cvv=cvv,
            tar_tipo=tarjeta_data.tar_tipo,
            tar_pin=tarjeta_data.tar_pin  # PIN en texto plano según esquema
        )
        
        db.add(tarjeta_base)
        db.flush()  # Para obtener el TAR_ID generado
        
        # Crear registro en tabla específica según el tipo (duplicando todos los campos)
        if tarjeta_data.tar_tipo == "DEBITO":
            tarjeta_debito = TarjetaDebito(
                tar_id=new_tar_id,
                cuen_id=tarjeta_data.cuen_id,
                tar_numero_tarjeta=numero_tarjeta,
                tar_fecha_emision=fecha_emision,
                tar_fecha_expiracion=fecha_expiracion,
                tar_estado_tarjeta=tarjeta_data.tar_estado_tarjeta,
                tar_cvv=cvv,
                tar_tipo=tarjeta_data.tar_tipo,
                tar_pin=tarjeta_data.tar_pin,  # PIN duplicado
                td_limite_retiro_diario=Decimal('500.00'),  # Valor por defecto
                td_comision_sobregiro=Decimal('5.00')       # Valor por defecto
            )
            db.add(tarjeta_debito)
            
        elif tarjeta_data.tar_tipo == "CREDITO":
            tarjeta_credito = TarjetaCredito(
                tar_id=new_tar_id,
                cuen_id=tarjeta_data.cuen_id,
                tar_numero_tarjeta=numero_tarjeta,
                tar_fecha_emision=fecha_emision,
                tar_fecha_expiracion=fecha_expiracion,
                tar_estado_tarjeta=tarjeta_data.tar_estado_tarjeta,
                tar_cvv=cvv,
                tar_tipo=tarjeta_data.tar_tipo,
                tar_pin=tarjeta_data.tar_pin,  # PIN duplicado
                tc_limite_credito=Decimal('1000.00'),       # Valor por defecto
                tc_tasa_interes=Decimal('24.50'),           # Valor por defecto
                tc_cargo_anual=Decimal('50.00'),            # Valor por defecto
                tc_fecha_corte=fecha_emision + timedelta(days=30),
                tc_fecha_vencimiento=fecha_emision + timedelta(days=45),
                tc_morosidad=False
            )
            db.add(tarjeta_credito)
        
        db.commit()
        db.refresh(tarjeta_base)
        return tarjeta_base
    
    @staticmethod
    def obtener_tarjeta_por_numero(db: Session, numero_tarjeta: str) -> Tarjeta:
        return db.query(Tarjeta).filter(Tarjeta.tar_numero_tarjeta == numero_tarjeta).first()
    
    @staticmethod
    def verificar_pin(pin_plano: str, pin_hash: str) -> bool:
        return pwd_context.verify(pin_plano, pin_hash)

class TransaccionService:
    @staticmethod
    def procesar_retiro(db: Session, retiro_data: RetiroCreate) -> dict:
        try:
            # Verificar cuenta
            cuenta = db.query(Cuenta).filter(Cuenta.cuen_id == retiro_data.cuen_id).first()
            if not cuenta:
                raise ValueError("Cuenta no encontrada")
            
            if cuenta.cuen_estado != "ACTIVA":
                raise ValueError("La cuenta no está activa")
            
            # Verificar cajero
            cajero = db.query(Cajero).filter(Cajero.caj_id == retiro_data.caj_id).first()
            if not cajero:
                raise ValueError("Cajero no encontrado")
            
            if cajero.caj_estado != "ACTIVO":
                raise ValueError("El cajero no está disponible")
            
            # Verificar saldo
            if float(cuenta.cuen_saldo) < retiro_data.ret_monto:
                raise ValueError("Saldo insuficiente")
            
            # Generar IDs
            new_tran_id = get_next_id(db, Transaccion, 'tran_id')
            new_ret_id = get_next_id(db, Retiro, 'ret_id')
            
            # Crear transacción
            transaccion = Transaccion(
                tran_id=new_tran_id,
                cuen_id=retiro_data.cuen_id,
                caj_id=retiro_data.caj_id
            )
            db.add(transaccion)
            
            # Generar número de transacción
            numero_tran = str(random.randint(1000, 9999))
            
            # Crear retiro base
            retiro = Retiro(
                tran_id=new_tran_id,
                ret_id=new_ret_id,
                cuen_id=retiro_data.cuen_id,
                caj_id=retiro_data.caj_id,
                ret_fecha=datetime.now(),
                ret_monto=retiro_data.ret_monto,
                ret_cajero=f"CAJ{retiro_data.caj_id:04d}",
                ret_numero_tran=numero_tran
            )
            db.add(retiro)
            
            mensaje = ""
            comprobante = {}
            
            # Procesar según el método
            if retiro_data.metodo == "CON_TARJETA":
                if not retiro_data.numero_tarjeta or not retiro_data.pin:
                    raise ValueError("Número de tarjeta y PIN son requeridos")
                
                tarjeta = TarjetaService.obtener_tarjeta_por_numero(db, retiro_data.numero_tarjeta)
                if not tarjeta:
                    raise ValueError("Tarjeta no encontrada")
                
                if tarjeta.cuen_id != retiro_data.cuen_id:
                    raise ValueError("La tarjeta no pertenece a esta cuenta")
                
                if not TarjetaService.verificar_pin(retiro_data.pin, tarjeta.tar_pin):
                    raise ValueError("PIN incorrecto")
                
                # Crear retiro con tarjeta
                retiro_con_tarjeta = RetiroConTarjeta(
                    tran_id=new_tran_id,
                    ret_id=new_ret_id,
                    cuen_id=retiro_data.cuen_id,
                    caj_id=retiro_data.caj_id,
                    ret_fecha=datetime.now(),
                    ret_monto=retiro_data.ret_monto,
                    ret_cajero=f"CAJ{retiro_data.caj_id:04d}",
                    ret_numero_tran=numero_tran,
                    rett_imprimir="SI",
                    rett_montomax=500  # Límite por defecto
                )
                db.add(retiro_con_tarjeta)
                mensaje = "Retiro con tarjeta procesado exitosamente"
                
            elif retiro_data.metodo == "SIN_TARJETA":
                if not retiro_data.telefono or not retiro_data.codigo_retiro:
                    raise ValueError("Teléfono y código de retiro son requeridos")
                
                # Verificar que el teléfono corresponde al cliente
                cliente = db.query(Cliente).filter(
                    Cliente.per_id == cuenta.per_id,
                    Cliente.cli_id == cuenta.cli_id
                ).first()
                
                if cliente.per_telefono != retiro_data.telefono:
                    raise ValueError("El teléfono no corresponde al titular de la cuenta")
                
                # Crear retiro sin tarjeta
                retiro_sin_tarjeta = RetiroSinTarjeta(
                    tran_id=new_tran_id,
                    ret_id=new_ret_id,
                    cuen_id=retiro_data.cuen_id,
                    caj_id=retiro_data.caj_id,
                    ret_fecha=datetime.now(),
                    ret_monto=retiro_data.ret_monto,
                    ret_cajero=f"CAJ{retiro_data.caj_id:04d}",
                    ret_numero_tran=numero_tran,
                    rets_codigo=retiro_data.codigo_retiro,
                    rets_telefono_asociado=retiro_data.telefono,
                    rets_estado_codigo="USADO"
                )
                db.add(retiro_sin_tarjeta)
                mensaje = "Retiro sin tarjeta procesado exitosamente"
            
            # Actualizar saldo de la cuenta
            nuevo_saldo = float(cuenta.cuen_saldo) - retiro_data.ret_monto
            cuenta.cuen_saldo = nuevo_saldo
            
            db.commit()
            
            # Preparar comprobante
            comprobante = {
                "banco": "Banco Pichincha",
                "transaccion": numero_tran,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "cajero": cajero.caj_ubicacion,
                "cuenta": cuenta.cuen_numero_cuenta[-4:],  # Solo últimos 4 dígitos
                "monto": retiro_data.ret_monto,
                "saldo_anterior": float(cuenta.cuen_saldo) + retiro_data.ret_monto,
                "saldo_actual": nuevo_saldo
            }
            
            return {
                "tran_id": new_tran_id,
                "ret_id": new_ret_id,
                "ret_fecha": datetime.now(),
                "ret_monto": retiro_data.ret_monto,
                "ret_numero_tran": numero_tran,
                "mensaje": mensaje,
                "comprobante": comprobante
            }
            
        except Exception as e:
            db.rollback()
            raise e
