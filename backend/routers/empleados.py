from datetime import datetime, timezone
from backend.models.asignacion import AsignacionEmpleado

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

from backend.models.empleado import Empleado
from backend.models.restaurante import Restaurante

from backend.schemas.empleado import (
    EmpleadoCrear,
    EmpleadoActualizar,
    EmpleadoRespuesta
)


# ==========================================
# CONFIGURACIÓN DEL ROUTER
# ==========================================

router = APIRouter(
    prefix="/empleados",
    tags=["Empleados"]
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
    Verifica que un restaurante exista
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
# FUNCIÓN AUXILIAR: OBTENER EMPLEADO
# ==========================================

def obtener_empleado_usuario(
    id_empleado: int,
    id_usuario: int,
    db: Session
) -> Empleado:
    """
    Busca un empleado cuyo restaurante
    pertenezca al usuario autenticado.

    Devuelve 404 si no existe o si
    pertenece a otro usuario.
    """

    empleado = db.scalar(
        select(Empleado)
        .join(
            Restaurante,
            Empleado.id_restaurante ==
            Restaurante.id_restaurante
        )
        .where(
            Empleado.id_empleado == id_empleado,
            Restaurante.id_usuario == id_usuario
        )
    )

    if empleado is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Empleado no encontrado"
        )

    return empleado


# ==========================================
# CREAR EMPLEADO
# ==========================================

@router.post(
    "",
    response_model=EmpleadoRespuesta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verificar_csrf)]
)
def crear_empleado(
    datos: EmpleadoCrear,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Registra un empleado en un restaurante
    perteneciente al usuario autenticado.
    """

    # Comprobar la propiedad del restaurante
    verificar_restaurante_usuario(
        datos.id_restaurante,
        usuario.id_usuario,
        db
    )

    nuevo_empleado = Empleado(
        **datos.model_dump()
    )

    try:
        db.add(nuevo_empleado)
        db.commit()
        db.refresh(nuevo_empleado)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo registrar el empleado"
        )

    return nuevo_empleado



# ==========================================
# LISTAR EMPLEADOS
# ==========================================

@router.get(
    "",
    response_model=List[EmpleadoRespuesta]
)
def listar_empleados(
    db: DBSession,
    usuario: UsuarioActual,
    id_restaurante: Optional[int] = Query(
        default=None,
        gt=0
    ),
    activo: Optional[bool] = Query(
        default=True,
        description=(
            "True: activos; False: inactivos; "
            "sin parámetro: activos"
        )
    ),
    incluir_todos: bool = Query(
        default=False,
        description="Incluir empleados activos e inactivos"
    )
):
    """
    Lista empleados de los restaurantes
    pertenecientes al usuario autenticado.

    Por defecto, muestra únicamente activos.
    """

    consulta = (
        select(Empleado)
        .join(
            Restaurante,
            Empleado.id_restaurante ==
            Restaurante.id_restaurante
        )
        .where(
            Restaurante.id_usuario == usuario.id_usuario
        )
    )

    # Filtrar por restaurante
    if id_restaurante is not None:

        verificar_restaurante_usuario(
            id_restaurante,
            usuario.id_usuario,
            db
        )

        consulta = consulta.where(
            Empleado.id_restaurante == id_restaurante
        )

    # Filtrar por estado
    if not incluir_todos:
        consulta = consulta.where(
            Empleado.activo == activo
        )

    consulta = consulta.order_by(
        Empleado.id_empleado.desc()
    )

    return db.scalars(consulta).all()



# ==========================================
# OBTENER EMPLEADO POR ID
# ==========================================

@router.get(
    "/{id_empleado}",
    response_model=EmpleadoRespuesta
)
def obtener_empleado(
    id_empleado: int,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Consulta un empleado específico.
    """

    return obtener_empleado_usuario(
        id_empleado,
        usuario.id_usuario,
        db
    )


# ==========================================
# ACTUALIZAR EMPLEADO
# ==========================================

@router.put(
    "/{id_empleado}",
    response_model=EmpleadoRespuesta,
    dependencies=[Depends(verificar_csrf)]
)
def actualizar_empleado(
    id_empleado: int,
    datos: EmpleadoActualizar,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Actualiza la información de un empleado
    perteneciente al usuario autenticado.
    """

    empleado = obtener_empleado_usuario(
        id_empleado,
        usuario.id_usuario,
        db
    )

    cambios = datos.model_dump(
        exclude_unset=True
    )

    # Campos que no admiten valores nulos
    campos_obligatorios = {
        "nombre",
        "primer_apellido",
        "puesto",
        "fecha_contratacion",
        "activo"
    }

    for campo in campos_obligatorios:
        if (
            campo in cambios
            and cambios[campo] is None
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"El campo '{campo}' "
                    "no puede ser nulo"
                )
            )

    # Aplicar únicamente los cambios recibidos
    for campo, valor in cambios.items():
        setattr(
            empleado,
            campo,
            valor
        )

    try:
        db.commit()
        db.refresh(empleado)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo actualizar el empleado"
        )

    return empleado



# ==========================================
# DESACTIVAR EMPLEADO Y CERRAR ASIGNACIONES
# ==========================================

@router.delete(
    "/{id_empleado}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verificar_csrf)]
)
def eliminar_empleado(
    id_empleado: int,
    db: DBSession,
    usuario: UsuarioActual
):
    """
    Desactiva un empleado y cierra sus
    asignaciones activas, conservando
    todos los registros históricos.
    """

    empleado = obtener_empleado_usuario(
        id_empleado,
        usuario.id_usuario,
        db
    )

    if not empleado.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El empleado ya se encuentra inactivo"
        )

    # Desactivar empleado
    empleado.activo = False

    # Buscar asignaciones vigentes
    asignaciones = db.scalars(
        select(AsignacionEmpleado).where(
            AsignacionEmpleado.id_empleado == id_empleado,
            AsignacionEmpleado.activo.is_(True)
        )
    ).all()

    fecha_cierre = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    # Cerrar asignaciones sin eliminarlas
    for asignacion in asignaciones:
        asignacion.activo = False

        if asignacion.fecha_finalizacion is None:
            asignacion.fecha_finalizacion = fecha_cierre

    # Guardar todos los cambios juntos
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
