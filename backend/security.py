
import hashlib
import hmac

from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import HTTPException, Response, status
from pwdlib import PasswordHash

from backend.config import settings


password_hash = PasswordHash.recommended()


# ==========================================
# CONTRASEÑAS
# ==========================================

def generar_hash(clave: str) -> str:
    return password_hash.hash(clave)


def verificar_clave(
    clave: str,
    clave_hash: str
) -> bool:
    """
    Verifica una contraseña con Argon2.
    """

    try:
        return password_hash.verify(
            clave,
            clave_hash
        )

    except Exception:
        return False


# ==========================================
# TOKENS JWT
# ==========================================

def crear_token_acceso(id_usuario: int) -> str:

    ahora = datetime.now(timezone.utc)

    expiracion = ahora + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(id_usuario),
        "iat": ahora,
        "exp": expiracion,
        "type": "access"
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verificar_token(token: str) -> int:

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "require": ["sub", "iat", "exp"]
            }
        )

        if payload.get("type") != "access":
            raise ValueError("Tipo de token inválido")

        id_usuario = int(payload["sub"])

        if id_usuario <= 0:
            raise ValueError("Usuario inválido")

        return id_usuario

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
        KeyError
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada"
        )


# ==========================================
# PROTECCIÓN CSRF
# ==========================================

def crear_token_csrf(token_sesion: str) -> str:
    """
    Genera un token CSRF vinculado
    al JWT de la sesión actual.
    """

    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        token_sesion.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def verificar_token_csrf(
    token_sesion: str,
    token_csrf: str | None
) -> bool:
    """
    Comprueba el token CSRF recibido.
    """

    if not token_csrf:
        return False

    esperado = crear_token_csrf(token_sesion)

    return hmac.compare_digest(
        esperado,
        token_csrf
    )


# ==========================================
# COOKIES DE AUTENTICACIÓN
# ==========================================

def establecer_cookie(
    response: Response,
    token: str
):

    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        path="/"
    )


def eliminar_cookie(response: Response):

    response.delete_cookie(
        key=settings.COOKIE_NAME,
        path="/",
        secure=settings.COOKIE_SECURE,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE
    )
