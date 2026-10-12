
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
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

    correo: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )

    clave_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    telefono: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )

    fecha_nacimiento: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )

    activo: Mapped[bool] = mapped_column(
        default=True, nullable=False
    )

    # Relación: un usuario tiene varios restaurantes
    restaurantes: Mapped[List["Restaurante"]] = relationship(
        "Restaurante",
        back_populates="usuario"
    )
