from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base

class Persona(Base):
    __tablename__ = "PERSONA"
    
    PER_ID = Column(Integer, primary_key=True, autoincrement=False)
    PER_NOMBRES = Column(String(300), nullable=False)
    PER_APELLIDOS = Column(String(300), nullable=False)
    PER_FECHA_NACIMIENTO = Column(DateTime, nullable=False)
    PER_GENERO = Column(String(64), nullable=False)
    PER_TELEFONO = Column(String(10), nullable=False)
    PER_CORREO = Column(String(64), nullable=False)
    PER_DIRECCION = Column(String(124), nullable=False)
    PER_TIPO = Column(String(64), nullable=False)

class PersonaNatural(Base):
    __tablename__ = "PERSONA_NATURAL"
    
    PER_ID = Column(Integer, ForeignKey("PERSONA.PER_ID"), primary_key=True)
    PER_NOMBRES = Column(String(300), nullable=False)
    PER_APELLIDOS = Column(String(300), nullable=False)
    PER_FECHA_NACIMIENTO = Column(DateTime, nullable=False)
    PER_GENERO = Column(String(64), nullable=False)
    PER_TELEFONO = Column(String(10), nullable=False)
    PER_CORREO = Column(String(64), nullable=False)
    PER_DIRECCION = Column(String(124), nullable=False)
    PER_TIPO = Column(String(64), nullable=False)
    PN_IDENTIFICACION = Column(String(13), nullable=False)
    PN_ESTADO_CIVIL = Column(String(20), nullable=False)
    PN_PROFESION = Column(String(100), nullable=False)

class PersonaJuridica(Base):
    __tablename__ = "PERSONA_JURIDICA"
    
    PER_ID = Column(Integer, ForeignKey("PERSONA.PER_ID"), primary_key=True)
    PER_NOMBRES = Column(String(300), nullable=False)
    PER_APELLIDOS = Column(String(300), nullable=False)
    PER_FECHA_NACIMIENTO = Column(DateTime, nullable=False)
    PER_GENERO = Column(String(64), nullable=False)
    PER_TELEFONO = Column(String(10), nullable=False)
    PER_CORREO = Column(String(64), nullable=False)
    PER_DIRECCION = Column(String(124), nullable=False)
    PER_TIPO = Column(String(64), nullable=False)
    PJ_RUC = Column(String(13), nullable=False)
    PJ_REPRESENTANTE = Column(String(100), nullable=False)
    PJ_TIPO_ENTIDAD = Column(String(50), nullable=False)
    PJ_FECHA_CONSTITUCION = Column(DateTime, nullable=False)
    PJ_ACTIVIDAD = Column(String(200), nullable=False)

class Cliente(Base):
    __tablename__ = "CLIENTE"
    
    PER_ID = Column(Integer, ForeignKey("PERSONA.PER_ID"), primary_key=True)
    CLI_ID = Column(Integer, primary_key=True)
    PER_NOMBRES = Column(String(300), nullable=False)
    PER_APELLIDOS = Column(String(300), nullable=False)
    PER_FECHA_NACIMIENTO = Column(DateTime, nullable=False)
    PER_GENERO = Column(String(64), nullable=False)
    PER_TELEFONO = Column(String(10), nullable=False)
    PER_CORREO = Column(String(64), nullable=False)
    PER_DIRECCION = Column(String(124), nullable=False)
    PER_TIPO = Column(String(64), nullable=False)
    CLI_FECHA_INGRESP = Column(DateTime, nullable=False)
    CLI_ESTADO = Column(String(64), nullable=False)

class Cuenta(Base):
    __tablename__ = "CUENTA"
    
    CUEN_ID = Column(Integer, primary_key=True, autoincrement=False)
    PER_ID = Column(Integer, nullable=False)
    CLI_ID = Column(Integer, nullable=False)
    CUEN_USUARIO = Column(String(64), nullable=False)
    CUEN_PASSWORD = Column(String(64), nullable=False)
    CUEN_TIPO = Column(String(64), nullable=False)
    CUEN_NUMERO_CUENTA = Column(String(10), nullable=False, unique=True)
    CUEN_SALDO = Column(Numeric, nullable=False)
    CUEN_ESTADO = Column(String(64), nullable=False)

class CuentaAhorro(Base):
    __tablename__ = "CUENTA_AHORRO"
    
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), primary_key=True)
    PER_ID = Column(Integer)
    CLI_ID = Column(Integer, nullable=False)
    CUEN_USUARIO = Column(String(64), nullable=False)
    CUEN_PASSWORD = Column(String(64), nullable=False)
    CUEN_TIPO = Column(String(64), nullable=False)
    CUEN_NUMERO_CUENTA = Column(String(10), nullable=False)
    CUEN_SALDO = Column(Numeric, nullable=False)
    CUEN_ESTADO = Column(String(64), nullable=False)
    CA_INTERES = Column(Numeric, nullable=False)
    CA_LIMITE_RETIROS = Column(Integer, nullable=False)
    CA_MIN_SALDO_REMUNERADO = Column(Numeric, nullable=False)

