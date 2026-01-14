try:
    from app.database import init_db
except Exception as e:
    import sys
    print("Error: no se puede importar 'app.database'. Asegúrate de ejecutar este script desde la raíz del proyecto o que PYTHONPATH incluya la raíz del repositorio.")
    print("Detalle:", e)
    sys.exit(1)


if __name__ == "__main__":
    init_db()
    print("fields_service: sqlite DB initialized")
