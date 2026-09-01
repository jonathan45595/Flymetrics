from sqlalchemy import Column, Integer, String, Numeric, Date, Time, DateTime, Boolean, Enum, ForeignKey, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.infrastructure.database.session import Base
import enum
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class AuditMixin:
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    deleted_at = Column(TIMESTAMP, nullable=True)
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

class MetodoPagoEnum(str, enum.Enum):
    Efectivo = "Efectivo"
    Transferencia = "Transferencia"
    Tarjeta = "Tarjeta"
    Convenio = "Convenio"
    Pendiente = "Pendiente"

class TipoTurnoEnum(str, enum.Enum):
    Asesoria = "Asesoría"
    Mantenimiento = "Mantenimiento"
    Fumigacion = "Fumigación"
    Monitoreo = "Monitoreo"

class UsuarioModel(Base, AuditMixin):
    __tablename__ = "tabla_usuarios"
    
    id_usuarios = Column(Integer, primary_key=True, autoincrement=True)
    rol = Column(String(50), nullable=False)  # 'cliente', 'tecnico', 'administrador'
    email = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    fecha_de_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relaciones
    cliente = relationship("ClienteModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    tecnico = relationship("TecnicoModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    notificaciones = relationship("NotificacionModel", back_populates="usuario", cascade="all, delete-orphan")


class ClienteModel(Base, AuditMixin):
    __tablename__ = "tabla_clientes"
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="SET NULL"), nullable=True)
    nombre = Column(String(150), nullable=False)
    apellido_1 = Column(String(150), nullable=True, default="")
    apellido_2 = Column(String(150), nullable=True, default="")
    telefono = Column(String(20), nullable=True)
    numero_documento = Column(String(20), nullable=True)
    ciudad_expedicion = Column(String(50), nullable=True)
    fecha_expedicion = Column(String(30), nullable=True)
    fecha_nacimiento = Column(String(30), nullable=True)
    codigo_verificacion = Column(String(10), nullable=True)
    verificado = Column(Boolean, default=False)
    link_alegra = Column(Text, nullable=True)
    
    # Relaciones
    usuario = relationship("UsuarioModel", back_populates="cliente")
    fincas = relationship("FincaModel", back_populates="cliente", cascade="all, delete-orphan")


class TecnicoModel(Base, AuditMixin):
    __tablename__ = "tecnicos"
    
    id_tecnico = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="SET NULL"), nullable=True)
    nombre = Column(String(150), nullable=False)
    apellido_1 = Column(String(150), nullable=True, default="")
    apellido_2 = Column(String(150), nullable=True, default="")
    certificacion = Column(String(50), nullable=True)
    estado = Column(String(20), default="disponible")  # 'disponible', 'ocupado', 'mantenimiento'
    telefono = Column(String(20), nullable=True)
    servicios_capacitados = Column(String(255), default="1,2,3")
    
    # Relaciones
    usuario = relationship("UsuarioModel", back_populates="tecnico")
    turnos = relationship("AgendaModel", back_populates="tecnico")


class FincaModel(Base, AuditMixin):
    __tablename__ = "tabla_fincas"
    
    id_finca = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey("tabla_clientes.id_cliente", ondelete="CASCADE"), nullable=False)
    nombre_finca = Column(String(50), nullable=False)
    ubicacion_municipio = Column(String(50), nullable=True)
    departamento = Column(String(50), nullable=True)
    hectareas = Column(Numeric(10, 2), nullable=True)
    latitud = Column(Numeric(10, 8), nullable=True)
    longitud = Column(Numeric(11, 8), nullable=True)
    
    # Relaciones
    cliente = relationship("ClienteModel", back_populates="fincas")
    turnos = relationship("AgendaModel", back_populates="finca", cascade="all, delete-orphan")


class ServicioModel(Base, AuditMixin):
    __tablename__ = "tabla_servicios"
    
    id_servicio = Column(Integer, primary_key=True, autoincrement=True)
    nombre_servicio = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_base_m2 = Column(Numeric(10, 4), nullable=False)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    turnos = relationship("AgendaModel", back_populates="servicio", passive_deletes=True)


