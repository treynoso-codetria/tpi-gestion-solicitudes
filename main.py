import sys

from gestor import GestorSolicitudes
from solicitudes.almacenamiento import AlmacenamientoJSON, ArchivoDeDatosDanado

ARCHIVO_DATOS = "solicitudes.json"


def main():
    try:
        gestor = GestorSolicitudes(AlmacenamientoJSON(ARCHIVO_DATOS))
    except ArchivoDeDatosDanado as error:
        print(f"Error: {error}")
        return 1
    gestor.menu()
    return 0


if __name__ == "__main__":
    sys.exit(main())
