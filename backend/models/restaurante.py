
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Restaurante(Base):
    __tablename__ = "restaurantes"

    id_restaurante: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id_usuario", ondelete="RESTRICT"),
        nullable=False
    )

    nombre: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    tipo_comida: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )

    cedula_juridica: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True
    )

    telefono: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    correo_contacto: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    sitio_web: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )

    fecha_fundacion: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    activo: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )

    # Relaciones
    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="restaurantes"
    )

    locales: Mapped[List["Local"]] = relationship(
        "Local",
        back_populates="restaurante"
    )

    empleados: Mapped[List["Empleado"]] = relationship(
        "Empleado",
        back_populates="restaurante"
    )
