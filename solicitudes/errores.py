"""Errores de negocio (Replace Error Code with Exception).

Antes cada operacion imprimia el error y devolvia -1, False o [] segun el
caso. Ahora la logica lanza una excepcion con el motivo y la capa de consola
decide como mostrarlo.
"""


class ErrorDeNegocio(Exception):
    """Operacion rechazada por una regla del dominio. El mensaje es para el usuario."""


class DatosInvalidos(ErrorDeNegocio):
    """Los datos ingresados no cumplen el formato esperado."""


class NoEncontrado(ErrorDeNegocio):
    """La entidad pedida no existe."""


class TransicionInvalida(ErrorDeNegocio):
    """El cambio de estado o la asignacion no esta permitido en el estado actual."""
