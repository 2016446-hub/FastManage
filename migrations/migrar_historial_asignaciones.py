
from datetime import datetime
from pathlib import Path
import sqlite3


# ==========================================
# RUTAS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "fastmanage.db"

BACKUP_DIR = BASE_DIR / "data" / "backups"

TABLA = "asignaciones_empleados"

INDICE_NUEVO = "uq_asignacion_activa_empleado_local"


# ==========================================
# DEFINICIÓN DE LA NUEVA TABLA
# ==========================================

CREAR_TABLA = """
CREATE TABLE asignaciones_empleados_nueva (
    id_asignacion INTEGER NOT NULL,
    id_empleado INTEGER NOT NULL,
    id_local INTEGER NOT NULL,
    id_restaurante INTEGER NOT NULL,
    fecha_asignacion DATETIME NOT NULL,
    fecha_finalizacion DATETIME,
    turno VARCHAR(50),
    observaciones TEXT,
    activo BOOLEAN NOT NULL,

    PRIMARY KEY (id_asignacion),

    FOREIGN KEY (id_empleado, id_restaurante)
        REFERENCES empleados (id_empleado, id_restaurante)
        ON DELETE CASCADE,

    FOREIGN KEY (id_local, id_restaurante)
        REFERENCES locales (id_local, id_restaurante)
        ON DELETE CASCADE,

    CONSTRAINT ck_asignacion_activo
        CHECK (activo IN (0, 1))
)
"""

COLUMNAS = [
    "id_asignacion",
    "id_empleado",
    "id_local",
    "id_restaurante",
    "fecha_asignacion",
    "fecha_finalizacion",
    "turno",
    "observaciones",
    "activo"
]


# ==========================================
# COMPROBACIONES PREVIAS
# ==========================================

