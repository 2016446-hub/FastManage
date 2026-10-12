"""Ejecutar desde la raíz: python -m backend.init_db"""
from backend.database import Base, engine
from backend import models  # Registra las cinco tablas en Base.metadata.

def inicializar():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    inicializar()
    print("Tablas inicializadas. create_all no modifica tablas existentes.")
