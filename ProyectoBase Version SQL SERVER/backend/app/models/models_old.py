from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.database import Base

class Persona(Base):
    __tablename__ = "PERSONA"
    
    PER_ID = Column(Integer, primary_key=True, index=True)
    PER_NOMBRES = Column(String(300), nullable=False)
    PER_APELLIDOS = Column(String(300), nullable=False)
    PER_FECHA_NACIMIENTO = Column(DateTime, nullable=False)
    PER_GENERO = Column(String(64), nullable=False)
    PER_TELEFONO = Column(String(10), nullable=False)
    PER_CORREO = Column(String(64), nullable=False)
    PER_DIRECCION = Column(String(124), nullable=False)
    PER_TIPO = Column(String(64), nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="persona")
    persona_natural = relationship("PersonaNatural", back_populates="persona")
    persona_juridica = relationship("PersonaJuridica", back_populates="persona")

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
    
    # Relación
    persona = relationship("Persona", back_populates="persona_natural")

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
    
    # Relación
    persona = relationship("Persona", back_populates="persona_juridica")

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
    
    # Relaciones
    persona = relationship("Persona", back_populates="cliente")
    cuentas = relationship("Cuenta", back_populates="cliente")

class Cuenta(Base):
    __tablename__ = "CUENTA"
    
    CUEN_ID = Column(Integer, primary_key=True, index=True)
    PER_ID = Column(Integer, nullable=False)
    CLI_ID = Column(Integer, nullable=False)
    CUEN_USUARIO = Column(String(64), nullable=False)
    CUEN_PASSWORD = Column(String(64), nullable=False)
    CUEN_TIPO = Column(String(64), nullable=False)
    CUEN_NUMERO_CUENTA = Column(String(10), nullable=False, unique=True)
    CUEN_SALDO = Column(Numeric(10, 2), nullable=False)
    CUEN_ESTADO = Column(String(64), nullable=False)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="cuentas")
    transacciones = relationship("Transaccion", back_populates="cuenta")
    tarjetas = relationship("Tarjeta", back_populates="cuenta")
    cuenta_ahorro = relationship("CuentaAhorro", back_populates="cuenta")
    cuenta_corriente = relationship("CuentaCorriente", back_populates="cuenta")

class CuentaAhorro(Base):
    __tablename__ = "CUENTA_AHORRO"
    
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), primary_key=True)
    PER_ID = Column(Integer)
    CLI_ID = Column(Integer, nullable=False)
    CUEN_USUARIO = Column(String(64), nullable=False)
    CUEN_PASSWORD = Column(String(64), nullable=False)
    CUEN_TIPO = Column(String(64), nullable=False)
    CUEN_NUMERO_CUENTA = Column(String(10), nullable=False)
    CUEN_SALDO = Column(Numeric(10, 2), nullable=False)
    CUEN_ESTADO = Column(String(64), nullable=False)
    CA_INTERES = Column(Numeric(5, 2), nullable=False)
    CA_LIMITE_RETIROS = Column(Integer, nullable=False)
    CA_MIN_SALDO_REMUNERADO = Column(Numeric(10, 2), nullable=False)
    
    # Relación
    cuenta = relationship("Cuenta", back_populates="cuenta_ahorro")

class CuentaCorriente(Base):
    __tablename__ = "CUENTA_CORRIENTE"
    
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), primary_key=True)
    PER_ID = Column(Integer)
    CLI_ID = Column(Integer, nullable=False)
    CUEN_USUARIO = Column(String(64), nullable=False)
    CUEN_PASSWORD = Column(String(64), nullable=False)
    CUEN_TIPO = Column(String(64), nullable=False)
    CUEN_NUMERO_CUENTA = Column(String(10), nullable=False)
    CUEN_SALDO = Column(Numeric(10, 2), nullable=False)
    CUEN_ESTADO = Column(String(64), nullable=False)
    CC_LIMITE_DESCUBIERTO = Column(Numeric(10, 2), nullable=False)
    CC_COMISION_MANTENIMIENTO = Column(Numeric(10, 2), nullable=False)
    CC_NUM_CHEQUES = Column(Integer, nullable=False)
    
    # Relación
    cuenta = relationship("Cuenta", back_populates="cuenta_corriente")

class Cajero(Base):
    __tablename__ = "CAJERO"
    
    CAJ_ID = Column(Integer, primary_key=True, index=True)
    CAJ_UBICACION = Column(String(100), nullable=False)
    CAJ_ESTADO = Column(String(20), nullable=False)
    CAJ_TIPO = Column(String(30), nullable=False)
    CAJ_SUCURSAL = Column(String(50), nullable=False)
    
    # Relaciones
    transacciones = relationship("Transaccion", back_populates="cajero")

