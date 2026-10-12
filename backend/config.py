
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Carpeta principal de FastManage
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # ==========================================
    # CONFIGURACIÓN GENERAL
    # ==========================================

    APP_NAME: str = "FastManage"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ==========================================
    # BASE DE DATOS
    # ==========================================

    DATABASE_URL: str = (
        "sqlite:///./data/fastmanage.db"
    )

   
    @field_validator("DATABASE_URL")
    @classmethod
    def normalizar_database_url(cls, valor: str) -> str:
        if valor.startswith("postgres://"):
            return valor.replace(
                "postgres://",
                "postgresql+psycopg://",
                1
            )

        if valor.startswith("postgresql://"):
            return valor.replace(
                "postgresql://",
                "postgresql+psycopg://",
                1
            )

        if valor.startswith("postgresql+psycopg://"):
            return valor

        prefijo = "sqlite:///"

        if not valor.startswith(prefijo):
            raise ValueError(
                "DATABASE_URL debe utilizar SQLite o PostgreSQL"
            )

        ruta = valor[len(prefijo):]

        if ruta == ":memory:":
            return valor

        archivo = Path(ruta)

        if not archivo.is_absolute():
            archivo = BASE_DIR / archivo

        archivo = archivo.resolve()

        return f"sqlite:///{archivo.as_posix()}"


    # ==========================================
    # SEGURIDAD Y AUTENTICACIÓN
    # ==========================================

    SECRET_KEY: str = Field(min_length=32)

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        gt=0
    )

    # ==========================================
    # COOKIES
    # ==========================================

    COOKIE_NAME: str = "fastmanage_session"

    COOKIE_SECURE: bool = True

    COOKIE_SAMESITE: str = "lax"

    # ==========================================
    # SERVIDOR
    # ==========================================

    HOST: str = "127.0.0.1"

    PORT: int = Field(
        default=8000,
        ge=1,
        le=65535
    )

    # ==========================================
    # LECTURA DE .env
    # ==========================================

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
