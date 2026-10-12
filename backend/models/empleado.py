
from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Text, DateTime, Numeric,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Empleado(Base):
    __tablename__ = "empleados"

    __table_args__ = (
        UniqueConstraint("id_empleado", "id_restaurante"),
        CheckConstraint("salario IS NULL OR salario >= 0"),
    )

    id_empleado: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    id_restaurante: Mapped[int] = mapped_column(
        ForeignKey("restaurantes.id_restaurante", ondelete="RESTRICT"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    primer_apellido: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    segundo_apellido: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    identificacion: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True
    )

    fecha_nacimiento: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    correo: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    telefono: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    direccion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    puesto: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    tipo_contrato: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    fecha_contratacion: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    salario: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    contacto_emergencia: Mapped[Optional[str]] = mapped_column(
        String(150), nullable=True
    )

    telefono_emergencia: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )

    # Relaciones
    restaurante: Mapped["Restaurante"] = relationship(
        "Restaurante",
        back_populates="empleados"
    )

    asignaciones: Mapped[List["AsignacionEmpleado"]] = relationship(
        "AsignacionEmpleado",
        primaryjoin=(
            "and_("
            "Empleado.id_empleado == "
            "foreign(AsignacionEmpleado.id_empleado), "
            "Empleado.id_restaurante == "
            "AsignacionEmpleado.id_restaurante"
            ")"
        ),
        back_populates="empleado"
    )
