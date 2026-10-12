
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings


# ==========================================
# CONFIGURACIÓN DE RUTAS
# ==========================================

# Obtener la ruta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Carpeta donde se almacenará la base de datos
DATA_DIR = BASE_DIR / "data"

# Crear la carpeta si todavía no existe
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================

# Obtener la URL de conexión desde config.py
DATABASE_URL = settings.DATABASE_URL

# Crear el motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)


# ==========================================
# HABILITAR LLAVES FORÁNEAS EN SQLITE
# ==========================================

@event.listens_for(engine, "connect")
def habilitar_foreign_keys(
    dbapi_connection,
    connection_record
):
    """
    Habilita las restricciones de llaves foráneas
    en cada conexión SQLite.
    """

    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.close()


# ==========================================
# CONFIGURACIÓN DE SESIONES
# ==========================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ==========================================
# CLASE BASE PARA LOS MODELOS
# ==========================================

class Base(DeclarativeBase):
    """
    Clase base que utilizarán todos los modelos
    de SQLAlchemy del proyecto FastManage.
    """
    pass


# ==========================================
# DEPENDENCIA DE BASE DE DATOS
# ==========================================

def get_db():
    """
    Proporciona una sesión de base de datos
    a los endpoints de FastAPI.

    La sesión se cierra automáticamente
    al finalizar la solicitud.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================
# CREACIÓN DE TABLAS
# ==========================================

def crear_tablas():
    """
    Crea las tablas de la base de datos
    que todavía no existan.

    Los modelos deben estar importados
    antes de ejecutar esta función.
    """

    Base.metadata.create_all(bind=engine)
