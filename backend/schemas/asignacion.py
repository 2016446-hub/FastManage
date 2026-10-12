
from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator
)


# ==========================================
# ESQUEMA BASE
# ==========================================

class AsignacionBase(BaseModel):

    fecha_finalizacion: Optional[datetime] = None

    turno: Optional[str] = Field(
        default=None,
        max_length=50
    )

    observaciones: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid"
    )


# ==========================================
# CREAR ASIGNACIÓN
# ==========================================

class AsignacionCrear(AsignacionBase):

    id_empleado: int = Field(gt=0)

    id_local: int = Field(gt=0)

    id_restaurante: int = Field(gt=0)

    fecha_asignacion: Optional[datetime] = None

    @model_validator(mode="after")
    def validar_fechas(self):

        if (
            self.fecha_asignacion is not None
            and self.fecha_finalizacion is not None
            and self.fecha_finalizacion < self.fecha_asignacion
        ):
            raise ValueError(
                "La fecha de finalización no puede "
                "ser anterior a la fecha de asignación"
            )

        return self


# ==========================================
# ACTUALIZAR ASIGNACIÓN
# ==========================================

class AsignacionActualizar(BaseModel):

    fecha_finalizacion: Optional[datetime] = None

    turno: Optional[str] = Field(
        default=None,
        max_length=50
    )

    observaciones: Optional[str] = None

    activo: Optional[bool] = None

    model_config = ConfigDict(
        extra="forbid"
    )


# ==========================================
# RESPUESTA DE ASIGNACIÓN
# ==========================================

class AsignacionRespuesta(AsignacionBase):

    id_asignacion: int

    id_empleado: int

    id_local: int

    id_restaurante: int

    fecha_asignacion: datetime

    activo: bool

    model_config = ConfigDict(
        from_attributes=True
    )

