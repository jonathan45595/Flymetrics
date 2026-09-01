from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Optional, List, Any
from datetime import date, time, datetime
from decimal import Decimal
from app.infrastructure.database.models.models import MetodoPagoEnum, TipoTurnoEnum

# ==========================================
# MÓDULO 1 — AUTENTICACIÓN & USUARIOS
# ==========================================

class UsuarioCreate(BaseModel):
    email: EmailStr
    contraseña: str = Field(..., min_length=8, description="Contraseña de mínimo 8 caracteres")
    rol: str = Field(..., description="cliente, tecnico o administrador")
    nombre: Optional[str] = Field(None, max_length=150, description="Nombre completo para el perfil")
    apellido_1: Optional[str] = Field(None, max_length=150, description="Primer apellido")
    apellido_2: Optional[str] = Field(None, max_length=150, description="Segundo apellido")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono")

class UsuarioLogin(BaseModel):
    email: EmailStr
    contraseña: str

class GoogleLoginRequest(BaseModel):
    token: str

class UsuarioResponse(BaseModel):
    id_usuarios: int
    email: EmailStr
    rol: str
    fecha_de_creacion: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UsuarioUpdateRol(BaseModel):
    rol: str = Field(..., description="cliente, tecnico o administrador")

class UsuarioResetPassword(BaseModel):
    nueva_contrasena: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    token: str
    rol: str
    id_usuarios: int
    email: str


# ==========================================
# MÓDULO 2 — CLIENTES
# ==========================================

class ClienteAdminCreate(BaseModel):
    nombre: str = Field(..., max_length=150, description="Nombre completo del cliente")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de WhatsApp o teléfono")
    email: Optional[str] = Field(None, description="Correo electrónico opcional")
    contraseña: Optional[str] = Field(None, description="Contraseña opcional")
    nombre_finca: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=50)
    ubicacion_municipio: Optional[str] = Field(None, max_length=50)
    hectareas: Optional[float] = Field(None)

class ClienteCreate(BaseModel):
    id_usuario: Optional[int] = None
    nombre: str = Field(..., max_length=150)
    apellido_1: Optional[str] = Field("", max_length=150)
    apellido_2: Optional[str] = Field("", max_length=150)
    telefono: Optional[str] = Field(None)

class ClienteVerifyRequest(BaseModel):
    numero_documento: str = Field(..., min_length=7, max_length=20)
    ciudad_expedicion: str = Field(..., min_length=3, max_length=50)
    fecha_expedicion: str = Field(..., min_length=5, max_length=30)

class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    apellido_1: Optional[str] = Field(None, max_length=150)
    apellido_2: Optional[str] = Field(None, max_length=150)
    telefono: Optional[str] = None
    numero_documento: Optional[str] = None
    cedula: Optional[str] = None
    fecha_expedicion: Optional[str] = None
    ciudad_expedicion: Optional[str] = None
    datos_cuenta: Optional[str] = None
    verificado: Optional[bool] = None
    link_alegra: Optional[str] = None
    transfer_password: Optional[str] = Field(None, description="Contraseña requerida si el NIT/Cédula ya pertenecía a otra cuenta para transferirlo")

class ClienteResponse(BaseModel):
    id_cliente: int
    id_usuario: Optional[int]
    nombre: str
    apellido_1: Optional[str] = ""
    apellido_2: Optional[str] = ""
    telefono: Optional[str]
    numero_documento: Optional[str]
    ciudad_expedicion: Optional[str]
    fecha_expedicion: Optional[str]
    fecha_nacimiento: Optional[str] = None
    verificado: bool
    link_alegra: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ClienteAlegraRequest(BaseModel):
    link_alegra: Optional[str] = Field(None, description="Enlace directo a factura o portal de Alegra")


class SolicitudCodigoRequest(BaseModel):
    email: str = Field(..., max_length=100)

class VerificacionCodigoRequest(BaseModel):
    email: str = Field(..., max_length=100)
    codigo: str = Field(..., min_length=4, max_length=10)

class CompletarVerificacionClienteRequest(BaseModel):
    numero_documento: str = Field(..., min_length=5, max_length=20)
    nombre: str = Field(..., min_length=2, max_length=150)
    apellido_1: Optional[str] = Field("", max_length=150)
    fecha_nacimiento: str = Field(..., min_length=6, max_length=30)
    transfer_password: Optional[str] = Field(None, description="Contraseña requerida si el NIT/Cédula pertenecía a otra cuenta para transferirlo")
    transfer_email: Optional[str] = Field(None, description="Correo opcional de la cuenta anterior para autenticar transferencia")



