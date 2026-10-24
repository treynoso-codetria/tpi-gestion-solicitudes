"""Datos de prueba sinteticos reutilizables (ningun dato real de personas)."""

from datetime import date

from solicitudes.almacenamiento import AlmacenamientoEnMemoria
from solicitudes.pedidos import DatosEstudiante, PedidoSolicitud
from solicitudes.repositorio import RepositorioSolicitudes
from solicitudes.servicio import ServicioSolicitudes

FECHA_FIJA = date(2026, 10, 24)


def reloj_fijo():
    return FECHA_FIJA


def estudiante(legajo="10234", email="ana.lopez@mail.com", nombre="Ana", apellido="Lopez"):
    return DatosEstudiante(legajo, nombre, apellido, email, "Tecnicatura en Programacion")


def pedido(tipo="CERTIFICADO", descripcion="Certificado de alumno regular", prioridad="", **datos_estudiante):
    return PedidoSolicitud(estudiante(**datos_estudiante), tipo, descripcion, prioridad)


def servicio_en_memoria():
    """Devuelve (servicio, repositorio, almacenamiento) sin tocar el disco."""
    almacenamiento = AlmacenamientoEnMemoria()
    repositorio = RepositorioSolicitudes(almacenamiento)
    return ServicioSolicitudes(repositorio, reloj=reloj_fijo), repositorio, almacenamiento
