
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Text, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Local(Base):
    __tablename__ = "locales"

    __table_args__ = (
        UniqueConstraint("id_local", "id_restaurante"),
        CheckConstraint(
            "capacidad_clientes IS NULL OR capacidad_clientes >= 0"
        ),
    )

    id_local: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    id_restaurante: Mapped[int] = mapped_column(
        ForeignKey("restaurantes.id_restaurante", ondelete="RESTRICT"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    provincia: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    canton: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    distrito: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    direccion: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    telefono: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    correo_contacto: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    horario_apertura: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True
    )

    horario_cierre: Mapped[Optional[str]] = mapped_column(
        String(5), nullable=True
    )

    capacidad_clientes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    fecha_apertura: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    imagen_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )

    # Relaciones
    restaurante: Mapped["Restaurante"] = relationship(
        "Restaurante",
        back_populates="locales"
    )

    asignaciones: Mapped[List["AsignacionEmpleado"]] = relationship(
        "AsignacionEmpleado",
        primaryjoin=(
            "and_("
            "Local.id_local == "
            "foreign(AsignacionEmpleado.id_local), "
            "Local.id_restaurante == "
            "AsignacionEmpleado.id_restaurante"
            ")"
        ),
        back_populates="local"
    )
