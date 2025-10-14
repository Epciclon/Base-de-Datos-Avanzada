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
        persona_existente = db.query(Persona).filter(Persona.PER_CORREO == cliente_data.PER_CORREO).first()
        if persona_existente:
            raise ValueError(f"Ya existe una persona registrada con el correo electrónico: {cliente_data.PER_CORREO}")
        
        # 2. Si es persona natural, verificar cédula
        if cliente_data.identificacion:
            persona_natural_existente = db.query(PersonaNatural).filter(
                PersonaNatural.PN_IDENTIFICACION == cliente_data.identificacion
            ).first()
            if persona_natural_existente:
                raise ValueError(f"Ya existe una persona registrada con la cédula: {cliente_data.identificacion}")
        
        # 3. Si es persona jurídica, verificar RUC
        if cliente_data.ruc:
            persona_juridica_existente = db.query(PersonaJuridica).filter(
                PersonaJuridica.PJ_RUC == cliente_data.ruc
            ).first()
            if persona_juridica_existente:
                raise ValueError(f"Ya existe una empresa registrada con el RUC: {cliente_data.ruc}")
        
        # Generar nuevos IDs usando la utilidad
        new_per_id = get_next_id(db, Persona, 'PER_ID')
        new_cli_id = get_next_id(db, Cliente, 'CLI_ID')
        
        # Determinar el tipo de persona
        per_tipo = "NATURAL" if cliente_data.identificacion else "JURIDICA"
        
        # Crear persona
        persona = Persona(
            PER_ID=new_per_id,
            PER_NOMBRES=cliente_data.PER_NOMBRES,
            PER_APELLIDOS=cliente_data.PER_APELLIDOS,
            PER_FECHA_NACIMIENTO=cliente_data.PER_FECHA_NACIMIENTO,
            PER_GENERO=cliente_data.PER_GENERO,
            PER_TELEFONO=cliente_data.PER_TELEFONO,
            PER_CORREO=cliente_data.PER_CORREO,
            PER_DIRECCION=cliente_data.PER_DIRECCION,
            PER_TIPO=per_tipo
        )
        db.add(persona)
        db.flush()
        
        # Si es persona natural, crear registro en PersonaNatural
        if cliente_data.identificacion:
            persona_natural = PersonaNatural(
                PER_ID=new_per_id,
                PER_NOMBRES=cliente_data.PER_NOMBRES,
                PER_APELLIDOS=cliente_data.PER_APELLIDOS,
                PER_FECHA_NACIMIENTO=cliente_data.PER_FECHA_NACIMIENTO,
                PER_GENERO=cliente_data.PER_GENERO,
                PER_TELEFONO=cliente_data.PER_TELEFONO,
                PER_CORREO=cliente_data.PER_CORREO,
                PER_DIRECCION=cliente_data.PER_DIRECCION,
                PER_TIPO="NATURAL",
                PN_IDENTIFICACION=cliente_data.identificacion,
                PN_ESTADO_CIVIL=cliente_data.estado_civil or "SOLTERO",
                PN_PROFESION=cliente_data.profesion or "NO ESPECIFICADO"
            )
            db.add(persona_natural)
        
        # Si es persona jurídica, crear registro en PersonaJuridica
        elif cliente_data.ruc:
            persona_juridica = PersonaJuridica(
                PER_ID=new_per_id,
                PER_NOMBRES=cliente_data.PER_NOMBRES,
                PER_APELLIDOS=cliente_data.PER_APELLIDOS,
                PER_FECHA_NACIMIENTO=cliente_data.PER_FECHA_NACIMIENTO,
                PER_GENERO=cliente_data.PER_GENERO,
                PER_TELEFONO=cliente_data.PER_TELEFONO,
                PER_CORREO=cliente_data.PER_CORREO,
                PER_DIRECCION=cliente_data.PER_DIRECCION,
                PER_TIPO="JURIDICA",
                PJ_RUC=cliente_data.ruc,
                PJ_REPRESENTANTE=cliente_data.representante_legal or "NO ESPECIFICADO",
                PJ_TIPO_ENTIDAD=cliente_data.tipo_entidad or "OTRA",
                PJ_FECHA_CONSTITUCION=cliente_data.fecha_constitucion or datetime.now(),
                PJ_ACTIVIDAD=cliente_data.actividad_economica or "NO ESPECIFICADO"
            )
            db.add(persona_juridica)
        
        # Crear cliente
        cliente = Cliente(
            PER_ID=new_per_id,
            CLI_ID=new_cli_id,
            PER_NOMBRES=cliente_data.PER_NOMBRES,
            PER_APELLIDOS=cliente_data.PER_APELLIDOS,
            PER_FECHA_NACIMIENTO=cliente_data.PER_FECHA_NACIMIENTO,
            PER_GENERO=cliente_data.PER_GENERO,
            PER_TELEFONO=cliente_data.PER_TELEFONO,
            PER_CORREO=cliente_data.PER_CORREO,
            PER_DIRECCION=cliente_data.PER_DIRECCION,
            PER_TIPO=per_tipo,
            CLI_FECHA_INGRESP=datetime.now(),
            CLI_ESTADO=cliente_data.CLI_ESTADO
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
        
        return cliente
    
    @staticmethod
    def obtener_cliente_por_id(db: Session, per_id: int, cli_id: int) -> Cliente:
        return db.query(Cliente).filter(
            Cliente.PER_ID == per_id, 
            Cliente.CLI_ID == cli_id
        ).first()
    
    @staticmethod
    def obtener_cliente_por_identificacion(db: Session, identificacion: str = None, ruc: str = None, correo: str = None) -> Cliente:
        """
        Buscar cliente existente por identificación (cédula/RUC) o correo
        """
        if identificacion:
            # Buscar por cédula en PersonaNatural
            persona_natural = db.query(PersonaNatural).filter(
                PersonaNatural.PN_IDENTIFICACION == identificacion
            ).first()
            if persona_natural:
                return db.query(Cliente).filter(Cliente.PER_ID == persona_natural.PER_ID).first()
        
        if ruc:
            # TODO: Buscar por RUC en PersonaJuridica cuando se implemente
            pass
            
        if correo:
            # Buscar por correo
            persona = db.query(Persona).filter(Persona.PER_CORREO == correo).first()
            if persona:
                return db.query(Cliente).filter(Cliente.PER_ID == persona.PER_ID).first()
        
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
            Cliente.PER_ID == per_id, 
            Cliente.CLI_ID == cli_id
        ).first()
        if not cliente:
            raise ValueError("Cliente no encontrado")
        
        # Verificar si el cliente ya tiene una cuenta del mismo tipo
        cuenta_existente = db.query(Cuenta).filter(
            Cuenta.PER_ID == per_id,
            Cuenta.CLI_ID == cli_id,
            Cuenta.CUEN_TIPO == cuenta_data.CUEN_TIPO
        ).first()
        
        if cuenta_existente:
            raise ValueError(f"El cliente ya tiene una cuenta de tipo {cuenta_data.CUEN_TIPO}. Un cliente solo puede tener una cuenta de cada tipo.")
        
        # Verificar unicidad del usuario de cuenta
        usuario_existente = db.query(Cuenta).filter(Cuenta.CUEN_USUARIO == cuenta_data.CUEN_USUARIO).first()
        if usuario_existente:
            raise ValueError(f"El nombre de usuario '{cuenta_data.CUEN_USUARIO}' ya está en uso. Por favor elige otro.")
        
        # Generar número de cuenta único
        numero_cuenta = CuentaService.generar_numero_cuenta()
        while db.query(Cuenta).filter(Cuenta.CUEN_NUMERO_CUENTA == numero_cuenta).first():
            numero_cuenta = CuentaService.generar_numero_cuenta()
        
        # Generar nuevo CUEN_ID
        new_cuen_id = get_next_id(db, Cuenta, 'CUEN_ID')
        
        # Crear cuenta principal
        cuenta = Cuenta(
            CUEN_ID=new_cuen_id,
            PER_ID=per_id,
            CLI_ID=cli_id,
            CUEN_USUARIO=cuenta_data.CUEN_USUARIO,
            CUEN_PASSWORD=pwd_context.hash(cuenta_data.CUEN_PASSWORD),
            CUEN_TIPO=cuenta_data.CUEN_TIPO,
            CUEN_NUMERO_CUENTA=numero_cuenta,
            CUEN_SALDO=cuenta_data.CUEN_SALDO,
            CUEN_ESTADO=cuenta_data.CUEN_ESTADO
        )
        db.add(cuenta)
        db.flush()
        
        # Crear cuenta específica según el tipo
        if cuenta_data.CUEN_TIPO == "AHORRO":
            if isinstance(cuenta_data, CuentaAhorroCreate):
                cuenta_ahorro = CuentaAhorro(
                    CUEN_ID=new_cuen_id,
                    PER_ID=per_id,
                    CLI_ID=cli_id,
                    CUEN_USUARIO=cuenta_data.CUEN_USUARIO,
                    CUEN_PASSWORD=pwd_context.hash(cuenta_data.CUEN_PASSWORD),
                    CUEN_TIPO=cuenta_data.CUEN_TIPO,
                    CUEN_NUMERO_CUENTA=numero_cuenta,
                    CUEN_SALDO=cuenta_data.CUEN_SALDO,
                    CUEN_ESTADO=cuenta_data.CUEN_ESTADO,
                    CA_INTERES=cuenta_data.CA_INTERES,
                    CA_LIMITE_RETIROS=cuenta_data.CA_LIMITE_RETIROS,
                    CA_MIN_SALDO_REMUNERADO=cuenta_data.CA_MIN_SALDO_REMUNERADO
                )
                db.add(cuenta_ahorro)
        elif cuenta_data.CUEN_TIPO == "CORRIENTE":
            if isinstance(cuenta_data, CuentaCorrienteCreate):
                cuenta_corriente = CuentaCorriente(
                    CUEN_ID=new_cuen_id,
                    PER_ID=per_id,
                    CLI_ID=cli_id,
                    CUEN_USUARIO=cuenta_data.CUEN_USUARIO,
                    CUEN_PASSWORD=pwd_context.hash(cuenta_data.CUEN_PASSWORD),
                    CUEN_TIPO=cuenta_data.CUEN_TIPO,
                    CUEN_NUMERO_CUENTA=numero_cuenta,
                    CUEN_SALDO=cuenta_data.CUEN_SALDO,
                    CUEN_ESTADO=cuenta_data.CUEN_ESTADO,
                    CC_LIMITE_DESCUBIERTO=cuenta_data.CC_LIMITE_DESCUBIERTO,
                    CC_COMISION_MANTENIMIENTO=cuenta_data.CC_COMISION_MANTENIMIENTO,
                    CC_NUM_CHEQUES=cuenta_data.CC_NUM_CHEQUES
                )
                db.add(cuenta_corriente)
        
        db.commit()
        db.refresh(cuenta)
        return cuenta
    
    @staticmethod
    def obtener_cuenta_por_usuario(db: Session, usuario: str) -> Cuenta:
        return db.query(Cuenta).filter(Cuenta.CUEN_USUARIO == usuario).first()
    
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
        cuenta = db.query(Cuenta).filter(Cuenta.CUEN_ID == tarjeta_data.CUEN_ID).first()
        if not cuenta:
            raise ValueError("Cuenta no encontrada")
        
        # Validar restricciones de tarjetas según tipo de cuenta
        if cuenta.CUEN_TIPO == "AHORRO" and tarjeta_data.TAR_TIPO == "CREDITO":
            raise ValueError("Las cuentas de ahorro solo pueden tener tarjetas de débito")
        
        # Verificar si ya existe una tarjeta del mismo tipo para esta cuenta
        tarjeta_existente = db.query(Tarjeta).filter(
            Tarjeta.CUEN_ID == tarjeta_data.CUEN_ID,
            Tarjeta.TAR_TIPO == tarjeta_data.TAR_TIPO
        ).first()
        
        if tarjeta_existente:
            raise ValueError(f"La cuenta ya tiene una tarjeta de {tarjeta_data.TAR_TIPO}. Solo se permite una tarjeta por tipo.")
        
        # Generar número de tarjeta único
        numero_tarjeta = TarjetaService.generar_numero_tarjeta()
        while db.query(Tarjeta).filter(Tarjeta.TAR_NUMERO_TARJETA == numero_tarjeta).first():
            numero_tarjeta = TarjetaService.generar_numero_tarjeta()
        
        # Generar nuevo TAR_ID
        new_tar_id = get_next_id(db, Tarjeta, 'TAR_ID')
        
        fecha_emision = datetime.now()
        fecha_expiracion = fecha_emision + timedelta(days=365*4)  # 4 años
        cvv = TarjetaService.generar_cvv()
        
        # Crear registro en tabla base TARJETA (con PIN encriptado)
        tarjeta_base = Tarjeta(
            TAR_ID=new_tar_id,
            CUEN_ID=tarjeta_data.CUEN_ID,
            TAR_NUMERO_TARJETA=numero_tarjeta,
            TAR_FECHA_EMISION=fecha_emision,
            TAR_FECHA_EXPIRACION=fecha_expiracion,
            TAR_ESTADO_TARJETA=tarjeta_data.TAR_ESTADO_TARJETA,
            TAR_CVV=cvv,
            TAR_TIPO=tarjeta_data.TAR_TIPO,
            TAR_PIN=tarjeta_data.TAR_PIN  # PIN en texto plano según esquema
        )
        
        db.add(tarjeta_base)
        db.flush()  # Para obtener el TAR_ID generado
        
        # Crear registro en tabla específica según el tipo (duplicando todos los campos)
        if tarjeta_data.TAR_TIPO == "DEBITO":
            tarjeta_debito = TarjetaDebito(
                TAR_ID=new_tar_id,
                CUEN_ID=tarjeta_data.CUEN_ID,
                TAR_NUMERO_TARJETA=numero_tarjeta,
                TAR_FECHA_EMISION=fecha_emision,
                TAR_FECHA_EXPIRACION=fecha_expiracion,
                TAR_ESTADO_TARJETA=tarjeta_data.TAR_ESTADO_TARJETA,
                TAR_CVV=cvv,
                TAR_TIPO=tarjeta_data.TAR_TIPO,
                TAR_PIN=tarjeta_data.TAR_PIN,  # PIN duplicado
                TD_LIMITE_RETIRO_DIARIO=Decimal('500.00'),  # Valor por defecto
                TD_COMISION_SOBREGIRO=Decimal('5.00')       # Valor por defecto
            )
            db.add(tarjeta_debito)
            
        elif tarjeta_data.TAR_TIPO == "CREDITO":
            tarjeta_credito = TarjetaCredito(
                TAR_ID=new_tar_id,
                CUEN_ID=tarjeta_data.CUEN_ID,
                TAR_NUMERO_TARJETA=numero_tarjeta,
                TAR_FECHA_EMISION=fecha_emision,
                TAR_FECHA_EXPIRACION=fecha_expiracion,
                TAR_ESTADO_TARJETA=tarjeta_data.TAR_ESTADO_TARJETA,
                TAR_CVV=cvv,
                TAR_TIPO=tarjeta_data.TAR_TIPO,
                TAR_PIN=tarjeta_data.TAR_PIN,  # PIN duplicado
                TC_LIMITE_CREDITO=Decimal('1000.00'),       # Valor por defecto
                TC_TASA_INTERES=Decimal('24.50'),           # Valor por defecto
                TC_CARGO_ANUAL=Decimal('50.00'),            # Valor por defecto
                TC_FECHA_CORTE=fecha_emision + timedelta(days=30),
                TC_FECHA_VENCIMIENTO=fecha_emision + timedelta(days=45),
                TC_MOROSIDAD=False
            )
            db.add(tarjeta_credito)
        
        db.commit()
        db.refresh(tarjeta_base)
        return tarjeta_base
    
    @staticmethod
    def obtener_tarjeta_por_numero(db: Session, numero_tarjeta: str) -> Tarjeta:
        return db.query(Tarjeta).filter(Tarjeta.TAR_NUMERO_TARJETA == numero_tarjeta).first()
    
    @staticmethod
    def verificar_pin(pin_plano: str, pin_hash: str) -> bool:
        return pwd_context.verify(pin_plano, pin_hash)

