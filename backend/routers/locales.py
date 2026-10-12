
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status
)

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.dependencies import (
    DBSession,
    UsuarioActual,
    verificar_csrf
)

from backend.models.local import Local
from backend.models.restaurante import Restaurante

from backend.schemas.local import (
    LocalCrear,
    LocalActualizar,
    LocalRespuesta
)


# ==========================================
# CONFIGURACIÓN DEL ROUTER
# ==========================================

router = APIRouter(
    prefix="/locales",
    tags=["Locales"]
)


# ==========================================
# FUNCIÓN AUXILIAR: VALIDAR RESTAURANTE
# ==========================================

def verificar_restaurante_usuario(
    id_restaurante: int,
    id_usuario: int,
    db: Session
) -> Restaurante:
    """
    Comprueba que el restaurante exista
    y pertenezca al usuario autenticado.
    """

    restaurante = db.scalar(
        select(Restaurante).where(
            Restaurante.id_restaurante == id_restaurante,
            Restaurante.id_usuario == id_usuario
        )
    )

    if restaurante is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurante no encontrado"
        )

    return restaurante


# ==========================================
# FUNCIÓN AUXILIAR: OBTENER LOCAL
# ==========================================

def obtener_local_usuario(
    id_local: int,
    id_usuario: int,
    db: Session
) -> Local:
    """
    Busca un local asociado a un restaurante
    que pertenezca al usuario autenticado.
    """

    local = db.scalar(
        select(Local)
        .join(
            Restaurante,
            Local.id_restaurante == Restaurante.id_restaurante
        )
        .where(
            Local.id_local == id_local,
            Restaurante.id_usuario == id_usuario
        )
    )

    if local is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Local no encontrado"
        )

    return local


# ==========================================
# CREAR LOCAL
# ==========================================

@router.post(
    "",
    response_model=LocalRespuesta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verificar_csrf)]
)
def crear_local(
    datos: LocalCrear,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Registra un nuevo local en un restaurante
    perteneciente al usuario autenticado.
    """

    # Verificar que el restaurante sea del usuario
    verificar_restaurante_usuario(
        datos.id_restaurante,
        usuario.id_usuario,
        db
    )

    nuevo_local = Local(
        **datos.model_dump()
    )

    try:
        db.add(nuevo_local)
        db.commit()
        db.refresh(nuevo_local)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo registrar el local"
        )

    return nuevo_local


# ==========================================
# LISTAR LOCALES
# ==========================================

@router.get(
    "",
    response_model=List[LocalRespuesta]
)
def listar_locales(
    db: DBSession,
    usuario: UsuarioActual,
    id_restaurante: Optional[int] = Query(
        default=None,
        gt=0
    )
):
    """
    Lista los locales de los restaurantes
    pertenecientes al usuario autenticado.

    Permite filtrar por restaurante.
    """

    consulta = (
        select(Local)
        .join(
            Restaurante,
            Local.id_restaurante == Restaurante.id_restaurante
        )
        .where(
            Restaurante.id_usuario == usuario.id_usuario
        )
    )

    if id_restaurante is not None:
        verificar_restaurante_usuario(
            id_restaurante,
            usuario.id_usuario,
            db
        )

        consulta = consulta.where(
            Local.id_restaurante == id_restaurante
        )

    consulta = consulta.order_by(
        Local.id_local.desc()
    )

    return db.scalars(consulta).all()


# ==========================================
# OBTENER LOCAL POR ID
# ==========================================

@router.get(
    "/{id_local}",
    response_model=LocalRespuesta
)
def obtener_local(
    id_local: int,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Consulta un local específico.
    """

    return obtener_local_usuario(
        id_local,
        usuario.id_usuario,
        db
    )


# ==========================================
# ACTUALIZAR LOCAL
# ==========================================

@router.put(
    "/{id_local}",
    response_model=LocalRespuesta,
    dependencies=[Depends(verificar_csrf)]
)
def actualizar_local(
    id_local: int,
    datos: LocalActualizar,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Actualiza un local perteneciente
    al usuario autenticado.
    """

    local = obtener_local_usuario(
        id_local,
        usuario.id_usuario,
        db
    )

    cambios = datos.model_dump(
        exclude_unset=True
    )

    # Campos que no pueden recibir None
    campos_obligatorios = {
        "nombre",
        "provincia",
        "canton",
        "direccion",
        "activo"
    }

    for campo in campos_obligatorios:
        if campo in cambios and cambios[campo] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El campo '{campo}' no puede ser nulo"
            )

    for campo, valor in cambios.items():
        setattr(local, campo, valor)

    try:
        db.commit()
        db.refresh(local)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar el local"
        )

    return local


# ==========================================
# ELIMINAR LOCAL
# ==========================================

@router.delete(
    "/{id_local}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verificar_csrf)]
)
def eliminar_local(
    id_local: int,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Elimina un local perteneciente
    al usuario autenticado.
    """

    local = obtener_local_usuario(
        id_local,
        usuario.id_usuario,
        db
    )

    try:
        db.delete(local)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo eliminar el local"
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
