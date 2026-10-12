
from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


class RestauranteBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: Optional[str] = None
    tipo_comida: Optional[str] = Field(default=None, max_length=100)
    cedula_juridica: Optional[str] = Field(default=None, max_length=30)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo_contacto: Optional[EmailStr] = None
    sitio_web: Optional[str] = Field(default=None, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    fecha_fundacion: Optional[datetime] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("El nombre es obligatorio")
        return valor


class RestauranteCrear(RestauranteBase):
    pass


class RestauranteActualizar(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = None
    tipo_comida: Optional[str] = Field(default=None, max_length=100)
    cedula_juridica: Optional[str] = Field(default=None, max_length=30)
    telefono: Optional[str] = Field(default=None, max_length=20)
    correo_contacto: Optional[EmailStr] = None
    sitio_web: Optional[str] = Field(default=None, max_length=255)
    logo_url: Optional[str] = Field(default=None, max_length=500)
    fecha_fundacion: Optional[datetime] = None
    activo: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                raise ValueError("El nombre no puede estar vacío")
        return valor


class RestauranteRespuesta(RestauranteBase):
    id_restaurante: int
    id_usuario: int
    fecha_registro: datetime
    activo: bool

    model_config = ConfigDict(from_attributes=True)
