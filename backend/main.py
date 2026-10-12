
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import crear_tablas

# Registrar todos los modelos de SQLAlchemy
import backend.models

# Routers de FastAPI
from backend.routers import (
    auth,
    restaurantes,
    locales,
    empleados,
    asignaciones
)


# ==========================================
# DIRECTORIOS DEL PROYECTO
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

PAGES_DIR = FRONTEND_DIR / "pages"
CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"
ASSETS_DIR = FRONTEND_DIR / "assets"


# ==========================================
# CICLO DE VIDA DE LA APLICACIÓN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear las tablas faltantes al iniciar
    crear_tablas()

    yield


# ==========================================
# CONFIGURACIÓN DE FASTAPI
# ==========================================

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API para gestionar restaurantes, "
        "locales, empleados y asignaciones."
    ),
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)


# ==========================================
# ARCHIVOS ESTÁTICOS
# ==========================================

app.mount(
    "/css",
    StaticFiles(directory=CSS_DIR),
    name="css"
)

app.mount(
    "/js",
    StaticFiles(directory=JS_DIR),
    name="js"
)

app.mount(
    "/assets",
    StaticFiles(directory=ASSETS_DIR),
    name="assets"
)


# ==========================================
# ROUTERS DE LA API
# ==========================================

app.include_router(
    auth.router,
    prefix="/api"
)

app.include_router(
    restaurantes.router,
    prefix="/api"
)

app.include_router(
    locales.router,
    prefix="/api"
)

app.include_router(
    empleados.router,
    prefix="/api"
)

app.include_router(
    asignaciones.router,
    prefix="/api"
)


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.get("/", include_in_schema=False)
def inicio():
    return FileResponse(
        PAGES_DIR / "index.html"
    )


# ==========================================
# PÁGINAS PERMITIDAS
# ==========================================

PAGINAS_PERMITIDAS = {
    "login",
    "registro",
    "dashboard",
    "restaurantes",
    "locales",
    "empleados",
    "asignaciones"
}


@app.get(
    "/{pagina}.html",
    include_in_schema=False
)
def mostrar_pagina(pagina: str):

    if pagina not in PAGINAS_PERMITIDAS:
        raise HTTPException(
            status_code=404,
            detail="Página no encontrada"
        )

    ruta = PAGES_DIR / f"{pagina}.html"

    if not ruta.is_file():
        raise HTTPException(
            status_code=404,
            detail="El archivo HTML no existe"
        )

    return FileResponse(ruta)


# ==========================================
# VERIFICACIÓN DEL SERVIDOR
# ==========================================

@app.get(
    "/api/health",
    tags=["Sistema"]
)
def verificar_estado():

    return {
        "estado": "activo",
        "aplicacion": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
