
from typing import Annotated

from fastapi import (
    Depends,
    HTTPException,
    Request,
    status
)

from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.usuario import Usuario

from backend.security import (
    verificar_token,
    verificar_token_csrf
)


# ==========================================
# DEPENDENCIA DE BASE DE DATOS
# ==========================================

DBSession = Annotated[
    Session,
    Depends(get_db)
]


# ==========================================
# OBTENER USUARIO ACTUAL
# ==========================================

def obtener_usuario_actual(
    request: Request,
    db: DBSession
) -> Usuario:

    token = request.cookies.get(
        settings.COOKIE_NAME
    )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión"
        )

    id_usuario = verificar_token(token)

    usuario = db.get(
        Usuario,
        id_usuario
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada"
        )

    return usuario


UsuarioActual = Annotated[
    Usuario,
    Depends(obtener_usuario_actual)
]


# ==========================================
# PROTECCIÓN CSRF
# ==========================================

def verificar_csrf(
    request: Request,
    usuario: UsuarioActual
) -> None:
    """
    Protege las operaciones que modifican datos.
    """

    token_sesion = request.cookies.get(
        settings.COOKIE_NAME
    )

    token_csrf = request.headers.get(
        "X-CSRF-Token"
    )

    if not token_sesion or not verificar_token_csrf(
        token_sesion,
        token_csrf
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF inválido o ausente"
        )

    # Comprobar el origen cuando esté presente.
    origen = request.headers.get("origin")

    origen_esperado = str(
        request.base_url
    ).rstrip("/")

    if origen and origen.rstrip("/") != origen_esperado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origen de solicitud no permitido"
        )


ProteccionCSRF = Annotated[
    None,
    Depends(verificar_csrf)
]
