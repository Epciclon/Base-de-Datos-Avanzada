from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, Text, Numeric, DECIMAL, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base

class Persona(Base):
    __tablename__ = "persona"
    
    per_id = Column(Integer, primary_key=True, autoincrement=False)
    per_nombres = Column(String(300), nullable=False)
    per_apellidos = Column(String(300), nullable=False)
    per_fecha_nacimiento = Column(Date, nullable=False)
    per_genero = Column(String(64), nullable=False)
    per_telefono = Column(String(10), nullable=False)
    per_correo = Column(String(64), nullable=False)
    per_direccion = Column(String(124), nullable=False)
    per_tipo = Column(String(64), nullable=False)

class PersonaNatural(Base):
    __tablename__ = "persona_natural"
    
    per_id = Column(Integer, ForeignKey("persona.per_id"), primary_key=True)
    per_nombres = Column(String(300), nullable=False)
    per_apellidos = Column(String(300), nullable=False)
    per_fecha_nacimiento = Column(Date, nullable=False)
    per_genero = Column(String(64), nullable=False)
    per_telefono = Column(String(10), nullable=False)
    per_correo = Column(String(64), nullable=False)
    per_direccion = Column(String(124), nullable=False)
    per_tipo = Column(String(64), nullable=False)
    pn_identificacion = Column(String(13), nullable=False)
    pn_estado_civil = Column(String(20), nullable=False)
    pn_profesion = Column(String(100), nullable=False)

class PersonaJuridica(Base):
    __tablename__ = "persona_juridica"
    
    per_id = Column(Integer, ForeignKey("persona.per_id"), primary_key=True)
    per_nombres = Column(String(300), nullable=False)
    per_apellidos = Column(String(300), nullable=False)
    per_fecha_nacimiento = Column(Date, nullable=False)
    per_genero = Column(String(64), nullable=False)
    per_telefono = Column(String(10), nullable=False)
    per_correo = Column(String(64), nullable=False)
    per_direccion = Column(String(124), nullable=False)
    per_tipo = Column(String(64), nullable=False)
    pj_ruc = Column(String(13), nullable=False)
    pj_representante = Column(String(100), nullable=False)
    pj_tipo_entidad = Column(String(50), nullable=False)
    pj_fecha_constitucion = Column(Date, nullable=False)
    pj_actividad = Column(String(200), nullable=False)

class Cliente(Base):
    __tablename__ = "cliente"
    
    per_id = Column(Integer, ForeignKey("persona.per_id"), primary_key=True)
    cli_id = Column(Integer, primary_key=True)
    per_nombres = Column(String(300), nullable=False)
    per_apellidos = Column(String(300), nullable=False)
    per_fecha_nacimiento = Column(Date, nullable=False)
    per_genero = Column(String(64), nullable=False)
    per_telefono = Column(String(10), nullable=False)
    per_correo = Column(String(64), nullable=False)
    per_direccion = Column(String(124), nullable=False)
    per_tipo = Column(String(64), nullable=False)
    cli_fecha_ingresp = Column(Date, nullable=False)
    cli_estado = Column(String(64), nullable=False)

class Cuenta(Base):
    __tablename__ = "cuenta"
    
    cuen_id = Column(Integer, primary_key=True, autoincrement=False)
    per_id = Column(Integer, nullable=False)
    cli_id = Column(Integer, nullable=False)
    cuen_usuario = Column(String(64), nullable=False)
    cuen_password = Column(String(64), nullable=False)
    cuen_tipo = Column(String(64), nullable=False)
    cuen_numero_cuenta = Column(String(10), nullable=False, unique=True)
    cuen_saldo = Column(Numeric, nullable=False)
    cuen_estado = Column(String(64), nullable=False)

class CuentaAhorro(Base):
    __tablename__ = "cuenta_ahorro"

    cuen_id = Column(Integer, ForeignKey("cuenta.cuen_id"), primary_key=True)
    per_id = Column(Integer)
    cli_id = Column(Integer, nullable=False)
    cuen_usuario = Column(String(64), nullable=False)
    cuen_password = Column(String(64), nullable=False)
    cuen_tipo = Column(String(64), nullable=False)
    cuen_numero_cuenta = Column(String(10), nullable=False)
    cuen_saldo = Column(Numeric, nullable=False)
    cuen_estado = Column(String(64), nullable=False)
    ca_interes = Column(Numeric, nullable=False)
    ca_limite_retiros = Column(Integer, nullable=False)
    ca_min_saldo_remunerado = Column(Numeric, nullable=False)