class TransaccionService:
    @staticmethod
    def procesar_retiro(db: Session, retiro_data: RetiroCreate) -> dict:
        try:
            # Verificar cuenta
            cuenta = db.query(Cuenta).filter(Cuenta.CUEN_ID == retiro_data.CUEN_ID).first()
            if not cuenta:
                raise ValueError("Cuenta no encontrada")
            
            if cuenta.CUEN_ESTADO != "ACTIVA":
                raise ValueError("La cuenta no está activa")
            
            # Verificar cajero
            cajero = db.query(Cajero).filter(Cajero.CAJ_ID == retiro_data.CAJ_ID).first()
            if not cajero:
                raise ValueError("Cajero no encontrado")
            
            if cajero.CAJ_ESTADO != "ACTIVO":
                raise ValueError("El cajero no está disponible")
            
            # Verificar saldo
            if float(cuenta.CUEN_SALDO) < retiro_data.RET_MONTO:
                raise ValueError("Saldo insuficiente")
            
            # Generar IDs
            new_tran_id = get_next_id(db, Transaccion, 'TRAN_ID')
            new_ret_id = get_next_id(db, Retiro, 'RET_ID')
            
            # Crear transacción
            transaccion = Transaccion(
                TRAN_ID=new_tran_id,
                CUEN_ID=retiro_data.CUEN_ID,
                CAJ_ID=retiro_data.CAJ_ID
            )
            db.add(transaccion)
            
            # Generar número de transacción
            numero_tran = str(random.randint(1000, 9999))
            
            # Crear retiro base
            retiro = Retiro(
                TRAN_ID=new_tran_id,
                RET_ID=new_ret_id,
                CUEN_ID=retiro_data.CUEN_ID,
                CAJ_ID=retiro_data.CAJ_ID,
                RET_FECHA=datetime.now(),
                RET_MONTO=retiro_data.RET_MONTO,
                RET_CAJERO=f"CAJ{retiro_data.CAJ_ID:04d}",
                RET_NUMERO_TRAN=numero_tran
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
                
                if tarjeta.CUEN_ID != retiro_data.CUEN_ID:
                    raise ValueError("La tarjeta no pertenece a esta cuenta")
                
                if not TarjetaService.verificar_pin(retiro_data.pin, tarjeta.TAR_PIN):
                    raise ValueError("PIN incorrecto")
                
                # Crear retiro con tarjeta
                retiro_con_tarjeta = RetiroConTarjeta(
                    TRAN_ID=new_tran_id,
                    RET_ID=new_ret_id,
                    CUEN_ID=retiro_data.CUEN_ID,
                    CAJ_ID=retiro_data.CAJ_ID,
                    RET_FECHA=datetime.now(),
                    RET_MONTO=retiro_data.RET_MONTO,
                    RET_CAJERO=f"CAJ{retiro_data.CAJ_ID:04d}",
                    RET_NUMERO_TRAN=numero_tran,
                    RETT_IMPRIMIR="SI",
                    RETT_MONTOMAX=500  # Límite por defecto
                )
                db.add(retiro_con_tarjeta)
                mensaje = "Retiro con tarjeta procesado exitosamente"
                
            elif retiro_data.metodo == "SIN_TARJETA":
                if not retiro_data.telefono or not retiro_data.codigo_retiro:
                    raise ValueError("Teléfono y código de retiro son requeridos")
                
                # Verificar que el teléfono corresponde al cliente
                cliente = db.query(Cliente).filter(
                    Cliente.PER_ID == cuenta.PER_ID,
                    Cliente.CLI_ID == cuenta.CLI_ID
                ).first()
                
                if cliente.PER_TELEFONO != retiro_data.telefono:
                    raise ValueError("El teléfono no corresponde al titular de la cuenta")
                
                # Crear retiro sin tarjeta
                retiro_sin_tarjeta = RetiroSinTarjeta(
                    TRAN_ID=new_tran_id,
                    RET_ID=new_ret_id,
                    CUEN_ID=retiro_data.CUEN_ID,
                    CAJ_ID=retiro_data.CAJ_ID,
                    RET_FECHA=datetime.now(),
                    RET_MONTO=retiro_data.RET_MONTO,
                    RET_CAJERO=f"CAJ{retiro_data.CAJ_ID:04d}",
                    RET_NUMERO_TRAN=numero_tran,
                    RETS_CODIGO=retiro_data.codigo_retiro,
                    RETS_TELEFONO_ASOCIADO=retiro_data.telefono,
                    RETS_ESTADO_CODIGO="USADO"
                )
                db.add(retiro_sin_tarjeta)
                mensaje = "Retiro sin tarjeta procesado exitosamente"
            
            # Actualizar saldo de la cuenta
            nuevo_saldo = float(cuenta.CUEN_SALDO) - retiro_data.RET_MONTO
            cuenta.CUEN_SALDO = nuevo_saldo
            
            db.commit()
            
            # Preparar comprobante
            comprobante = {
                "banco": "Banco Pichincha",
                "transaccion": numero_tran,
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "cajero": cajero.CAJ_UBICACION,
                "cuenta": cuenta.CUEN_NUMERO_CUENTA[-4:],  # Solo últimos 4 dígitos
                "monto": retiro_data.RET_MONTO,
                "saldo_anterior": float(cuenta.CUEN_SALDO) + retiro_data.RET_MONTO,
                "saldo_actual": nuevo_saldo
            }
            
            return {
                "TRAN_ID": new_tran_id,
                "RET_ID": new_ret_id,
                "RET_FECHA": datetime.now(),
                "RET_MONTO": retiro_data.RET_MONTO,
                "RET_NUMERO_TRAN": numero_tran,
                "mensaje": mensaje,
                "comprobante": comprobante
            }
            
        except Exception as e:
            db.rollback()
            raise e
