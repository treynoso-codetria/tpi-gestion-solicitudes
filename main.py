"""Punto de entrada: arma las dependencias y arranca la consola."""

import sys

from solicitudes.almacenamiento import AlmacenamientoJSON, ArchivoDeDatosDanado
from solicitudes.cli import ConsolaSolicitudes
from solicitudes.reporte import GeneradorReporte
from solicitudes.repositorio import RepositorioSolicitudes
from solicitudes.servicio import ServicioSolicitudes

ARCHIVO_DATOS = "solicitudes.json"


def crear_consola(ruta_datos: str = ARCHIVO_DATOS) -> ConsolaSolicitudes:
    repositorio = RepositorioSolicitudes(AlmacenamientoJSON(ruta_datos))
    return ConsolaSolicitudes(ServicioSolicitudes(repositorio), GeneradorReporte(repositorio))


def main() -> int:
    try:
        consola = crear_consola()
    except ArchivoDeDatosDanado as error:
        print(f"Error: {error}")
        return 1
    consola.ejecutar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