class CuentaCorriente(Base):
    __tablename__ = "cuenta_corriente"
    
    cuen_id = Column(Integer, ForeignKey("cuenta.cuen_id"), primary_key=True)
    per_id = Column(Integer)
    cli_id = Column(Integer, nullable=False)
    cuen_usuario = Column(String(64), nullable=False)
    cuen_password = Column(String(64), nullable=False)
    cuen_tipo = Column(String(64), nullable=False)
    cuen_numero_cuenta = Column(String(10), nullable=False)
    cuen_saldo = Column(Numeric, nullable=False)
    cuen_estado = Column(String(64), nullable=False)
    cc_limite_descubierto = Column(Numeric, nullable=False)
    cc_comision_mantenimiento = Column(Numeric, nullable=False)
    cc_num_cheques = Column(Integer, nullable=False)

class Cajero(Base):
    __tablename__ = "cajero"
    
    caj_id = Column(Integer, primary_key=True, autoincrement=False)
    caj_ubicacion = Column(String(100), nullable=False)
    caj_estado = Column(String(20), nullable=False)
    caj_tipo = Column(String(30), nullable=False)
    caj_sucursal = Column(String(50), nullable=False)

class Transaccion(Base):
    __tablename__ = "transaccion"
    
    tran_id = Column(Integer, primary_key=True, autoincrement=False)
    cuen_id = Column(Integer, ForeignKey("cuenta.cuen_id"), nullable=False)
    caj_id = Column(Integer, ForeignKey("cajero.caj_id"), nullable=False)

class Retiro(Base):
    __tablename__ = "retiro"
    
    tran_id = Column(Integer, ForeignKey("transaccion.tran_id"), primary_key=True)
    ret_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    ret_fecha = Column(DateTime, nullable=False)
    ret_monto = Column(Integer, nullable=False)
    ret_cajero = Column(String(8), nullable=False)
    ret_numero_tran = Column(String(4), nullable=False)

class RetiroConTarjeta(Base):
    __tablename__ = "retiro_contarjeta"

    tran_id = Column(Integer, primary_key=True)
    ret_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    ret_fecha = Column(Date, nullable=False)
    ret_monto = Column(Integer, nullable=False)
    ret_cajero = Column(String(8), nullable=False)
    ret_numero_tran = Column(String(4), nullable=False)
    rett_imprimir = Column(String(2), nullable=False)
    rett_montomax = Column(Integer, nullable=False)

class RetiroSinTarjeta(Base):
    __tablename__ = "retiro_sintarjeta"

    tran_id = Column(Integer, primary_key=True)
    ret_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    ret_fecha = Column(Date, nullable=False)
    ret_monto = Column(Integer, nullable=False)
    ret_cajero = Column(String(8), nullable=False)
    ret_numero_tran = Column(String(4), nullable=False)
    cond_id = Column(Integer, ForeignKey("condiciones.cond_id"), nullable=False)
    rets_codigo = Column(String(8), nullable=False)
    rets_telefono_asociado = Column(String(10), nullable=False)
    rets_estado_codigo = Column(String(64), nullable=False)

class Tarjeta(Base):
    __tablename__ = "tarjeta"
    
    tar_id = Column(Integer, primary_key=True, autoincrement=False)
    cuen_id = Column(Integer, ForeignKey("cuenta.cuen_id"), nullable=False)
    tar_numero_tarjeta = Column(String(16), nullable=False, unique=True)
    tar_fecha_emision = Column(Date, nullable=False)
    tar_fecha_expiracion = Column(Date, nullable=False)
    tar_estado_tarjeta = Column(String(64), nullable=False)
    tar_cvv = Column(String(3), nullable=False)
    tar_tipo = Column(String(64), nullable=False)
    tar_pin = Column(String(4), nullable=False)

class Consulta(Base):
    __tablename__ = "consulta"
    
    tran_id = Column(Integer, ForeignKey("transaccion.tran_id"), primary_key=True)
    cons_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    cons_fecha_hora = Column(Date, nullable=False)
    cons_comision = Column(Numeric, nullable=False)
    cons_tipo = Column(String(100), nullable=False)
    cons_resultados = Column(Text, nullable=False)

class Deposito(Base):
    __tablename__ = "depositos"
    
    tran_id = Column(Integer, ForeignKey("transaccion.tran_id"), primary_key=True)
    dep_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    dep_fecha = Column(Date, nullable=False)
    dep_monto = Column(Numeric, nullable=False)
    dep_cuenta_dest = Column(String(20), nullable=False)
    dep_canal = Column(String(20), nullable=False)
    dep_referencia = Column(String(30), nullable=False)
    dep_estado = Column(String(20), nullable=False)