class Transaccion(Base):
    __tablename__ = "TRANSACCION"
    
    TRAN_ID = Column(Integer, primary_key=True, index=True)
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), nullable=False)
    CAJ_ID = Column(Integer, ForeignKey("CAJERO.CAJ_ID"), nullable=False)
    
    # Relaciones
    cuenta = relationship("Cuenta", back_populates="transacciones")
    cajero = relationship("Cajero", back_populates="transacciones")
    retiro = relationship("Retiro", back_populates="transaccion")
    consulta = relationship("Consulta", back_populates="transaccion")
    deposito = relationship("Deposito", back_populates="transaccion")
    transferencia = relationship("Transferencia", back_populates="transaccion")
    pago_servicio = relationship("PagoServicio", back_populates="transaccion")

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
    
    # Relaciones
    transaccion = relationship("Transaccion", back_populates="retiro")
    retiro_con_tarjeta = relationship("RetiroConTarjeta", back_populates="retiro")
    retiro_sin_tarjeta = relationship("RetiroSinTarjeta", back_populates="retiro")

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
    
    # Relación
    retiro = relationship("Retiro", back_populates="retiro_con_tarjeta")

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
    RETS_CODIGO = Column(String(8), nullable=False)
    RETS_TELEFONO_ASOCIADO = Column(String(10), nullable=False)
    RETS_ESTADO_CODIGO = Column(String(64), nullable=False)
    
    # Relación
    retiro = relationship("Retiro", back_populates="retiro_sin_tarjeta")

class Tarjeta(Base):
    __tablename__ = "TARJETA"
    
    TAR_ID = Column(Integer, primary_key=True, index=True)
    CUEN_ID = Column(Integer, ForeignKey("CUENTA.CUEN_ID"), nullable=False)
    CUE_CUEN_ID = Column(Integer, nullable=False)
    TAR_NUMERO_TARJETA = Column(String(16), nullable=False, unique=True)
    TAR_FECHA_EMISION = Column(DateTime, nullable=False)
    TAR_FECHA_EXPIRACION = Column(DateTime, nullable=False)
    TAR_ESTADO_TARJETA = Column(String(64), nullable=False)
    TAR_CVV = Column(String(3), nullable=False)
    TAR_TIPO = Column(String(64), nullable=False)
    TAR_PIN = Column(String(4), nullable=False)
    
    # Relaciones
    cuenta = relationship("Cuenta", back_populates="tarjetas")

class Consulta(Base):
    __tablename__ = "CONSULTA"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    CONS_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    CONS_FECHA_HORA = Column(DateTime, nullable=False)
    CONS_COMISION = Column(Numeric(10, 2), nullable=False)
    CONS_TIPO = Column(String(100), nullable=False)
    CONS_RESULTADOS = Column(Text, nullable=False)
    
    # Relación
    transaccion = relationship("Transaccion", back_populates="consulta")

class Deposito(Base):
    __tablename__ = "DEPOSITOS"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    DEP_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    DEP_FECHA = Column(DateTime, nullable=False)
    DEP_MONTO = Column(Numeric(10, 2), nullable=False)
    DEP_CUENTA_DEST = Column(String(20), nullable=False)
    DEP_CANAL = Column(String(20), nullable=False)
    DEP_REFERENCIA = Column(String(30), nullable=False)
    DEP_ESTADO = Column(String(20), nullable=False)
    
    # Relación
    transaccion = relationship("Transaccion", back_populates="deposito")

class Transferencia(Base):
    __tablename__ = "TRANSFERENCIA"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    TRANS_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    TRANS_FECHA = Column(DateTime, nullable=False)
    TRANS_MONTO = Column(Numeric(10, 2), nullable=False)
    TRANS_ORIGEN = Column(String(20), nullable=False)
    TRANS_DESTINO = Column(String(20), nullable=False)
    TRANS_CANAL = Column(String(20), nullable=False)
    TRANS_ESTADO = Column(String(20), nullable=False)
    
    # Relación
    transaccion = relationship("Transaccion", back_populates="transferencia")

