
from datetime import datetime, timezone
from typing import Optional

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

from backend.models.asignacion import AsignacionEmpleado
from backend.models.empleado import Empleado
from backend.models.local import Local
from backend.models.restaurante import Restaurante

from backend.schemas.asignacion import (
    AsignacionCrear,
    AsignacionActualizar,
    AsignacionRespuesta
)


router = APIRouter(
    prefix="/asignaciones",
    tags=["Asignaciones"]
)


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def fecha_actual():
    """Devuelve la fecha actual en UTC."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def verificar_restaurante_usuario(
    id_restaurante: int,
    id_usuario: int,
    db: Session
):
    restaurante = db.scalar(
        select(Restaurante).where(
            Restaurante.id_restaurante == id_restaurante,
            Restaurante.id_usuario == id_usuario
        )
    )

    if restaurante is None:
        raise HTTPException(
            status_code=404,
            detail="Restaurante no encontrado"
        )

    return restaurante


def obtener_asignacion_usuario(
    id_asignacion: int,
    id_usuario: int,
    db: Session
):
    asignacion = db.scalar(
        select(AsignacionEmpleado)
        .join(
            Restaurante,
            AsignacionEmpleado.id_restaurante ==
            Restaurante.id_restaurante
        )
        .where(
            AsignacionEmpleado.id_asignacion == id_asignacion,
            Restaurante.id_usuario == id_usuario
        )
    )

    if asignacion is None:
        raise HTTPException(
            status_code=404,
            detail="Asignación no encontrada"
        )

    return asignacion


def validar_empleado_local(
    id_empleado: int,
    id_local: int,
    id_restaurante: int,
    db: Session,
    exigir_activos: bool = True
):
    """
    Comprueba que el empleado y el local
    pertenezcan al restaurante indicado.
    """

    empleado = db.scalar(
        select(Empleado).where(
            Empleado.id_empleado == id_empleado,
            Empleado.id_restaurante == id_restaurante
        )
    )

    if empleado is None:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado en el restaurante"
        )

    local = db.scalar(
        select(Local).where(
            Local.id_local == id_local,
            Local.id_restaurante == id_restaurante
        )
    )

    if local is None:
        raise HTTPException(
            status_code=404,
            detail="Local no encontrado en el restaurante"
        )

    if exigir_activos:
        if not empleado.activo:
            raise HTTPException(
                status_code=409,
                detail="No se puede asignar un empleado inactivo"
            )

        if not local.activo:
            raise HTTPException(
                status_code=409,
                detail="No se puede asignar a un local inactivo"
            )

    return empleado, local


def verificar_asignacion_duplicada(
    id_empleado: int,
    id_local: int,
    db: Session,
    excluir_id: Optional[int] = None
):
    """
    Impide dos asignaciones activas del
    mismo empleado al mismo local.
    """

    consulta = select(AsignacionEmpleado).where(
        AsignacionEmpleado.id_empleado == id_empleado,
        AsignacionEmpleado.id_local == id_local,
        AsignacionEmpleado.activo.is_(True)
    )

    if excluir_id is not None:
        consulta = consulta.where(
            AsignacionEmpleado.id_asignacion != excluir_id
        )

    existente = db.scalar(consulta)

    if existente is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "El empleado ya tiene una asignación "
                "activa en este local"
            )
        )


def validar_fechas(
    fecha_inicio: datetime,
    fecha_fin: Optional[datetime]
):
    if (
        fecha_fin is not None
        and fecha_fin < fecha_inicio
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "La fecha de finalización no puede "
                "ser anterior a la fecha de asignación"
            )
        )


# ==========================================
# CREAR ASIGNACIÓN
# ==========================================

@router.post(
    "",
    response_model=AsignacionRespuesta,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verificar_csrf)]
)
def crear_asignacion(
    datos: AsignacionCrear,
    db: DBSession,
    usuario: UsuarioActual
):
    verificar_restaurante_usuario(
        datos.id_restaurante,
        usuario.id_usuario,
        db
    )

    validar_empleado_local(
        datos.id_empleado,
        datos.id_local,
        datos.id_restaurante,
        db
    )

    verificar_asignacion_duplicada(
        datos.id_empleado,
        datos.id_local,
        db
    )

    valores = datos.model_dump()

    if valores.get("fecha_asignacion") is None:
        valores["fecha_asignacion"] = fecha_actual()

    # Una asignación nueva siempre comienza activa.
    valores["activo"] = True
    valores["fecha_finalizacion"] = None

    nueva_asignacion = AsignacionEmpleado(
        **valores
    )

    try:
        db.add(nueva_asignacion)
        db.commit()
        db.refresh(nueva_asignacion)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="No se pudo crear la asignación"
        )

    return nueva_asignacion


# ==========================================
# LISTAR ASIGNACIONES
# ==========================================

@router.get(
    "",
    response_model=list[AsignacionRespuesta]
)
def listar_asignaciones(
    db: DBSession,
    usuario: UsuarioActual,
    id_restaurante: Optional[int] = Query(
        default=None,
        gt=0
    ),
    id_empleado: Optional[int] = Query(
        default=None,
        gt=0
    ),
    id_local: Optional[int] = Query(
        default=None,
        gt=0
    ),
    activo: Optional[bool] = Query(
        default=None
    )
):
    consulta = (
        select(AsignacionEmpleado)
        .join(
            Restaurante,
            AsignacionEmpleado.id_restaurante ==
            Restaurante.id_restaurante
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
            AsignacionEmpleado.id_restaurante ==
            id_restaurante
        )

    if id_empleado is not None:
        consulta = consulta.where(
            AsignacionEmpleado.id_empleado == id_empleado
        )

    if id_local is not None:
        consulta = consulta.where(
            AsignacionEmpleado.id_local == id_local
        )

    if activo is not None:
        consulta = consulta.where(
            AsignacionEmpleado.activo.is_(activo)
        )

    consulta = consulta.order_by(
        AsignacionEmpleado.id_asignacion.desc()
    )

    return db.scalars(consulta).all()


# ==========================================
# CONSULTAR ASIGNACIÓN
# ==========================================

@router.get(
    "/{id_asignacion}",
    response_model=AsignacionRespuesta
)
def obtener_asignacion(
    id_asignacion: int,
    db: DBSession,
    usuario: UsuarioActual
):
    return obtener_asignacion_usuario(
        id_asignacion,
        usuario.id_usuario,
        db
    )


# ==========================================
# ACTUALIZAR ASIGNACIÓN
# ==========================================

@router.put(
    "/{id_asignacion}",
    response_model=AsignacionRespuesta,
    dependencies=[Depends(verificar_csrf)]
)
def actualizar_asignacion(
    id_asignacion: int,
    datos: AsignacionActualizar,
    db: DBSession,
    usuario: UsuarioActual
):
    asignacion = obtener_asignacion_usuario(
        id_asignacion,
        usuario.id_usuario,
        db
    )

    cambios = datos.model_dump(
        exclude_unset=True
    )

    # Los vínculos y el período laboral son
    # inmutables para preservar el historial.
    campos_prohibidos = {
        "id_empleado",
        "id_local",
        "id_restaurante",
        "fecha_asignacion",
        "fecha_finalizacion",
        "activo"
    }

    if campos_prohibidos.intersection(cambios):
        raise HTTPException(
            status_code=422,
            detail=(
                "No se pueden modificar empleados, "
                "locales, fechas o estado mediante PUT. "
                "Finaliza la asignación y crea una nueva "
                "cuando cambie el período laboral."
            )
        )

    if not asignacion.activo:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede modificar una asignación "
                "histórica finalizada"
            )
        )

    campos_editables = {
        "turno",
        "observaciones"
    }

    for campo, valor in cambios.items():
        if campo not in campos_editables:
            raise HTTPException(
                status_code=422,
                detail=f"Campo no editable: {campo}"
            )

        setattr(asignacion, campo, valor)

    db.commit()
    db.refresh(asignacion)

    return asignacion


# ==========================================
# FINALIZAR ASIGNACIÓN
# ==========================================

@router.delete(
    "/{id_asignacion}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verificar_csrf)]
)
def finalizar_asignacion(
    id_asignacion: int,
    db: DBSession,
    usuario: UsuarioActual
):
    asignacion = obtener_asignacion_usuario(
        id_asignacion,
        usuario.id_usuario,
        db
    )

    if not asignacion.activo:
        raise HTTPException(
            status_code=409,
            detail="La asignación ya está finalizada"
        )

    ahora = fecha_actual()

    # Una fecha de cierre nunca debe preceder
    # a la fecha de inicio del período.
    if ahora < asignacion.fecha_asignacion:
        raise HTTPException(
            status_code=409,
            detail=(
                "La fecha de inicio es posterior a hoy. "
                "Revisa los datos de la asignación."
            )
        )

    asignacion.activo = False
    asignacion.fecha_finalizacion = ahora

    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