class Transferencia(Base):
    __tablename__ = "transferencia"
    
    tran_id = Column(Integer, ForeignKey("transaccion.tran_id"), primary_key=True)
    trans_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    trans_fecha = Column(Date, nullable=False)
    trans_monto = Column(Numeric, nullable=False)
    trans_origen = Column(String(20), nullable=False)
    trans_destino = Column(String(20), nullable=False)
    trans_canal = Column(String(20), nullable=False)
    trans_estado = Column(String(20), nullable=False)

class PagoServicio(Base):
    __tablename__ = "pago_servicios"
    
    tran_id = Column(Integer, ForeignKey("transaccion.tran_id"), primary_key=True)
    ps_id = Column(Integer, primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    ps_tipo_servicio = Column(String(100), nullable=False)
    ps_proveedor = Column(String(100), nullable=False)
    ps_referencia = Column(String(100), nullable=False)
    ps_monto = Column(Numeric, nullable=False)
    ps_fecha_hora = Column(Date, nullable=False)
    ps_comision = Column(Numeric, nullable=False)
    ps_resultado_codigo = Column(String(10), nullable=False)
    ps_estado = Column(String(20), nullable=False)
    ps_comprobante = Column(Text, nullable=False)

class BoucherCabecera(Base):
    __tablename__ = "boucher_cabecera"
    
    ban_aid = Column(String(14), primary_key=True)
    ban_nombre = Column(String(64), nullable=False)
    ban_direccion = Column(String(64), nullable=False)
    ban_ruc = Column(String(13), nullable=False)
    ban_mensaje = Column(String(300), nullable=False)

class BoucherCuerpo(Base):
    __tablename__ = "boucher_cuerpo"
    
    bouc_id = Column(Integer, primary_key=True)
    tran_id = Column(Integer, primary_key=True)
    ret_id = Column(Integer, primary_key=True)
    rett_imprimir = Column(String(2), nullable=False)
    rett_montomax = Column(Integer, nullable=False)
    cuen_id = Column(Integer, nullable=False)
    caj_id = Column(Integer, nullable=False)
    ret_fecha = Column(Date, nullable=False)
    ret_monto = Column(Integer, nullable=False)
    ret_cajero = Column(String(8), nullable=False)
    ret_numero_tran = Column(String(4), nullable=False)
    ban_aid = Column(String(14), ForeignKey("boucher_cabecera.ban_aid"), nullable=False)
    bouc_costo = Column(DECIMAL(10, 2), nullable=False)
    bouc_totaldebitado = Column(DECIMAL(10, 2), nullable=False)

class TarjetaCredito(Base):
    __tablename__ = "tarjeta_credito"
    
    tar_id = Column(Integer, ForeignKey("tarjeta.tar_id"), primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    tar_numero_tarjeta = Column(String(16), nullable=False)
    tar_fecha_emision = Column(Date, nullable=False)
    tar_fecha_expiracion = Column(Date, nullable=False)
    tar_estado_tarjeta = Column(String(64), nullable=False)
    tar_cvv = Column(String(3), nullable=False)
    tar_tipo = Column(String(64), nullable=False)
    tar_pin = Column(String(4), nullable=False)
    tc_limite_credito = Column(Numeric, nullable=False)
    tc_tasa_interes = Column(Numeric, nullable=False)
    tc_cargo_anual = Column(Numeric, nullable=False)
    tc_fecha_corte = Column(Date, nullable=False)
    tc_fecha_vencimiento = Column(Date, nullable=False)
    tc_morosidad = Column(Boolean, nullable=False)

class TarjetaDebito(Base):
    __tablename__ = "tarjeta_debito"
    
    tar_id = Column(Integer, ForeignKey("tarjeta.tar_id"), primary_key=True)
    cuen_id = Column(Integer, nullable=False)
    tar_numero_tarjeta = Column(String(16), nullable=False)
    tar_fecha_emision = Column(Date, nullable=False)
    tar_fecha_expiracion = Column(Date, nullable=False)
    tar_estado_tarjeta = Column(String(64), nullable=False)
    tar_cvv = Column(String(3), nullable=False)
    tar_tipo = Column(String(64), nullable=False)
    tar_pin = Column(String(4), nullable=False)
    td_limite_retiro_diario = Column(Numeric, nullable=False)
    td_comision_sobregiro = Column(Numeric, nullable=False)

class Condiciones(Base):
    __tablename__ = "condiciones"
    
    cond_id = Column(Integer, primary_key=True)
    cond_descripcion = Column(String(200), nullable=False)
    cond_horas = Column(Integer, nullable=False)
    cond_intentos = Column(Integer, nullable=False)
    cond_monto = Column(Integer, nullable=False)
    cond_estado = Column(String(20), nullable=False)
