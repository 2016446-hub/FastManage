
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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

from backend.models.restaurante import Restaurante

from backend.schemas.restaurante import (
    RestauranteCrear,
    RestauranteActualizar,
    RestauranteRespuesta
)


# ==========================================
# CONFIGURACIÓN DEL ROUTER
# ==========================================

router = APIRouter(
    prefix="/restaurantes",
    tags=["Restaurantes"]
)


# ==========================================
# FUNCIÓN AUXILIAR
# ==========================================

def obtener_restaurante_usuario(
    id_restaurante: int,
    id_usuario: int,
    db: Session
) -> Restaurante:
    """
    Busca un restaurante que pertenezca
    al usuario autenticado.

    Devuelve 404 si no existe o si
    pertenece a otro usuario.
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
# CREAR RESTAURANTE
# ==========================================

@router.post(
    "",
    response_model=RestauranteRespuesta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verificar_csrf)]
)
def crear_restaurante(
    datos: RestauranteCrear,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Registra un restaurante asociado
    al usuario autenticado.
    """

    nuevo_restaurante = Restaurante(
        **datos.model_dump(),
        id_usuario=usuario.id_usuario
    )

    try:
        db.add(nuevo_restaurante)
        db.commit()
        db.refresh(nuevo_restaurante)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo registrar el restaurante"
        )

    return nuevo_restaurante


# ==========================================
# LISTAR RESTAURANTES
# ==========================================

@router.get(
    "",
    response_model=List[RestauranteRespuesta]
)
def listar_restaurantes(
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Devuelve únicamente los restaurantes
    pertenecientes al usuario autenticado.
    """

    restaurantes = db.scalars(
        select(Restaurante)
        .where(
            Restaurante.id_usuario == usuario.id_usuario
        )
        .order_by(Restaurante.id_restaurante.desc())
    ).all()

    return restaurantes


# ==========================================
# OBTENER RESTAURANTE
# ==========================================

@router.get(
    "/{id_restaurante}",
    response_model=RestauranteRespuesta
)
def obtener_restaurante(
    id_restaurante: int,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Consulta un restaurante específico.
    """

    return obtener_restaurante_usuario(
        id_restaurante,
        usuario.id_usuario,
        db
    )


# ==========================================
# ACTUALIZAR RESTAURANTE
# ==========================================

@router.put(
    "/{id_restaurante}",
    response_model=RestauranteRespuesta,
    dependencies=[Depends(verificar_csrf)]
)
def actualizar_restaurante(
    id_restaurante: int,
    datos: RestauranteActualizar,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Actualiza los datos de un restaurante
    perteneciente al usuario autenticado.
    """

    restaurante = obtener_restaurante_usuario(
        id_restaurante,
        usuario.id_usuario,
        db
    )

    cambios = datos.model_dump(
        exclude_unset=True
    )

    # Evitar valores nulos en campos obligatorios
    if "nombre" in cambios and cambios["nombre"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El nombre no puede ser nulo"
        )

    if "activo" in cambios and cambios["activo"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El estado activo no puede ser nulo"
        )

    for campo, valor in cambios.items():
        setattr(restaurante, campo, valor)

    try:
        db.commit()
        db.refresh(restaurante)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar el restaurante"
        )

    return restaurante


# ==========================================
# ELIMINAR RESTAURANTE
# ==========================================

@router.delete(
    "/{id_restaurante}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verificar_csrf)]
)
def eliminar_restaurante(
    id_restaurante: int,
    db: DBSession
    ,usuario: UsuarioActual
):
    """
    Elimina un restaurante si no existen
    registros dependientes que lo impidan.
    """

    restaurante = obtener_restaurante_usuario(
        id_restaurante,
        usuario.id_usuario,
        db
    )

    try:
        db.delete(restaurante)
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar el restaurante "
                "porque tiene locales o empleados asociados"
            )
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
