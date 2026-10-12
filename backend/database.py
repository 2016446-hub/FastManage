
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = settings.DATABASE_URL

ES_SQLITE = DATABASE_URL.startswith("sqlite:")


# ==========================================
# CONFIGURACIÓN DE SQLITE
# ==========================================

if ES_SQLITE:
    if ":memory:" not in DATABASE_URL:
        DATA_DIR = BASE_DIR / "data"
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )

    @event.listens_for(engine, "connect")
    def habilitar_foreign_keys(
        dbapi_connection,
        connection_record
    ):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


# ==========================================
# CONFIGURACIÓN DE POSTGRESQL
# ==========================================

else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )


# ==========================================
# SESIONES
# ==========================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ==========================================
# BASE DE MODELOS
# ==========================================

class Base(DeclarativeBase):
    pass


# ==========================================
# DEPENDENCIA DE BASE DE DATOS
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# CREACIÓN DE TABLAS
# ==========================================

def crear_tablas():
    Base.metadata.create_all(bind=engine)

