
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator
)


class EmpleadoBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    primer_apellido: str = Field(min_length=1, max_length=100)
    segundo_apellido: Optional[str] = Field(default=None, max_length=100)

    identificacion: Optional[str] = Field(default=None, max_length=30)
    fecha_nacimiento: Optional[datetime] = None

    correo: Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, max_length=20)
    direccion: Optional[str] = None

    puesto: str = Field(min_length=1, max_length=100)
    tipo_contrato: Optional[str] = Field(default=None, max_length=50)
    fecha_contratacion: datetime

    salario: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2
    )

    contacto_emergencia: Optional[str] = Field(
        default=None,
        max_length=150
    )
    telefono_emergencia: Optional[str] = Field(
        default=None,
        max_length=20
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "primer_apellido", "puesto")
    @classmethod
    def validar_obligatorio(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("Este campo es obligatorio")
        return valor


class EmpleadoCrear(EmpleadoBase):
    id_restaurante: int = Field(gt=0)


class EmpleadoActualizar(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    primer_apellido: Optional[str] = Field(default=None, min_length=1, max_length=100)
    segundo_apellido: Optional[str] = Field(default=None, max_length=100)

    identificacion: Optional[str] = Field(default=None, max_length=30)
    fecha_nacimiento: Optional[datetime] = None

    correo: Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, max_length=20)
    direccion: Optional[str] = None

    puesto: Optional[str] = Field(default=None, min_length=1, max_length=100)
    tipo_contrato: Optional[str] = Field(default=None, max_length=50)
    fecha_contratacion: Optional[datetime] = None

    salario: Optional[Decimal] = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2
    )

    contacto_emergencia: Optional[str] = Field(
        default=None,
        max_length=150
    )
    telefono_emergencia: Optional[str] = Field(
        default=None,
        max_length=20
    )
    activo: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre", "primer_apellido", "puesto")
    @classmethod
    def validar_obligatorio(cls, valor: Optional[str]) -> Optional[str]:
        if valor is not None:
            valor = valor.strip()
            if not valor:
                raise ValueError("Este campo no puede estar vacío")
        return valor


class EmpleadoRespuesta(EmpleadoBase):
    id_empleado: int
    id_restaurante: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)