# ==========================================
# MÓDULO 3 — TÉCNICOS
# ==========================================

class TecnicoCreate(BaseModel):
    id_usuario: int
    nombre: str = Field(..., max_length=150)
    apellido_1: Optional[str] = Field("", max_length=150)
    apellido_2: Optional[str] = Field("", max_length=150)
    certificacion: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=20)

class TecnicoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    apellido_1: Optional[str] = Field(None, max_length=150)
    apellido_2: Optional[str] = Field(None, max_length=150)
    certificacion: Optional[str] = Field(None, max_length=50)
    estado: Optional[str] = Field(None, description="disponible, ocupado, mantenimiento")
    telefono: Optional[str] = Field(None, max_length=20)
    servicios_capacitados: Optional[str] = Field(None, max_length=255)

class TecnicoResponse(BaseModel):
    id_tecnico: int
    id_usuario: Optional[int]
    nombre: str
    apellido_1: Optional[str] = ""
    apellido_2: Optional[str] = ""
    certificacion: Optional[str]
    estado: str
    telefono: Optional[str]
    servicios_capacitados: str
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 4 — FINCAS
# ==========================================

class FincaCreate(BaseModel):
    id_cliente: Optional[int] = None
    nombre_finca: str = Field(..., max_length=100)
    ubicacion_municipio: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    hectareas: Optional[Decimal] = Field(Decimal("1.0"), ge=0, description="Hectáreas del predio")
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None

    @field_validator('latitud', 'longitud', mode='before')
    @classmethod
    def empty_gps_to_none(cls, v):
        if v == '' or v is None or str(v).strip().lower() in ['null', 'none', 'undefined', '0', '0.0']:
            return None
        try:
            return Decimal(str(v).strip())
        except Exception:
            return None

    @field_validator('hectareas', mode='before')
    @classmethod
    def parse_hectareas(cls, v):
        if v == '' or v is None:
            return Decimal("1.0")
        try:
            val = Decimal(str(v).strip())
            return val if val > 0 else Decimal("1.0")
        except Exception:
            return Decimal("1.0")


class FincaUpdate(BaseModel):
    nombre_finca: Optional[str] = Field(None, max_length=100)
    ubicacion_municipio: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    hectareas: Optional[Decimal] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None

    @field_validator('latitud', 'longitud', mode='before')
    @classmethod
    def empty_gps_to_none(cls, v):
        if v == '' or v is None or str(v).strip().lower() in ['null', 'none', 'undefined']:
            return None
        try:
            return Decimal(str(v).strip())
        except Exception:
            return None

class FincaResponse(BaseModel):
    id_finca: int
    id_cliente: int
    nombre_finca: str
    ubicacion_municipio: Optional[str] = None
    departamento: Optional[str] = None
    hectareas: Optional[Decimal] = None
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 5 — SERVICIOS & COTIZACIONES
# ==========================================

class ServicioCreate(BaseModel):
    nombre_servicio: str = Field(..., max_length=100)
    descripcion: Optional[str] = None
    precio_base_m2: Optional[Decimal] = Field(Decimal("0.0"), ge=0)
    activo: Optional[bool] = True

class ServicioUpdate(BaseModel):
    nombre_servicio: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    precio_base_m2: Optional[Decimal] = Field(None, ge=0)
    activo: Optional[bool] = None

class ServicioResponse(BaseModel):
    id_servicio: int
    nombre_servicio: str
    descripcion: Optional[str] = None
    precio_base_m2: Decimal
    activo: Optional[bool] = True
    
    model_config = ConfigDict(from_attributes=True)

class CotizacionRequest(BaseModel):
    id_servicio: Optional[int] = None
    id_finca: Optional[int] = None

class CotizacionResponse(BaseModel):
    id_servicio: int
    id_finca: int
    nombre_servicio: str
    nombre_finca: str
    hectareas: Decimal
    precio_base: Decimal
    costo_logistico: Decimal
    precio_total: Decimal
    distancia_km: float
    duracion_estimada_horas: float


# ==========================================
# MÓDULO 6 — AGENDAMIENTO / TURNOS
# ==========================================

