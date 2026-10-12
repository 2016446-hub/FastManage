
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
    Index,
    text
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    foreign
)

from backend.database import Base


def fecha_actual():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AsignacionEmpleado(Base):
    __tablename__ = "asignaciones_empleados"

    __table_args__ = (
    ForeignKeyConstraint(
        ["id_empleado", "id_restaurante"],
        ["empleados.id_empleado", "empleados.id_restaurante"],
        ondelete="CASCADE"
    ),

    ForeignKeyConstraint(
        ["id_local", "id_restaurante"],
        ["locales.id_local", "locales.id_restaurante"],
        ondelete="CASCADE"
    ),

    CheckConstraint(
        "activo IN (0, 1)",
        name="ck_asignacion_activo"
    ),

    Index(
        "uq_asignacion_activa_empleado_local",
        "id_empleado",
        "id_local",
        unique=True,
        sqlite_where=text("activo = 1")
    )
)

    # ==========================================
    # LLAVE PRIMARIA
    # ==========================================

    id_asignacion: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    # ==========================================
    # LLAVES FORÁNEAS
    # ==========================================

    id_empleado: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    id_local: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    id_restaurante: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    # ==========================================
    # INFORMACIÓN DE ASIGNACIÓN
    # ==========================================

    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime,
        default=fecha_actual,
        nullable=False
    )

    fecha_finalizacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    turno: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )

    observaciones: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    # ==========================================
    # RELACIÓN CON EMPLEADO
    # ==========================================

    empleado: Mapped["Empleado"] = relationship(
        "Empleado",
        primaryjoin=(
            "and_("
            "Empleado.id_empleado == "
            "foreign(AsignacionEmpleado.id_empleado), "
            "Empleado.id_restaurante == "
            "AsignacionEmpleado.id_restaurante"
            ")"
        ),
        back_populates="asignaciones"
    )

    # ==========================================
    # RELACIÓN CON LOCAL
    # ==========================================

    local: Mapped["Local"] = relationship(
        "Local",
        primaryjoin=(
            "and_("
            "Local.id_local == "
            "foreign(AsignacionEmpleado.id_local), "
            "Local.id_restaurante == "
            "AsignacionEmpleado.id_restaurante"
            ")"
        ),
        back_populates="asignaciones"
    )
