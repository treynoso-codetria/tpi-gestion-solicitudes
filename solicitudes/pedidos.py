"""Objetos parametro (Introduce Parameter Object).

Reemplazan los 8 parametros sueltos de registrar_solicitud por dos objetos
con nombre y con la responsabilidad de validarse a si mismos.
"""

from dataclasses import dataclass

from solicitudes.modelo import Prioridad, TipoSolicitud
from solicitudes.validaciones import es_descripcion_valida, es_email_valido, es_legajo_valido


@dataclass(frozen=True)
class DatosEstudiante:
    legajo: str
    nombre: str
    apellido: str
    email: str
    carrera: str

    def error_de_validacion(self) -> str | None:
        if not es_legajo_valido(self.legajo):
            return "Error: legajo invalido"
        if self.nombre.strip() == "" or self.apellido.strip() == "":
            return "Error: nombre y apellido son obligatorios"
        if not es_email_valido(self.email):
            return "Error: email invalido"
        return None


@dataclass(frozen=True)
class PedidoSolicitud:
    """Datos que ingresa el usuario para registrar una solicitud."""

    estudiante: DatosEstudiante
    tipo: str
    descripcion: str
    prioridad: str = ""  # vacio = se calcula segun el tipo

    def error_de_validacion(self) -> str | None:
        """Valida TODO el pedido antes de modificar datos (corrige el defecto D2)."""
        error = self.estudiante.error_de_validacion()
        if error is not None:
            return error
        if TipoSolicitud.desde_texto(self.tipo) is None:
            return "Error: tipo de solicitud invalido"
        if not es_descripcion_valida(self.descripcion):
            return "Error: la descripcion debe tener al menos 10 caracteres"
        if self.prioridad != "" and Prioridad.desde_texto(self.prioridad) is None:
            return "Error: prioridad invalida"
        return None

    def prioridad_efectiva(self) -> Prioridad:
        if self.prioridad == "":
            return TipoSolicitud(self.tipo).prioridad_por_defecto
        return Prioridad(self.prioridad)