class AgendaCreate(BaseModel):
    id_finca: Optional[int] = None
    id_servicio: Optional[int] = None
    fecha_de_turno: Optional[date] = None
    hora_inicio_estimada: Optional[time] = time(8, 0)
    tipo_turno: Optional[Any] = TipoTurnoEnum.Fumigacion
    id_tecnico: Optional[int] = None
    cel: Optional[str] = Field(None, max_length=50)
    observaciones_servicio: Optional[str] = None
    tarifa: Optional[Decimal] = None

    @field_validator('id_finca', 'id_servicio', 'id_tecnico', mode='before')
    @classmethod
    def coerce_id(cls, v):
        if v == '' or v is None or str(v).strip().lower() in ['null', 'undefined']:
            return None
        try:
            return int(v)
        except Exception:
            return None

    @field_validator('fecha_de_turno', mode='before')
    @classmethod
    def parse_fecha(cls, v):
        if not v or v == '' or str(v).strip().lower() in ['null', 'undefined']:
            return date.today()
        if isinstance(v, str):
            try:
                return datetime.strptime(v.split('T')[0], '%Y-%m-%d').date()
            except Exception:
                return date.today()
        return v

    @field_validator('hora_inicio_estimada', mode='before')
    @classmethod
    def parse_hora(cls, v):
        if not v or v == '' or str(v).strip().lower() in ['null', 'undefined']:
            return time(8, 0)
        if isinstance(v, str):
            try:
                parts = v.split(':')
                return time(int(parts[0]), int(parts[1]))
            except Exception:
                return time(8, 0)
        return v

class ReservaRapidaCreate(BaseModel):
    nombre_completo: str = Field(..., min_length=2, max_length=150)
    cedula: str = Field(..., min_length=3, max_length=50)
    telefono: str = Field(..., min_length=5, max_length=20)
    email: Optional[str] = Field(None, max_length=150)
    nombre_finca: str = Field(..., min_length=2, max_length=150)
    departamento: str = Field(..., min_length=2, max_length=100)
    municipio: str = Field(..., min_length=2, max_length=100)
    vereda_corregimiento: str = Field(..., min_length=2, max_length=150)
    direccion_ubicacion: Optional[str] = Field(None, max_length=255)
    hectareas: float = Field(..., gt=0)
    tipo_cultivo: str = Field(..., min_length=2, max_length=100)
    servicio_solicitado: Optional[str] = Field("Fumigación Agrícola", max_length=100)
    id_servicio: Optional[int] = Field(None)
    fecha_deseada: date
    observaciones: Optional[str] = None

class AgendaAsignarRequest(BaseModel):
    id_tecnico: int
    id_drone: Optional[int] = None

class AgendaDecisionRequest(BaseModel):
    decision: bool
    motivo_rechazo: Optional[str] = None

class CheckinRequest(BaseModel):
    latitud_checkin: Optional[Decimal] = None
    longitud_checkin: Optional[Decimal] = None

class CheckoutRequest(BaseModel):
    insumos_litros_aplicados: Decimal = Field(..., ge=0)
    agua_litros: Decimal = Field(..., ge=0)
    baterias_utilizadas: int = Field(..., ge=0)
    cumple_rac100: int = Field(..., ge=0, le=1, description="1 = Sí, 0 = No")
    observaciones_campo: Optional[str] = None
    recomendaciones_agronomicas: Optional[str] = None
    url_entregable_drive: Optional[str] = None
    retraso_justificacion: Optional[str] = None

class AgendaForceEstadoRequest(BaseModel):
    estado: str = Field(..., description="Pendiente, Confirmado, En Proceso, Hecho, Cancelado")
    motivo_admin: Optional[str] = None

class AgendaResponse(BaseModel):
    id_turno: int
    id_finca: Optional[int]
    id_servicio: int
    id_drone: Optional[int]
    id_tecnico: Optional[int]
    fecha_de_turno: date
    hora_inicio_estimada: time
    hora_fin_estimada: Optional[time]
    tipo_turno: TipoTurnoEnum
    estado: Optional[str]
    tarifa: Optional[Decimal]
    costo_logistico: Optional[Decimal]
    cel: Optional[str]
    observaciones_servicio: Optional[str]
    hora_inicio_real: Optional[time]
    hora_fin_real: Optional[time]
    retraso_justificacion: Optional[str]
    motivo_reagendamiento: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 7 — BITÁCORA DEL TÉCNICO & REPORTES
# ==========================================

class ReporteVueloResponse(BaseModel):
    id_reporte: int
    id_turno: int
    insumos_litros_aplicados: Decimal
    agua_litros: Decimal
    baterias_utilizadas: int
    cumple_rac100: int
    observaciones_campo: Optional[str]
    recomendaciones_agronomicas: Optional[str] = None
    url_entregable_drive: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 8 — DRONES & MANTENIMIENTOS
# ==========================================

class DroneCreate(BaseModel):
    modelo: str = Field(..., max_length=50)
    tipo: str = Field(..., max_length=50, description="aspersion, fotogrametria")
    estado: str = Field("disponible", max_length=30)
    numero_serie: Optional[str] = Field(None, max_length=100)
    ultima_revision: Optional[str] = Field(None, max_length=50)
    id_tecnico_asignado: Optional[int] = Field(None, description="ID del técnico/piloto asignado")