class PagoServicio(Base):
    __tablename__ = "PAGO_SERVICIOS"
    
    TRAN_ID = Column(Integer, ForeignKey("TRANSACCION.TRAN_ID"), primary_key=True)
    PS_ID = Column(Integer, primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CAJ_ID = Column(Integer, nullable=False)
    PS_TIPO_SERVICIO = Column(String(100), nullable=False)
    PS_PROVEEDOR = Column(String(100), nullable=False)
    PS_REFERENCIA = Column(String(100), nullable=False)
    PS_MONTO = Column(Numeric(10, 2), nullable=False)
    PS_FECHA_HORA = Column(DateTime, nullable=False)
    PS_COMISION = Column(Numeric(10, 2), nullable=False)
    PS_RESULTADO_CODIGO = Column(String(10), nullable=False)
    PS_ESTADO = Column(String(20), nullable=False)
    PS_COMPROBANTE = Column(Text, nullable=False)
    
    # Relación
    transaccion = relationship("Transaccion", back_populates="pago_servicio")

class BoucherCabecera(Base):
    __tablename__ = "BOUCHER_CABECERA"
    
    BAN_AID = Column(String(14), primary_key=True)
    BAN_NOMBRE = Column(String(64), nullable=False)
    BAN_DIRECCION = Column(String(64), nullable=False)
    BAN_RUC = Column(String(13), nullable=False)
    BAN_MENSAJE = Column(String(300), nullable=False)
    
    # Relaciones
    boucher_cuerpo = relationship("BoucherCuerpo", back_populates="cabecera")

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
    BOUC_COSTO = Column(Numeric(10, 2), nullable=False)
    BOUC_TOTALDEBITADO = Column(Numeric(10, 2), nullable=False)
    
    # Relación
    cabecera = relationship("BoucherCabecera", back_populates="boucher_cuerpo")

class TarjetaCredito(Base):
    __tablename__ = "TARJETA_CREDITO"
    
    TAR_ID = Column(Integer, ForeignKey("TARJETA.TAR_ID"), primary_key=True)
    CUEN_ID = Column(Integer, nullable=False)
    CUE_CUEN_ID = Column(Integer)
    TAR_NUMERO_TARJETA = Column(String(16), nullable=False)
    TAR_FECHA_EMISION = Column(DateTime, nullable=False)
    TAR_FECHA_EXPIRACION = Column(DateTime, nullable=False)
    TAR_ESTADO_TARJETA = Column(String(64), nullable=False)
    TAR_CVV = Column(String(3), nullable=False)
    TAR_TIPO = Column(String(64), nullable=False)
    TAR_PIN = Column(String(4), nullable=False)
    TC_LIMITE_CREDITO = Column(Numeric(10, 2), nullable=False)
    TC_TASA_INTERES = Column(Numeric(5, 2), nullable=False)
    TC_CARGO_ANUAL = Column(Numeric(10, 2), nullable=False)
    TC_FECHA_CORTE = Column(DateTime, nullable=False)
    TC_FECHA_VENCIMIENTO = Column(DateTime, nullable=False)
    TC_MOROSIDAD = Column(Boolean, nullable=False)
    
    # Relación
    tarjeta = relationship("Tarjeta")

class TarjetaDebito(Base):
    __tablename__ = "TARJETA_DEBITO"
    
    TAR_ID = Column(Integer, ForeignKey("TARJETA.TAR_ID"), primary_key=True)
    TAR_CUEN_ID = Column(Integer, nullable=False)
    CUE_CUEN_ID = Column(Integer)
    TAR_NUMERO_TARJETA = Column(String(16), nullable=False)
    TAR_FECHA_EMISION = Column(DateTime, nullable=False)
    TAR_FECHA_EXPIRACION = Column(DateTime, nullable=False)
    TAR_ESTADO_TARJETA = Column(String(64), nullable=False)
    TAR_CVV = Column(String(3), nullable=False)
    TAR_TIPO = Column(String(64), nullable=False)
    TAR_PIN = Column(String(4), nullable=False)
    CUEN_ID = Column(Integer, nullable=False)
    TD_PIN_HASH = Column(String(255), nullable=False)
    TD_LIMITE_RETIRO_DIARIO = Column(Numeric(10, 2), nullable=False)
    TD_COMISION_SOBREGIRO = Column(Numeric(10, 2), nullable=False)
    
    # Relación
    tarjeta = relationship("Tarjeta")

class Condiciones(Base):
    __tablename__ = "CONDICIONES"
    
    COND_ID = Column(Integer, primary_key=True)
    TRAN_ID = Column(Integer, nullable=False)
    RET_ID = Column(Integer, nullable=False)
    COND_DESCRIPCION = Column(String(200), nullable=False)
    COND_TIEMPO_INICIO = Column(DateTime, nullable=False)
    COND_TIEMPO_FIN = Column(DateTime, nullable=False)
    COND_INTENTOS = Column(Integer, nullable=False)
    COND_MONTO = Column(Integer, nullable=False)
    COND_ESTADO = Column(String(20), nullable=False)
