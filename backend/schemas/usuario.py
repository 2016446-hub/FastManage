
from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


class UsuarioBase(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=100
    )

    primer_apellido: str = Field(
        min_length=1,
        max_length=100
    )

    segundo_apellido: Optional[str] = Field(
        default=None,
        max_length=100
    )

    correo: EmailStr

    telefono: Optional[str] = Field(
        default=None,
        max_length=20
    )

    fecha_nacimiento: Optional[datetime] = None

    @field_validator("nombre", "primer_apellido")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "Este campo no puede estar vacío"
            )

        return valor

    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, valor: str) -> str:
        return valor.lower()


# ==========================================
# REGISTRO
# ==========================================

class UsuarioCrear(UsuarioBase):
    clave: str = Field(
        min_length=8,
        max_length=128
    )


# ==========================================
# LOGIN
# ==========================================

class UsuarioLogin(BaseModel):
    correo: EmailStr
    clave: str

    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, valor: str) -> str:
        return valor.lower()


# ==========================================
# ACTUALIZACIÓN
# ==========================================

class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    primer_apellido: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    segundo_apellido: Optional[str] = Field(
        default=None,
        max_length=100
    )

    telefono: Optional[str] = Field(
        default=None,
        max_length=20
    )

    @field_validator("nombre", "primer_apellido")
    @classmethod
    def validar_texto(cls, valor):
        if valor is not None:
            valor = valor.strip()

            if not valor:
                raise ValueError(
                    "Este campo no puede estar vacío"
                )

        return valor


# ==========================================
# RESPUESTA
# ==========================================

class UsuarioRespuesta(UsuarioBase):
    id_usuario: int
    fecha_registro: datetime
    ultimo_acceso: Optional[datetime]
    activo: bool

    model_config = ConfigDict(
        from_attributes=True
    )