class CuentaCorriente(Base):
    __tablename__ = "CUENTA_CORRIENTE"
    
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), primary_key=True)
    PER_ID = Column(Integer)
    CLI_ID = Column(Integer, nullable=False)
    CUEN_USUARIO = Column(String(64), nullable=False)
    CUEN_PASSWORD = Column(String(64), nullable=False)
    CUEN_TIPO = Column(String(64), nullable=False)
    CUEN_NUMERO_CUENTA = Column(String(10), nullable=False)
    CUEN_SALDO = Column(Numeric, nullable=False)
    CUEN_ESTADO = Column(String(64), nullable=False)
    CC_LIMITE_DESCUBIERTO = Column(Numeric, nullable=False)
    CC_COMISION_MANTENIMIENTO = Column(Numeric, nullable=False)
    CC_NUM_CHEQUES = Column(Integer, nullable=False)

class Cajero(Base):
    __tablename__ = "CAJERO"
    
    CAJ_ID = Column(Integer, primary_key=True, autoincrement=False)
    CAJ_UBICACION = Column(String(100), nullable=False)
    CAJ_ESTADO = Column(String(20), nullable=False)
    CAJ_TIPO = Column(String(30), nullable=False)
    CAJ_SUCURSAL = Column(String(50), nullable=False)

class Transaccion(Base):
    __tablename__ = "TRANSACCION"
    
    TRAN_ID = Column(Integer, primary_key=True, autoincrement=False)
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), nullable=False)
    CAJ_ID = Column(Integer, ForeignKey("CAJERO.CAJ_ID"), nullable=False)

class Retiro(Base):
    __tablename__ = "RETIRO"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    RET_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    RET_FECHA = Column(DateTime, nullable=False)
    RET_MONTO = Column(Integer, nullable=False)
    RET_CAJERO = Column(String(8), nullable=False)
    RET_NUMERO_TRAN = Column(String(4), nullable=False)

class RetiroConTarjeta(Base):
    __tablename__ = "RETIRO_CONTARJETA"
    
    TRAN_ID = Column(Integer, primary_key=True)
    RET_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    RET_FECHA = Column(DateTime, nullable=False)
    RET_MONTO = Column(Integer, nullable=False)
    RET_CAJERO = Column(String(8), nullable=False)
    RET_NUMERO_TRAN = Column(String(4), nullable=False)
    RETT_IMPRIMIR = Column(String(2), nullable=False)
    RETT_MONTOMAX = Column(Integer, nullable=False)

class RetiroSinTarjeta(Base):
    __tablename__ = "RETIRO_SINTARJETA"
    
    TRAN_ID = Column(Integer, primary_key=True)
    RET_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    RET_FECHA = Column(DateTime, nullable=False)
    RET_MONTO = Column(Integer, nullable=False)
    RET_CAJERO = Column(String(8), nullable=False)
    RET_NUMERO_TRAN = Column(String(4), nullable=False)
    COND_ID = Column(Integer, ForeignKey("CONDICIONES.COND_ID"), nullable=False)
    RETS_CODIGO = Column(String(8), nullable=False)
    RETS_TELEFONO_ASOCIADO = Column(String(10), nullable=False)
    RETS_ESTADO_CODIGO = Column(String(64), nullable=False)
    # Nota: RETS_INTENTOS_REALIZADOS y REST_FECHA no existen en la BD actual
    # Se manejará el conteo de intentos en el campo RETS_ESTADO_CODIGO

class Tarjeta(Base):
    __tablename__ = "TARJETA"
    
    TAR_ID = Column(Integer, primary_key=True, autoincrement=False)
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), nullable=False)
    TAR_NUMERO_TARJETA = Column(String(16), nullable=False, unique=True)
    TAR_FECHA_EMISION = Column(DateTime, nullable=False)
    TAR_FECHA_EXPIRACION = Column(DateTime, nullable=False)
    TAR_ESTADO_TARJETA = Column(String(64), nullable=False)
    TAR_CVV = Column(String(3), nullable=False)
    TAR_TIPO = Column(String(64), nullable=False)
    TAR_PIN = Column(String(4), nullable=False)

class Consulta(Base):
    __tablename__ = "CONSULTA"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    CONS_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    CONS_FECHA_HORA = Column(DateTime, nullable=False)
    CONS_COMISION = Column(Numeric, nullable=False)
    CONS_TIPO = Column(String(100), nullable=False)
    CONS_RESULTADOS = Column(Text, nullable=False)

class Deposito(Base):
    __tablename__ = "DEPOSITOS"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    DEP_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    DEP_FECHA = Column(DateTime, nullable=False)
    DEP_MONTO = Column(Numeric, nullable=False)
    DEP_CUENTA_DEST = Column(String(20), nullable=False)
    DEP_CANAL = Column(String(20), nullable=False)
    DEP_REFERENCIA = Column(String(30), nullable=False)
    DEP_ESTADO = Column(String(20), nullable=False)

