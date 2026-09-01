from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.infrastructure.config.settings import settings
from app.presentation.api.middleware.error_handler import setup_error_handlers

# Importar routers
from app.presentation.api.routers import (
    auth, clientes, tecnicos, fincas, servicios, agenda, bitacora, drones, entregables, pagos, notificaciones, webhook, usuarios, solicitudes, pqrs, contacto
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API REST profesional para la gestión de flota de drones, agendas de vuelo y bitácoras de Flymetrics S.A.S.",
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi.middleware.gzip import GZipMiddleware

# Configurar compresión Gzip para acelerar transferencias en redes móviles y ngrok
app.add_middleware(GZipMiddleware, minimum_size=500)

# Configurar CORS para acceso local y frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar manejadores de error globales (excepciones de negocio y Pydantic)
setup_error_handlers(app)

# Crear sub-router principal de la API con versión v1
from fastapi import APIRouter
api_router = APIRouter(prefix="/api/v1")

# Registrar routers modulares
api_router.include_router(auth.router)
api_router.include_router(clientes.router)
api_router.include_router(tecnicos.router)
api_router.include_router(fincas.router)
api_router.include_router(servicios.router)
api_router.include_router(agenda.router)
api_router.include_router(agenda.admin_router)
api_router.include_router(bitacora.router)
api_router.include_router(drones.router)
api_router.include_router(entregables.router)
api_router.include_router(pagos.router)
api_router.include_router(notificaciones.router)
api_router.include_router(webhook.router)
api_router.include_router(usuarios.router)
api_router.include_router(solicitudes.router)
api_router.include_router(pqrs.router)
api_router.include_router(contacto.router)

# Health check y estado del sistema
@api_router.get("/health", tags=["General"])
def read_root():
    return {
        "success": True,
        "message": f"Servicio activo de {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": "development",
        "docs": "/docs"
    }

# Registrar el sub-router en la aplicación
app.include_router(api_router)

from fastapi.responses import FileResponse
import os

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    fav_path = os.path.join("frontend", "img", "logo.png")
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return FileResponse(os.path.join("frontend", "index.html"))

# Montar los archivos estáticos del frontend al final de la aplicación
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
