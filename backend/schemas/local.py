
from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator
)


def validar_horario(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None

    try:
        horas, minutos = map(int, valor.split(":"))
        if not (0 <= horas <= 23 and 0 <= minutos <= 59):
            raise ValueError
    except (ValueError, TypeError):
        raise ValueError(
            "El horario debe tener formato HH:MM"
        )

    if len(valor) != 5:
        raise ValueError(
            "El horario debe tener formato HH:MM"
        )

    return valor


class LocalBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    descripcion: Optional[str] = None

    provincia: str = Field(min_length=1, max_length=100)
    canton: str = Field(min_length=1, max_length=100)
    distrito: Optional[str] = Field(default=None, max_length=100)
    direccion: str = Field(min_length=1)

    telefono: Optional[str] = Field(default=None, max_length=20)
    correo_contacto: Optional[EmailStr] = None

    horario_apertura: Optional[str] = None
    horario_cierre: Optional[str] = None

    capacidad_clientes: Optional[int] = Field(default=None, ge=0)
    fecha_apertura: Optional[datetime] = None
    imagen_url: Optional[str] = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "provincia", "canton", "direccion")
    @classmethod
    def validar_obligatorio(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("Este campo es obligatorio")
        return valor

    @field_validator("horario_apertura", "horario_cierre")
    @classmethod
    def comprobar_horario(cls, valor: Optional[str]) -> Optional[str]:
        return validar_horario(valor)


class LocalCrear(LocalBase):
    id_restaurante: int = Field(gt=0)


class LocalActualizar(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = None

    provincia: Optional[str] = Field(default=None, min_length=1, max_length=100)
    canton: Optional[str] = Field(default=None, min_length=1, max_length=100)
    distrito: Optional[str] = Field(default=None, max_length=100)
    direccion: Optional[str] = Field(default=None, min_length=1)

    telefono: Optional[str] = Field(default=None, max_length=20)
    correo_contacto: Optional[EmailStr] = None

    horario_apertura: Optional[str] = None
    horario_cierre: Optional[str] = None

    capacidad_clientes: Optional[int] = Field(default=None, ge=0)
    fecha_apertura: Optional[datetime] = None
    imagen_url: Optional[str] = Field(default=None, max_length=500)
    activo: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "provincia", "canton", "direccion")
    @classmethod
    def validar_obligatorio(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                raise ValueError("Este campo no puede estar vacío")
        return valor

    @field_validator("horario_apertura", "horario_cierre")
    @classmethod
    def comprobar_horario(cls, valor: Optional[str]) -> Optional[str]:
        return validar_horario(valor)


class LocalRespuesta(LocalBase):
    id_local: int
    id_restaurante: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)
