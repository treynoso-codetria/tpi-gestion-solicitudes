"""Objetos parametro (Introduce Parameter Object).

Reemplazan las listas largas de parametros sueltos por objetos con nombre que
saben validarse a si mismos.
"""

from dataclasses import dataclass

from solicitudes.errores import DatosInvalidos
from solicitudes.modelo import Estudiante, Prioridad, Solicitud, TipoSolicitud
from solicitudes.validaciones import es_descripcion_valida, es_email_valido, es_legajo_valido


@dataclass(frozen=True)
class DatosEstudiante:
    legajo: str
    nombre: str
    apellido: str
    email: str
    carrera: str

    def validar(self) -> None:
        if not es_legajo_valido(self.legajo):
            raise DatosInvalidos("legajo invalido")
        if self.nombre.strip() == "" or self.apellido.strip() == "":
            raise DatosInvalidos("nombre y apellido son obligatorios")
        if not es_email_valido(self.email):
            raise DatosInvalidos("email invalido")

    def crear_estudiante(self) -> Estudiante:
        return Estudiante(self.legajo, self.nombre, self.apellido, self.email, self.carrera)


@dataclass(frozen=True)
class PedidoSolicitud:
    """Datos que ingresa el usuario para registrar una solicitud."""

    estudiante: DatosEstudiante
    tipo: str
    descripcion: str
    prioridad: str = ""  # vacio = se calcula segun el tipo

    def validar(self) -> None:
        """Valida TODO el pedido antes de modificar datos (corrige el defecto D2)."""
        self.estudiante.validar()
        if TipoSolicitud.desde_texto(self.tipo) is None:
            raise DatosInvalidos("tipo de solicitud invalido")
        if not es_descripcion_valida(self.descripcion):
            raise DatosInvalidos("la descripcion debe tener al menos 10 caracteres")
        if self.prioridad != "" and Prioridad.desde_texto(self.prioridad) is None:
            raise DatosInvalidos("prioridad invalida")

    def prioridad_efectiva(self) -> Prioridad:
        if self.prioridad == "":
            return TipoSolicitud(self.tipo).prioridad_por_defecto
        return Prioridad(self.prioridad)


@dataclass(frozen=True)
class FiltroSolicitudes:
    """Criterios de busqueda. Un campo vacio significa 'cualquiera'."""

    estado: str = ""
    tipo: str = ""
    legajo: str = ""
    prioridad: str = ""

    def validar(self) -> None:
        if self.tipo != "" and TipoSolicitud.desde_texto(self.tipo) is None:
            raise DatosInvalidos("tipo de solicitud invalido")

    def acepta(self, solicitud: Solicitud) -> bool:
        criterios = (
            (self.estado, solicitud.estado),
            (self.tipo, solicitud.tipo),
            (self.legajo, solicitud.legajo),
            (self.prioridad, solicitud.prioridad),
        )
        return all(buscado in ("", valor) for buscado, valor in criterios)
