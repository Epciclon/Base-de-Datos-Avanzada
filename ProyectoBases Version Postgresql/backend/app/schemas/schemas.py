from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Schemas para Persona
class PersonaBase(BaseModel):
    per_nombres: str
    per_apellidos: str
    per_fecha_nacimiento: datetime
    per_genero: str
    per_telefono: str
    per_correo: EmailStr
    per_direccion: str
    per_tipo: str

class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    per_id: int
    
    class Config:
        from_attributes = True

# Schemas para Persona Natural
class PersonaNaturalBase(PersonaBase):
    pn_identificacion: str
    pn_estado_civil: str
    pn_profesion: str

class PersonaNaturalCreate(PersonaNaturalBase):
    pass

class PersonaNaturalResponse(PersonaNaturalBase):
    per_id: int
    
    class Config:
        from_attributes = True

# Schemas para Cliente
class ClienteBase(BaseModel):
    per_nombres: str
    per_apellidos: str
    per_fecha_nacimiento: datetime
    per_genero: str
    per_telefono: str
    per_correo: EmailStr
    per_direccion: str
    per_tipo: str
    cli_estado: str = "ACTIVO"

class ClienteCreate(ClienteBase):
    # Campos para persona natural
    identificacion: Optional[str] = None
    estado_civil: Optional[str] = None
    profesion: Optional[str] = None
    
    # Campos para persona jurídica
    ruc: Optional[str] = None
    representante_legal: Optional[str] = None
    tipo_entidad: Optional[str] = None
    fecha_constitucion: Optional[datetime] = None
    actividad_economica: Optional[str] = None

class ClienteResponse(ClienteBase):
    per_id: int
    cli_id: int
    cli_fecha_ingresp: datetime
    
    class Config:
        from_attributes = True

# Schemas para Cuenta
class CuentaBase(BaseModel):
    cuen_usuario: str
    cuen_tipo: str  # AHORRO, CORRIENTE
    cuen_saldo: Decimal = Decimal('0.00')
    cuen_estado: str = "ACTIVA"

class CuentaCreate(CuentaBase):
    cuen_password: str
    
    @validator('cuen_tipo')
    def validate_tipo_cuenta(cls, v):
        if v not in ['AHORRO', 'CORRIENTE']:
            raise ValueError('Tipo de cuenta debe ser AHORRO o CORRIENTE')
        return v

class CuentaResponse(CuentaBase):
    cuen_id: int
    per_id: int
    cli_id: int
    cuen_numero_cuenta: str
    
    class Config:
        from_attributes = True

# Schemas para Cuenta Ahorro
class CuentaAhorroCreate(CuentaCreate):
    ca_interes: Decimal = Decimal('2.5')
    ca_limite_retiros: int = 3
    ca_min_saldo_remunerado: Decimal = Decimal('100.00')

# Schemas para Cuenta Corriente
class CuentaCorrienteCreate(CuentaCreate):
    cc_limite_descubierto: Decimal = Decimal('500.00')
    cc_comision_mantenimiento: Decimal = Decimal('5.00')
    cc_num_cheques: int = 20

# Schemas para Tarjeta
class TarjetaBase(BaseModel):
    tar_tipo: str  # DEBITO, CREDITO
    tar_estado_tarjeta: str = "ACTIVA"

class TarjetaCreate(TarjetaBase):
    cuen_id: int
    tar_pin: str  # Requerido para ambos tipos de tarjeta
    
    @validator('tar_tipo')
    def validate_tipo_tarjeta(cls, v):
        if v not in ['DEBITO', 'CREDITO']:
            raise ValueError('Tipo de tarjeta debe ser DEBITO o CREDITO')
        return v
    
    @validator('tar_pin')
    def validate_pin(cls, v):
        if len(v) != 4 or not v.isdigit():
            raise ValueError('PIN debe tener exactamente 4 dígitos')
        return v

class TarjetaResponse(TarjetaBase):
    tar_id: int
    cuen_id: int
    tar_numero_tarjeta: str
    tar_fecha_emision: datetime
    tar_fecha_expiracion: datetime
    tar_cvv: str
    
    class Config:
        from_attributes = True

# Schemas para Cajero
class CajeroBase(BaseModel):
    caj_ubicacion: str
    caj_estado: str = "ACTIVO"
    caj_tipo: str
    caj_sucursal: str

class CajeroCreate(CajeroBase):
    pass

class CajeroResponse(CajeroBase):
    caj_id: int
    
    class Config:
        from_attributes = True

# Schemas para Retiro
class RetiroCreate(BaseModel):
    cuen_id: int
    caj_id: int
    ret_monto: float
    tipo_retiro: str  # "CON_TARJETA" o "SIN_TARJETA"
    
    # Para retiro con tarjeta
    tar_numero_tarjeta: Optional[str] = None
    imprimir_boucher: Optional[str] = "SI"  # "SI" o "NO"
    
    # Para retiro sin tarjeta
    telefono: Optional[str] = None
    codigo_retiro: Optional[str] = None

class RetiroResponse(BaseModel):
    tran_id: int
    ret_id: int
    ret_fecha: datetime
    ret_monto: int
    ret_numero_tran: str
    mensaje: str
    comprobante: Optional[dict] = None
    
    class Config:
        from_attributes = True

# Schemas para autenticación
class LoginRequest(BaseModel):
    usuario: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: str
    cuenta_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Schemas para consultas
class ConsultaSaldoResponse(BaseModel):
    numero_cuenta: str
    saldo: Decimal
    tipo_cuenta: str
    estado: str
    fecha_consulta: datetime
    
    class Config:
        from_attributes = True

class MovimientoResponse(BaseModel):
    fecha: datetime
    tipo: str
    monto: Decimal
    descripcion: str
    saldo_anterior: Decimal
    saldo_actual: Decimal
    
    class Config:
        from_attributes = True

# Schemas de respuesta general
class MessageResponse(BaseModel):
    mensaje: str
    detalle: Optional[str] = None

# Schemas para Retiro Sin Tarjeta
class CodigoRetiroRequest(BaseModel):
    cuen_id: int
    caj_id: int
    telefono: str
    monto: float
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError('El teléfono debe tener 10 dígitos')
        return v
    
    @validator('monto')
    def validar_monto(cls, v):
        if v < 10 or v > 300:
            raise ValueError('El monto debe estar entre $10 y $300')
        if v % 5 != 0:
            raise ValueError('El monto debe ser múltiplo de $5')
        return v

class CodigoRetiroResponse(BaseModel):
    codigo: str
    fecha_expiracion: datetime
    monto: float
    mensaje: str
    
    class Config:
        from_attributes = True

class ValidarCodigoRequest(BaseModel):
    codigo: str
    telefono: str
    
    @validator('codigo')
    def validar_codigo(cls, v):
        if len(v) != 6 or not v.isdigit():
            raise ValueError('El código debe tener 6 dígitos')
        return v
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError('El teléfono debe tener 10 dígitos')
        return v
