
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status
)

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from backend.config import settings
from backend.dependencies import (
    DBSession,
    UsuarioActual,
    verificar_csrf
)

from backend.models.usuario import Usuario

from backend.schemas.usuario import (
    UsuarioCrear,
    UsuarioLogin,
    UsuarioRespuesta
)

from backend.security import (
    generar_hash,
    verificar_clave,
    crear_token_acceso,
    verificar_token,
    crear_token_csrf,
    establecer_cookie,
    eliminar_cookie
)


# ==========================================
# CONFIGURACIÓN DEL ROUTER
# ==========================================

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


# ==========================================
# REGISTRO DE USUARIOS
# ==========================================

@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED
)
def registrar_usuario(
    datos: UsuarioCrear,
    db: DBSession
):
    """
    Registra un nuevo usuario en FastManage.
    """

    correo = str(datos.correo).strip().lower()

    # Comprobar si el correo ya está registrado
    usuario_existente = db.scalar(
        select(Usuario).where(
            func.lower(Usuario.correo) == correo
        )
    )

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado"
        )

    # Crear el usuario con la contraseña cifrada
    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        primer_apellido=datos.primer_apellido,
        segundo_apellido=datos.segundo_apellido,
        correo=correo,
        clave_hash=generar_hash(datos.clave),
        telefono=datos.telefono,
        fecha_nacimiento=datos.fecha_nacimiento,
        activo=True
    )

    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo registrar el usuario. Verifica el correo electrónico"
        )

    return nuevo_usuario


# ==========================================
# INICIO DE SESIÓN
# ==========================================

@router.post(
    "/login",
    response_model=UsuarioRespuesta
)
def iniciar_sesion(
    datos: UsuarioLogin,
    response: Response,
    db: DBSession
):
    """
    Valida las credenciales y crea una sesión.
    """

    correo = str(datos.correo).strip().lower()

    usuario = db.scalar(
        select(Usuario).where(
            func.lower(Usuario.correo) == correo
        )
    )

    # No revelar cuál credencial es incorrecta
    if (
        usuario is None
        or not verificar_clave(
            datos.clave,
            usuario.clave_hash
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos"
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta está desactivada"
        )

    # Registrar el último acceso
    usuario.ultimo_acceso = (
        datetime.now(timezone.utc)
        .replace(tzinfo=None)
    )

    db.commit()
    db.refresh(usuario)

    # Generar el JWT
    token = crear_token_acceso(
        usuario.id_usuario
    )

    # Guardarlo en una cookie HttpOnly
    establecer_cookie(
        response,
        token
    )

    # Evitar que la respuesta autenticada
    # quede almacenada en caché
    response.headers["Cache-Control"] = "no-store"

    return usuario


# ==========================================
# PERFIL DEL USUARIO
# ==========================================

@router.get(
    "/me",
    response_model=UsuarioRespuesta
)
def obtener_perfil(
    usuario: UsuarioActual,
    response: Response
):
    """
    Devuelve el perfil del usuario autenticado.
    """

    response.headers["Cache-Control"] = "no-store"

    return usuario


# ==========================================
# TOKEN CSRF
# ==========================================

@router.get("/csrf")
def obtener_csrf(
    request: Request,
    response: Response,
    usuario: UsuarioActual
):
    """
    Genera un token CSRF vinculado a la sesión.
    """

    token_sesion = request.cookies.get(
        settings.COOKIE_NAME
    )

    if not token_sesion:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debes iniciar sesión"
        )

    # UsuarioActual ya verificó la sesión.
    token_csrf = crear_token_csrf(
        token_sesion
    )

    response.headers["Cache-Control"] = "no-store"

    return {
        "csrf_token": token_csrf
    }


# ==========================================
# CIERRE DE SESIÓN
# ==========================================

@router.post(
    "/logout",
    dependencies=[Depends(verificar_csrf)]
)
def cerrar_sesion(
    response: Response
):
    """
    Elimina la cookie de autenticación.
    """

    eliminar_cookie(response)

    response.headers["Cache-Control"] = "no-store"

    return {
        "mensaje": "Sesión cerrada correctamente"
    }
