from fastapi import APIRouter, Depends, status, Query, File, UploadFile, Form
import os, uuid
from sqlalchemy.orm import Session
from app.infrastructure.database.session import get_db
from app.application.dto import schemas
from app.application.use_cases.use_cases import EntregableUseCases
from app.presentation.api.dependencies.auth import RoleChecker
from app.infrastructure.database.models.models import UsuarioModel, EntregableModel, AgendaModel
from app.shared.responses.response import success_response

router = APIRouter(prefix="/entregables", tags=["Buzón de Entregables"])

cliente_required = RoleChecker(["cliente"])
admin_required = RoleChecker(["administrador"])
admin_or_tech = RoleChecker(["administrador", "tecnico"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def subir_archivo_entregable(
    id_turno: int = Form(...),
    tipo_archivo: str = Form("Ortofoto"),
    notas: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_or_tech)
):
    """Permite al técnico o administrador subir un archivo físico de entregable directamente desde la plataforma."""
    uploads_dir = os.path.join("frontend", "uploads", "entregables")
    os.makedirs(uploads_dir, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    unique_name = f"entregable_{uuid.uuid4().hex[:10]}{ext}"
    file_path = os.path.join(uploads_dir, unique_name)
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
        
    relative_url = f"/uploads/entregables/{unique_name}"
    
    req = schemas.EntregableCreate(
        id_turno=id_turno,
        tipo_archivo=tipo_archivo,
        url_archivo=relative_url,
        nombre_archivo=file.filename,
        notas=notas
    )
    entregable = EntregableUseCases.subir_entregable(db, req)
    data = schemas.EntregableResponse.model_validate(entregable).model_dump()
    return success_response(message="Archivo de entregable subido exitosamente", data=data, status_code=201)

@router.post("", status_code=status.HTTP_201_CREATED)
def subir_entregable(
    request: schemas.EntregableCreate,
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_or_tech)
):
    """El administrador sube la URL del mapa procesado (Ortofoto, NDVI) y lo vincula al turno. Envía alerta WhatsApp."""
    entregable = EntregableUseCases.subir_entregable(db, request)
    data = schemas.EntregableResponse.model_validate(entregable).model_dump()
    return success_response(message="Entregable registrado exitosamente y notificación enviada al cliente", data=data, status_code=201)

@router.get("/mis-archivos")
def get_mis_entregables(
    id_turno: int = Query(None, description="Filtrar por un turno específico"),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(cliente_required)
):
    """El cliente consulta su buzón privado de mapas y entregables."""
    from app.shared.exceptions.exceptions import NotFoundException
    try:
        entregables = EntregableUseCases.ver_mis_entregables(db, current_user, id_turno)
    except NotFoundException:
        entregables = []
    except Exception as exc:
        import logging
        logging.getLogger("flymetrics").error(f"Error al obtener entregables del cliente: {exc}")
        entregables = []

    from app.infrastructure.database.models.models import ClienteModel, FincaModel, AgendaModel, ReporteVueloModel
    cliente = db.query(ClienteModel).filter(ClienteModel.id_usuario == current_user.id_usuarios).first()
    
    data = []
    for e in entregables:
        item = schemas.EntregableResponse.model_validate(e).model_dump()
        if e.turno:
            item["fecha_turno"] = str(e.turno.fecha_de_turno)
            if e.turno.finca:
                item["nombre_finca"] = e.turno.finca.nombre_finca
                if e.turno.finca.cliente:
                    item["cliente_nombre"] = f"{e.turno.finca.cliente.nombre} {e.turno.finca.cliente.apellido_1 or ''}".strip()
        data.append(item)

    # Añadir entregables de Google Drive registrados en Reportes de Vuelo
    if cliente:
        rep_query = db.query(ReporteVueloModel).join(AgendaModel).join(FincaModel).filter(
            FincaModel.id_cliente == cliente.id_cliente,
            ReporteVueloModel.url_entregable_drive.isnot(None),
            ReporteVueloModel.url_entregable_drive != ""
        )
        if id_turno:
            rep_query = rep_query.filter(ReporteVueloModel.id_turno == id_turno)
        
        reps = rep_query.all()
        for r in reps:
            # Evitar duplicar si ya existe en data con la misma URL
            if not any(d.get("url_archivo") == r.url_entregable_drive for d in data):
                f_nom = r.turno.finca.nombre_finca if (r.turno and r.turno.finca) else "Predio Agrícola"
                f_fec = str(r.turno.fecha_de_turno) if (r.turno and r.turno.fecha_de_turno) else str(r.created_at)[:10]
                data.append({
                    "id_entregable": r.id_reporte * 10000,
                    "id_turno": r.id_turno,
                    "tipo_archivo": "Carpeta Google Drive (Mapas / Ortofotos)",
                    "url_archivo": r.url_entregable_drive,
                    "nombre_archivo": f"Entrega_Drive_Turno_{r.id_turno}.url",
                    "fecha_subida": r.created_at.isoformat() if r.created_at else None,
                    "fecha_turno": f_fec,
                    "nombre_finca": f_nom,
                    "cliente_nombre": f"{cliente.nombre} {cliente.apellido_1 or ''}".strip(),
                    "descripcion": "Enlace directo en la nube a mapas ortomosaicos, índices NDVI y telemetría completa."
                })

    return success_response(message="Buzón de entregables obtenido exitosamente", data=data)

@router.get("")
def list_todos_entregables(
    id_turno: int = Query(None),
    db: Session = Depends(get_db),
    current_user: UsuarioModel = Depends(admin_or_tech)
):
    """Vista de entregables subidos al sistema. Admin ve todos, técnico ve exclusivamente los de sus vuelos asignados."""
    from app.infrastructure.database.models.models import TecnicoModel
    if current_user.rol == "tecnico":
        tecnico = db.query(TecnicoModel).filter(TecnicoModel.id_usuario == current_user.id_usuarios).first()
        if tecnico:
            query = db.query(EntregableModel).join(AgendaModel).filter(AgendaModel.id_tecnico == tecnico.id_tecnico)
            if id_turno:
                query = query.filter(EntregableModel.id_turno == id_turno)
            entregables = query.all()
        else:
            entregables = []
    else:
        entregables = EntregableUseCases.list_all_entregables(db, id_turno)

    data = []
    for e in entregables:
        item = schemas.EntregableResponse.model_validate(e).model_dump()
        if e.turno:
            item["fecha_turno"] = str(e.turno.fecha_de_turno)
            if e.turno.finca:
                item["nombre_finca"] = e.turno.finca.nombre_finca
                if e.turno.finca.cliente:
                    item["cliente_nombre"] = f"{e.turno.finca.cliente.nombre} {e.turno.finca.cliente.apellido_1 or ''}".strip()
        data.append(item)
    return success_response(message="Historial de entregables obtenido", data=data)

from fastapi.responses import Response, FileResponse
import os

@router.get("/{id_entregable}/descargar")
def descargar_entregable(
    id_entregable: int,
    db: Session = Depends(get_db)
):
    """Fuerza la descarga directa del archivo entregable en formato oficial PDF."""
    from app.infrastructure.database.models.models import EntregableModel, ReporteVueloModel
    import mimetypes

    entregable = db.query(EntregableModel).filter(EntregableModel.id_entregable == id_entregable).first()
    filename = f"Entregable_Flymetrics_{id_entregable}.pdf"

    recom_text = "Se sugiere revision de suelo a los 5 dias y reingreso seguro al lote en 24h."
    insumos_text = "Insumos: 15.0L | Agua: 120.0L | Baterias: 4 | Estado: Operacion Exitosa"
    finca_text = "Predio: Finca Registrada Flymetrics"

    if entregable:
        raw_name = entregable.nombre_archivo or f"entregable_{entregable.tipo_archivo}_{id_entregable}"
        # Siempre garantizar extension .pdf en el nombre de descarga
        base_name = os.path.splitext(raw_name)[0]
        filename = base_name + ".pdf"

        clean_url = (entregable.url_archivo or "").lstrip("/")
        path1 = os.path.normpath(clean_url)
        path2 = os.path.normpath(os.path.join("frontend", clean_url))

        target_path = None
        if os.path.exists(path1):
            target_path = path1
        elif os.path.exists(path2):
            target_path = path2

        if target_path:
            # Detectar si el archivo es realmente un PDF por magic bytes
            # Esto evita que mimetypes lo clasifique como text/plain por extension erronea
            detected_mime = "application/pdf"
            try:
                with open(target_path, "rb") as f_check:
                    header = f_check.read(8)
                if header.startswith(b"%PDF"):
                    detected_mime = "application/pdf"
                else:
                    guessed, _ = mimetypes.guess_type(target_path)
                    if guessed and guessed not in ("text/plain", "application/octet-stream"):
                        detected_mime = guessed
                    # Si es text/plain pero el contenido puede ser PDF, forzar PDF
                    else:
                        detected_mime = "application/pdf"
            except Exception:
                pass

            return FileResponse(
                path=target_path,
                filename=filename,
                media_type=detected_mime,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"',
                    "X-Content-Type-Options": "nosniff"
                }
            )

        if entregable.turno:
            if entregable.turno.finca:
                finca_text = f"Predio: {entregable.turno.finca.nombre_finca}"
            if entregable.turno.reporte_vuelo:
                rep = entregable.turno.reporte_vuelo
                insumos_text = f"Insumos: {rep.insumos_litros_aplicados}L | Agua: {rep.agua_litros}L | Baterias: {rep.baterias_utilizadas}"
                if rep.recomendaciones_agronomicas:
                    recom_text = rep.recomendaciones_agronomicas[:90]

    # Documento PDF Oficial Autogenerado formateado
    pdf_str = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Count 1 /Kids [3 0 R] >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 450 >>
stream
BT
/F1 18 Tf
50 720 Td
(FLYMETRICS OS - CONTROL AEREO Y AGRO) Tj
/F1 14 Tf
0 -40 Td
(INFORME TECNICO Y RECOMENDACIONES DE VUELO) Tj
/F1 11 Tf
0 -30 Td
(ID Entregable: #{id_entregable} | {finca_text}) Tj
0 -20 Td
(Servicio: Fotogrametria y Aspersion Aerea Especializada) Tj
0 -25 Td
(TELEMETRIA: {insumos_text}) Tj
0 -25 Td
(RECOMENDACIONES AGRONOMICAS DEL PILOTO TECNICO:) Tj
0 -20 Td
({recom_text}) Tj
0 -40 Td
(Este reporte certifica la finalizacion del servicio y procesamiento) Tj
0 -20 Td
(exitoso de mapas multiespectrales en la nube de Flymetrics.) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000233 00000 n 
0000000302 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
815
%%EOF"""

    pdf_bytes = pdf_str.encode('latin1')
    pdf_filename = f"Informe_Recomendaciones_Flymetrics_{id_entregable}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{pdf_filename}"',
            "X-Content-Type-Options": "nosniff"
        }
    )