class Transferencia(Base):
    __tablename__ = "TRANSFERENCIA"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    TRANS_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    TRANS_FECHA = Column(DateTime, nullable=False)
    TRANS_MONTO = Column(Numeric, nullable=False)
    TRANS_ORIGEN = Column(String(20), nullable=False)
    TRANS_DESTINO = Column(String(20), nullable=False)
    TRANS_CANAL = Column(String(20), nullable=False)
    TRANS_ESTADO = Column(String(20), nullable=False)

class PagoServicio(Base):
    __tablename__ = "PAGO_SERVICIOS"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    PS_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    PS_TIPO_SERVICIO = Column(String(100), nullable=False)
    PS_PROVEEDOR = Column(String(100), nullable=False)
    PS_REFERENCIA = Column(String(100), nullable=False)
    PS_MONTO = Column(Numeric, nullable=False)
    PS_FECHA_HORA = Column(DateTime, nullable=False)
    PS_COMISION = Column(Numeric, nullable=False)
    PS_RESULTADO_CODIGO = Column(String(10), nullable=False)
    PS_ESTADO = Column(String(20), nullable=False)
    PS_COMPROBANTE = Column(Text, nullable=False)

class BoucherCabecera(Base):
    __tablename__ = "BOUCHER_CABECERA"
    
    BAN_AID = Column(String(14), primary_key=True)
    BAN_NOMBRE = Column(String(64), nullable=False)
    BAN_DIRECCION = Column(String(64), nullable=False)
    BAN_RUC = Column(String(13), nullable=False)
    BAN_MENSAJE = Column(String(300), nullable=False)

class BoucherCuerpo(Base):
    __tablename__ = "BOUCHER_CUERPO"
    
    BOUC_ID = Column(Integer, primary_key=True)
    TRAN_ID = Column(Integer, primary_key=True)
    RET_ID = Column(Integer, primary_key=True)
    RETT_IMPRIMIR = Column(String(2), nullable=False)
    RETT_MONTOMAX = Column(Integer, nullable=False)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    RET_FECHA = Column(DateTime, nullable=False)
    RET_MONTO = Column(Integer, nullable=False)
    RET_CAJERO = Column(String(8), nullable=False)
    RET_NUMERO_TRAN = Column(String(4), nullable=False)
    BAN_AID = Column(String(14), ForeignKey("BOUCHER_CABECERA.BAN_AID"), nullable=False)
    BOUC_COSTO = Column(DECIMAL(10, 2), nullable=False)
    BOUC_TOTALDEBITADO = Column(DECIMAL(10, 2), nullable=False)

class TarjetaCredito(Base):
    __tablename__ = "TARJETA_CREDITO"
    
    TAR_ID = Column(Integer, ForeignKey("TARJETA.TAR_ID"), primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    TAR_NUMERO_TARJETA = Column(String(16), nullable=False)
    TAR_FECHA_EMISION = Column(DateTime, nullable=False)
    TAR_FECHA_EXPIRACION = Column(DateTime, nullable=False)
    TAR_ESTADO_TARJETA = Column(String(64), nullable=False)
    TAR_CVV = Column(String(3), nullable=False)
    TAR_TIPO = Column(String(64), nullable=False)
    TAR_PIN = Column(String(4), nullable=False)
    TC_LIMITE_CREDITO = Column(Numeric, nullable=False)
    TC_TASA_INTERES = Column(Numeric, nullable=False)
    TC_CARGO_ANUAL = Column(Numeric, nullable=False)
    TC_FECHA_CORTE = Column(DateTime, nullable=False)
    TC_FECHA_VENCIMIENTO = Column(DateTime, nullable=False)
    TC_MOROSIDAD = Column(Boolean, nullable=False)

class TarjetaDebito(Base):
    __tablename__ = "TARJETA_DEBITO"
    
    TAR_ID = Column(Integer, ForeignKey("TARJETA.TAR_ID"), primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    TAR_NUMERO_TARJETA = Column(String(16), nullable=False)
    TAR_FECHA_EMISION = Column(DateTime, nullable=False)
    TAR_FECHA_EXPIRACION = Column(DateTime, nullable=False)
    TAR_ESTADO_TARJETA = Column(String(64), nullable=False)
    TAR_CVV = Column(String(3), nullable=False)
    TAR_TIPO = Column(String(64), nullable=False)
    TAR_PIN = Column(String(4), nullable=False)
    TD_LIMITE_RETIRO_DIARIO = Column(Numeric, nullable=False)
    TD_COMISION_SOBREGIRO = Column(Numeric, nullable=False)

class Condiciones(Base):
    __tablename__ = "CONDICIONES"
    
    COND_ID = Column(Integer, primary_key=True)
    COND_DESCRIPCION = Column(String(200), nullable=False)
    COND_HORAS = Column(Integer, nullable=False)
    COND_INTENTOS = Column(Integer, nullable=False)
    COND_MONTO = Column(Integer, nullable=False)
    COND_ESTADO = Column(String(20), nullable=False)
