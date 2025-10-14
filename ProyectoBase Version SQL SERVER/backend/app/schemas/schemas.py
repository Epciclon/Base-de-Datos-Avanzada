from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Schemas para Persona
class PersonaBase(BaseModel):
    PER_NOMBRES: str
    PER_APELLIDOS: str
    PER_FECHA_NACIMIENTO: datetime
    PER_GENERO: str
    PER_TELEFONO: str
    PER_CORREO: EmailStr
    PER_DIRECCION: str
    PER_TIPO: str

class PersonaCreate(PersonaBase):
    pass

class PersonaResponse(PersonaBase):
    PER_ID: int
    
    class Config:
        from_attributes = True

# Schemas para Persona Natural
class PersonaNaturalBase(PersonaBase):
    PN_IDENTIFICACION: str
    PN_ESTADO_CIVIL: str
    PN_PROFESION: str

class PersonaNaturalCreate(PersonaNaturalBase):
    pass

class PersonaNaturalResponse(PersonaNaturalBase):
    PER_ID: int
    
    class Config:
        from_attributes = True

# Schemas para Cliente
class ClienteBase(BaseModel):
    PER_NOMBRES: str
    PER_APELLIDOS: str
    PER_FECHA_NACIMIENTO: datetime
    PER_GENERO: str
    PER_TELEFONO: str
    PER_CORREO: EmailStr
    PER_DIRECCION: str
    PER_TIPO: str
    CLI_ESTADO: str = "ACTIVO"

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
    PER_ID: int
    CLI_ID: int
    CLI_FECHA_INGRESP: datetime
    
    class Config:
        from_attributes = True

# Schemas para Cuenta
class CuentaBase(BaseModel):
    CUEN_USUARIO: str
    CUEN_TIPO: str  # AHORRO, CORRIENTE
    CUEN_SALDO: Decimal = Decimal('0.00')
    CUEN_ESTADO: str = "ACTIVA"

class CuentaCreate(CuentaBase):
    CUEN_PASSWORD: str
    
    @validator('CUEN_TIPO')
    def validate_tipo_cuenta(cls, v):
        if v not in ['AHORRO', 'CORRIENTE']:
            raise ValueError('Tipo de cuenta debe ser AHORRO o CORRIENTE')
        return v

class CuentaResponse(CuentaBase):
    CUEN_ID: int
    PER_ID: int
    CLI_ID: int
    CUEN_NUMERO_CUENTA: str
    
    class Config:
        from_attributes = True

# Schemas para Cuenta Ahorro
class CuentaAhorroCreate(CuentaCreate):
    CA_INTERES: Decimal = Decimal('2.5')
    CA_LIMITE_RETIROS: int = 3
    CA_MIN_SALDO_REMUNERADO: Decimal = Decimal('100.00')

# Schemas para Cuenta Corriente
class CuentaCorrienteCreate(CuentaCreate):
    CC_LIMITE_DESCUBIERTO: Decimal = Decimal('500.00')
    CC_COMISION_MANTENIMIENTO: Decimal = Decimal('5.00')
    CC_NUM_CHEQUES: int = 20

# Schemas para Tarjeta
class TarjetaBase(BaseModel):
    TAR_TIPO: str  # DEBITO, CREDITO
    TAR_ESTADO_TARJETA: str = "ACTIVA"

class TarjetaCreate(TarjetaBase):
    CUEN_ID: int
    TAR_PIN: str  # Requerido para ambos tipos de tarjeta
    
    @validator('TAR_TIPO')
    def validate_tipo_tarjeta(cls, v):
        if v not in ['DEBITO', 'CREDITO']:
            raise ValueError('Tipo de tarjeta debe ser DEBITO o CREDITO')
        return v
    
    @validator('TAR_PIN')
    def validate_pin(cls, v):
        if len(v) != 4 or not v.isdigit():
            raise ValueError('PIN debe tener exactamente 4 dígitos')
        return v

class TarjetaResponse(TarjetaBase):
    TAR_ID: int
    CUEN_ID: int
    TAR_NUMERO_TARJETA: str
    TAR_FECHA_EMISION: datetime
    TAR_FECHA_EXPIRACION: datetime
    TAR_CVV: str
    
    class Config:
        from_attributes = True

# Schemas para Cajero
class CajeroBase(BaseModel):
    CAJ_UBICACION: str
    CAJ_ESTADO: str = "ACTIVO"
    CAJ_TIPO: str
    CAJ_SUCURSAL: str

class CajeroCreate(CajeroBase):
    pass

class CajeroResponse(CajeroBase):
    CAJ_ID: int
    
    class Config:
        from_attributes = True

# Schemas para Retiro
class RetiroCreate(BaseModel):
    CUEN_ID: int
    CAJ_ID: int
    RET_MONTO: float
    tipo_retiro: str  # "CON_TARJETA" o "SIN_TARJETA"
    
    # Para retiro con tarjeta
    TAR_NUMERO_TARJETA: Optional[str] = None
    IMPRIMIR_BOUCHER: Optional[str] = "SI"  # "SI" o "NO"
    
    # Para retiro sin tarjeta
    telefono: Optional[str] = None
    codigo_retiro: Optional[str] = None

class RetiroResponse(BaseModel):
    TRAN_ID: int
    RET_ID: int
    RET_FECHA: datetime
    RET_MONTO: int
    RET_NUMERO_TRAN: str
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
    CUEN_ID: int
    CAJ_ID: int
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