class AgendaModel(Base, AuditMixin):
    __tablename__ = "tabla_agenda"
    
    id_turno = Column(Integer, primary_key=True, autoincrement=True)
    id_finca = Column(Integer, ForeignKey("tabla_fincas.id_finca", ondelete="CASCADE"), nullable=True)
    id_servicio = Column(Integer, ForeignKey("tabla_servicios.id_servicio", ondelete="CASCADE"), nullable=False)
    id_drone = Column(Integer, ForeignKey("tabla_drones.id_drone", ondelete="SET NULL"), nullable=True)
    id_tecnico = Column(Integer, ForeignKey("tecnicos.id_tecnico", ondelete="SET NULL"), nullable=True)
    fecha_de_turno = Column(Date, nullable=False)
    hora_inicio_estimada = Column(Time, nullable=False)
    hora_fin_estimada = Column(Time, nullable=True)
    tipo_turno = Column(Enum(TipoTurnoEnum), default=TipoTurnoEnum.Fumigacion)
    estado = Column(String(30), nullable=True)  # 'Pendiente', 'Confirmado', 'En Proceso', 'Hecho', 'Cancelado', 'Rechazado'
    tarifa = Column(Numeric(10, 2), nullable=True)
    costo_logistico = Column(Numeric(10, 2), default=0.00)
    cel = Column(String(20), nullable=True)
    observaciones_servicio = Column(Text, nullable=True)
    hora_inicio_real = Column(Time, nullable=True)
    hora_fin_real = Column(Time, nullable=True)
    retraso_justificacion = Column(Text, nullable=True)
    motivo_reagendamiento = Column(Text, nullable=True)
    
    # Relaciones
    finca = relationship("FincaModel", back_populates="turnos")
    servicio = relationship("ServicioModel", back_populates="turnos")
    drone = relationship("DroneModel", back_populates="turnos")
    tecnico = relationship("TecnicoModel", back_populates="turnos")
    reporte_vuelo = relationship("ReporteVueloModel", back_populates="turno", uselist=False, cascade="all, delete-orphan")
    entregables = relationship("EntregableModel", back_populates="turno", cascade="all, delete-orphan")
    pago = relationship("PagoModel", back_populates="turno", uselist=False, cascade="all, delete-orphan")


class ReporteVueloModel(Base, AuditMixin):
    __tablename__ = "tabla_reportes_vuelo"
    
    id_reporte = Column(Integer, primary_key=True, autoincrement=True)
    id_turno = Column(Integer, ForeignKey("tabla_agenda.id_turno", ondelete="CASCADE"), unique=True, nullable=False)
    insumos_litros_aplicados = Column(Numeric(8, 2), nullable=False)
    agua_litros = Column(Numeric(8, 2), nullable=False)
    baterias_utilizadas = Column(Integer, nullable=False)
    cumple_rac100 = Column(Integer, default=0)  # 1 = Sí, 0 = No
    observaciones_campo = Column(Text, nullable=True)
    requerimientos_vuelo = Column(Text, nullable=True)
    notas_tecnicas = Column(Text, nullable=True)
    recomendaciones_agronomicas = Column(Text, nullable=True)
    url_entregable_drive = Column(String(500), nullable=True)
    
    # Relaciones
    turno = relationship("AgendaModel", back_populates="reporte_vuelo")


class DroneModel(Base, AuditMixin):
    __tablename__ = "tabla_drones"
    
    id_drone = Column(Integer, primary_key=True, autoincrement=True)
    modelo = Column(String(50), nullable=False)
    estado = Column(String(30), nullable=True)  # 'disponible', 'en_vuelo', 'mantenimiento'
    tipo = Column(String(50), nullable=True)  # 'aspersion', 'fotogrametria'
    numero_serie = Column(String(100), nullable=True)
    ultima_revision = Column(String(50), nullable=True)
    horas_vuelo = Column(Integer, default=0)
    id_tecnico_asignado = Column(Integer, ForeignKey("tecnicos.id_tecnico", ondelete="SET NULL"), nullable=True)
    
    # Relaciones
    turnos = relationship("AgendaModel", back_populates="drone")
    mantenimientos = relationship("MantenimientoModel", back_populates="drone", cascade="all, delete-orphan")
    tecnico_asignado = relationship("TecnicoModel", foreign_keys=[id_tecnico_asignado])


class MantenimientoModel(Base, AuditMixin):
    __tablename__ = "tabla_mantenimientos_flota"
    
    id_mantenimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_drone = Column(Integer, ForeignKey("tabla_drones.id_drone", ondelete="CASCADE"), nullable=False)
    tipo_mantenimiento = Column(String(50), nullable=False)  # 'Preventivo', 'Correctivo'
    descripcion_falla = Column(Text, nullable=False)
    fecha_ingreso = Column(DateTime, nullable=False)
    fecha_salida = Column(DateTime, nullable=True)
    costo_mantenimiento = Column(Numeric(12, 2), default=0.00)
    responsable_tecnico = Column(String(100), nullable=True)
    
    # Relaciones
    drone = relationship("DroneModel", back_populates="mantenimientos")