class DroneUpdate(BaseModel):
    modelo: Optional[str] = Field(None, max_length=50)
    tipo: Optional[str] = Field(None, max_length=50)
    estado: Optional[str] = Field(None, max_length=30)
    numero_serie: Optional[str] = Field(None, max_length=100)
    ultima_revision: Optional[str] = Field(None, max_length=50)
    horas_vuelo: Optional[int] = Field(None, ge=0)
    id_tecnico_asignado: Optional[int] = Field(None)

class MantenimientoCreate(BaseModel):
    tipo_mantenimiento: str = Field(..., max_length=50)  # 'Preventivo', 'Correctivo'
    descripcion_falla: str
    fecha_ingreso: datetime = Field(default_factory=datetime.utcnow)
    fecha_salida: Optional[datetime] = None
    costo_mantenimiento: Optional[Decimal] = Decimal("0.00")
    responsable_tecnico: Optional[str] = Field(None, max_length=100)

class DroneResponse(BaseModel):
    id_drone: int
    modelo: str
    tipo: Optional[str]
    estado: Optional[str]
    numero_serie: Optional[str]
    ultima_revision: Optional[str]
    horas_vuelo: Optional[int]
    id_tecnico_asignado: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class MantenimientoResponse(BaseModel):
    id_mantenimiento: int
    id_drone: int
    tipo_mantenimiento: str
    descripcion_falla: str
    fecha_ingreso: datetime
    fecha_salida: Optional[datetime]
    costo_mantenimiento: Optional[Decimal]
    responsable_tecnico: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 9 — ENTREGABLES
# ==========================================

class EntregableCreate(BaseModel):
    id_turno: int
    tipo_archivo: str = Field(..., max_length=50)  # 'ortofoto', 'ndvi', 'reporte_pdf'
    url_archivo: str = Field(..., max_length=255)
    nombre_archivo: Optional[str] = Field(None, max_length=150)
    notas: Optional[str] = None

class EntregableResponse(BaseModel):
    id_entregable: int
    id_turno: int
    tipo_archivo: str
    url_archivo: str
    fecha_subida: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 10 — PAGOS
# ==========================================

class PagoCreate(BaseModel):
    id_turno: int
    monto: Decimal = Field(..., gt=0)
    metodo_pago: MetodoPagoEnum = MetodoPagoEnum.Pendiente
    referencia_transaccion: Optional[str] = Field(None, max_length=100)

class PagoResponse(BaseModel):
    id_pago: int
    id_turno: int
    monto: Decimal
    fecha_pago: datetime
    metodo_pago: MetodoPagoEnum
    referencia_transaccion: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 11 — NOTIFICACIONES
# ==========================================

class NotificacionCreate(BaseModel):
    id_usuario: int
    titulo: str = Field(..., max_length=100)
    mensaje: str

class NotificacionResponse(BaseModel):
    id_notificacion: int
    id_usuario: int
    titulo: str
    mensaje: str
    leido: bool
    fecha_envio: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 12 — QUEJAS, RECLAMOS Y SOPORTE (PQRs)
# ==========================================

class PQRCreate(BaseModel):
    tipo: str = Field(..., max_length=50)  # 'Petición', 'Queja', 'Reclamo', 'Soporte'
    asunto: str = Field(..., max_length=150)
    mensaje: Optional[str] = None
    descripcion: Optional[str] = None

class MensajePQRCreate(BaseModel):
    mensaje: str

class MensajePQRResponse(BaseModel):
    id_mensaje_pqr: int
    id_pqr: int
    id_usuario: int
    id_emisor: Optional[int] = None
    id_receptor: Optional[int] = None
    mensaje: str
    contenido: Optional[str] = None
    fecha_envio: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PQRResponse(BaseModel):
    id_pqr: int
    id_usuario: int
    tipo: str
    asunto: str
    mensaje: Optional[str] = ""
    estado: str
    fecha_creacion: datetime
    mensajes: List[MensajePQRResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MÓDULO 13 — SOLICITUDES Y PERMISOS DE TÉCNICOS
# ==========================================

class SolicitudTecnicoCreate(BaseModel):
    id_turno: Optional[int] = None
    tipo_solicitud: str  # 'Cancelacion', 'Reprogramacion', 'Viaticos', 'Novedad_Equipo'
    titulo: str
    justificacion: str

class SolicitudTecnicoResponder(BaseModel):
    estado: str  # 'Aprobado', 'Rechazado'
    respuesta_admin: Optional[str] = None


