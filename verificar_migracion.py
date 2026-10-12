
import sqlite3

conexion = sqlite3.connect(
    "data/fastmanage.db"
)

print("Índices de asignaciones:")

for indice in conexion.execute(
    "PRAGMA index_list('asignaciones_empleados')"
):
    print(indice)

print("\nComprobación de integridad:")

print(
    conexion.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]
)

print("\nAsignaciones conservadas:")

print(
    conexion.execute(
        "SELECT COUNT(*) FROM asignaciones_empleados"
    ).fetchone()[0]
)

conexion.close()