class EntregableModel(Base, AuditMixin):
    __tablename__ = "tabla_entregables"
    
    id_entregable = Column(Integer, primary_key=True, autoincrement=True)
    id_turno = Column(Integer, ForeignKey("tabla_agenda.id_turno", ondelete="CASCADE"), nullable=False)
    tipo_archivo = Column(String(50), nullable=False)  # 'ortofoto', 'ndvi', 'reporte_pdf', 'cotizacion', 'factura'
    url_archivo = Column(String(255), nullable=False)
    nombre_archivo = Column(String(150), nullable=True)
    fecha_subida = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relaciones
    turno = relationship("AgendaModel", back_populates="entregables")


class PagoModel(Base, AuditMixin):
    __tablename__ = "tabla_pagos"
    
    id_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_turno = Column(Integer, ForeignKey("tabla_agenda.id_turno", ondelete="CASCADE"), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_pago = Column(TIMESTAMP, server_default=func.current_timestamp())
    metodo_pago = Column(Enum(MetodoPagoEnum), default=MetodoPagoEnum.Pendiente)
    referencia_transaccion = Column(String(100), nullable=True)
    url_comprobante = Column(String(255), nullable=True)
    url_cotizacion = Column(String(255), nullable=True)
    estado_pago = Column(String(30), default="Pendiente")  # 'Pendiente', 'Enviado', 'Aprobado', 'Rechazado'
    
    # Relaciones
    turno = relationship("AgendaModel", back_populates="pago")


class NotificacionModel(Base, AuditMixin):
    __tablename__ = "tabla_notificaciones"
    
    id_notificacion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="CASCADE"), nullable=False)
    titulo = Column(String(100), nullable=False)
    mensaje = Column(Text, nullable=False)
    leido = Column(Boolean, default=False)
    fecha_envio = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relaciones
    usuario = relationship("UsuarioModel", back_populates="notificaciones")


class PQRModel(Base, AuditMixin):
    __tablename__ = "tabla_pqrs"
    
    id_pqr = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="CASCADE"), nullable=False)
    tipo = Column(String(50), nullable=False)  # 'Petición', 'Queja', 'Reclamo', 'Soporte'
    asunto = Column(String(150), nullable=False)
    mensaje = Column(Text, nullable=False)
    estado = Column(String(30), default="Abierto")  # 'Abierto', 'En Proceso', 'Cerrado'
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relaciones
    usuario = relationship("UsuarioModel")
    mensajes = relationship("MensajePQRModel", back_populates="pqr", cascade="all, delete-orphan")


class MensajePQRModel(Base, AuditMixin):
    __tablename__ = "tabla_mensajes_pqrs"
    
    id_mensaje_pqr = Column(Integer, primary_key=True, autoincrement=True)
    id_pqr = Column(Integer, ForeignKey("tabla_pqrs.id_pqr", ondelete="CASCADE"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="CASCADE"), nullable=False)
    id_emisor = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="SET NULL"), nullable=True)
    id_receptor = Column(Integer, ForeignKey("tabla_usuarios.id_usuarios", ondelete="SET NULL"), nullable=True)
    mensaje = Column(Text, nullable=False)
    fecha_envio = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relaciones
    pqr = relationship("PQRModel", back_populates="mensajes")
    usuario = relationship("UsuarioModel", foreign_keys=[id_usuario])
    emisor = relationship("UsuarioModel", foreign_keys=[id_emisor])
    receptor = relationship("UsuarioModel", foreign_keys=[id_receptor])


class SolicitudTecnicoModel(Base, AuditMixin):
    __tablename__ = "tabla_solicitudes_tecnico"
    
    id_solicitud = Column(Integer, primary_key=True, autoincrement=True)
    id_tecnico = Column(Integer, ForeignKey("tecnicos.id_tecnico", ondelete="CASCADE"), nullable=False)
    id_turno = Column(Integer, ForeignKey("tabla_agenda.id_turno", ondelete="SET NULL"), nullable=True)
    tipo_solicitud = Column(String(50), nullable=False)  # 'Cancelacion', 'Reprogramacion', 'Viaticos', 'Novedad_Equipo'
    titulo = Column(String(150), nullable=False)
    justificacion = Column(Text, nullable=False)
    estado = Column(String(30), default="Pendiente")  # 'Pendiente', 'Aprobado', 'Rechazado'
    respuesta_admin = Column(Text, nullable=True)
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relaciones
    tecnico = relationship("TecnicoModel")
    turno = relationship("AgendaModel")


class SystemConfigModel(Base, AuditMixin):
    __tablename__ = "tabla_configuracion_sistema"

    id_config = Column(Integer, primary_key=True, autoincrement=True)
    clave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text, nullable=False)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


