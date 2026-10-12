
from contextlib import asynccontextmanager

from fastapi import FastAPI

import backend.models

from backend.database import crear_tablas

from backend.routers import (
    auth,
    restaurantes,
    locales,
    empleados
)


# ==========================================
# INICIALIZACIÓN DE LA BASE DE DATOS
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    yield


# ==========================================
# APLICACIÓN DE PRUEBAS
# ==========================================

app = FastAPI(
    title="FastManage - Pruebas de API",
    version="1.0.0",
    lifespan=lifespan
)


# ==========================================
# ROUTERS
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


# ==========================================
# ESTADO DEL SERVIDOR
# ==========================================

@app.get(
    "/api/health",
    tags=["Sistema"]
)
def health():
    return {
        "estado": "activo",
        "aplicacion": "FastManage"
    }