def comprobar_estructura(conexion):
    registro = conexion.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (TABLA,)
    ).fetchone()

    if registro is None:
        raise RuntimeError(
            "No existe la tabla de asignaciones."
        )

    definicion = registro[0].lower()

    columnas_actuales = [
        fila[1]
        for fila in conexion.execute(
            f"PRAGMA table_info({TABLA})"
        )
    ]

    if columnas_actuales != COLUMNAS:
        raise RuntimeError(
            "La estructura de columnas no coincide. "
            "Se cancela la migración."
        )

    if "uq_empleado_local" not in definicion:
        raise RuntimeError(
            "No se encontró la restricción antigua. "
            "Es posible que la tabla ya esté migrada."
        )

    if "ck_asignacion_activo" not in definicion:
        raise RuntimeError(
            "No se encontró la restricción CHECK esperada."
        )

    claves = list(
        conexion.execute(
            f"PRAGMA foreign_key_list({TABLA})"
        )
    )

    if len(claves) != 4:
        raise RuntimeError(
            "Las claves foráneas no coinciden "
            "con la estructura esperada."
        )

    referencias = {
        (fila[2], fila[3], fila[4], fila[6])
        for fila in claves
    }

    esperadas = {
        ("empleados", "id_empleado", "id_empleado", "CASCADE"),
        ("empleados", "id_restaurante", "id_restaurante", "CASCADE"),
        ("locales", "id_local", "id_local", "CASCADE"),
        ("locales", "id_restaurante", "id_restaurante", "CASCADE")
    }

    if referencias != esperadas:
        raise RuntimeError(
            "Las referencias foráneas no coinciden."
        )

    # No reconstruir si existen otras tablas
    # que dependen de asignaciones_empleados.
    tablas_dependientes = []

    for (nombre,) in conexion.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
          AND name != ?
        """,
        (TABLA,)
    ):
        for fk in conexion.execute(
            f'PRAGMA foreign_key_list("{nombre}")'
        ):
            if fk[2] == TABLA:
                tablas_dependientes.append(nombre)

    if tablas_dependientes:
        raise RuntimeError(
            "Existen tablas dependientes: "
            + ", ".join(tablas_dependientes)
        )

    # Comprobar que no hay índices adicionales
    # cuya definición debamos conservar.
    indices = list(
        conexion.execute(
            f"PRAGMA index_list({TABLA})"
        )
    )

    if len(indices) != 1:
        raise RuntimeError(
            "Se encontraron índices adicionales. "
            "Es necesario revisarlos antes de migrar."
        )

    indice = indices[0]

    if indice[2] != 1 or indice[3] != "u":
        raise RuntimeError(
            "El índice existente no corresponde "
            "a la restricción UNIQUE esperada."
        )

    columnas_indice = [
        fila[2]
        for fila in conexion.execute(
            f'PRAGMA index_info("{indice[1]}")'
        )
    ]

    if columnas_indice != [
        "id_empleado",
        "id_local"
    ]:
        raise RuntimeError(
            "El índice UNIQUE no coincide."
        )


def comprobar_integridad(conexion):
    resultado = conexion.execute(
        "PRAGMA integrity_check"
    ).fetchone()

    if resultado[0] != "ok":
        raise RuntimeError(
            "La base de datos presenta errores de integridad."
        )

    errores_fk = list(
        conexion.execute(
            "PRAGMA foreign_key_check"
        )
    )

    if errores_fk:
        raise RuntimeError(
            "Existen referencias foráneas inválidas."
        )


# ==========================================
# COPIA DE SEGURIDAD
# ==========================================

def crear_respaldo(conexion):
    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    marca = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    destino = BACKUP_DIR / (
        f"fastmanage_antes_historial_{marca}.db"
    )

    with sqlite3.connect(destino) as respaldo:
        conexion.backup(respaldo)

    print("Copia de seguridad:", destino)

    return destino


# ==========================================
# MIGRACIÓN
# ==========================================

def ejecutar_migracion():
    if not DB_PATH.is_file():
        raise RuntimeError(
            f"No se encontró la base de datos: {DB_PATH}"
        )

    conexion = sqlite3.connect(
        DB_PATH,
        timeout=10
    )

    try:
        comprobar_integridad(conexion)
        comprobar_estructura(conexion)

        cantidad_original = conexion.execute(
            f"SELECT COUNT(*) FROM {TABLA}"
        ).fetchone()[0]

        print(
            "Asignaciones existentes:",
            cantidad_original
        )

        crear_respaldo(conexion)

        # SQLite exige desactivar las FK antes
        # de iniciar la transacción de reconstrucción.
        conexion.execute(
            "PRAGMA foreign_keys = OFF"
        )

        conexion.execute("BEGIN IMMEDIATE")

        try:
            conexion.execute(CREAR_TABLA)

            columnas_sql = ", ".join(COLUMNAS)

            conexion.execute(
                f"""
                INSERT INTO asignaciones_empleados_nueva
                    ({columnas_sql})
                SELECT {columnas_sql}
                FROM asignaciones_empleados
                """
            )

            cantidad_copiada = conexion.execute(
                """
                SELECT COUNT(*)
                FROM asignaciones_empleados_nueva
                """
            ).fetchone()[0]

            if cantidad_copiada != cantidad_original:
                raise RuntimeError(
                    "La cantidad de registros no coincide."
                )

            conexion.execute(
                "DROP TABLE asignaciones_empleados"
            )

            conexion.execute(
                """
                ALTER TABLE asignaciones_empleados_nueva
                RENAME TO asignaciones_empleados
                """
            )

            conexion.execute(
                """
                CREATE UNIQUE INDEX
                    uq_asignacion_activa_empleado_local
                ON asignaciones_empleados (
                    id_empleado,
                    id_local
                )
                WHERE activo = 1
                """
            )

            errores_fk = list(
                conexion.execute(
                    "PRAGMA foreign_key_check"
                )
            )

            if errores_fk:
                raise RuntimeError(
                    "La migración produjo referencias inválidas."
                )

            resultado = conexion.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if resultado[0] != "ok":
                raise RuntimeError(
                    "Falló la comprobación de integridad."
                )

            conexion.commit()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.execute(
                "PRAGMA foreign_keys = ON"
            )

        print("Migración completada correctamente.")
        print(
            "Asignaciones conservadas:",
            cantidad_copiada
        )
        print(
            "Índice creado:",
            INDICE_NUEVO
        )

    finally:
        conexion.close()


if __name__ == "__main__":
    ejecutar_migracion()
