"""Vocabulario del dominio: estados, tipos y prioridades de una solicitud.

Cada regla que antes estaba repartida en cadenas if/elif (prioridad por tipo,
plazo por prioridad, transiciones de estado) vive ahora junto al concepto al
que pertenece. Agregar un tipo, una prioridad o un estado nuevo se hace en
este archivo, sin tocar el resto del sistema (principio Abierto/Cerrado).
"""

from dataclasses import dataclass, field
from enum import StrEnum

from solicitudes.errores import TransicionInvalida


class Prioridad(StrEnum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"

    @property
    def dias_de_plazo(self) -> int:
        return _DIAS_DE_PLAZO[self]

    @classmethod
    def desde_texto(cls, texto: str) -> "Prioridad | None":
        return cls.__members__.get(texto)


class TipoSolicitud(StrEnum):
    CERTIFICADO = "CERTIFICADO"
    EQUIVALENCIA = "EQUIVALENCIA"
    CAMBIO_COMISION = "CAMBIO_COMISION"
    RECLAMO_NOTA = "RECLAMO_NOTA"
    BAJA = "BAJA"

    @property
    def prioridad_por_defecto(self) -> Prioridad:
        return _PRIORIDAD_POR_TIPO[self]

    @classmethod
    def desde_texto(cls, texto: str) -> "TipoSolicitud | None":
        return cls.__members__.get(texto)


class Estado(StrEnum):
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    RESUELTA = "RESUELTA"
    RECHAZADA = "RECHAZADA"

    @property
    def es_final(self) -> bool:
        return not _TRANSICIONES[self]

    def puede_pasar_a(self, destino: "Estado") -> bool:
        return destino in _TRANSICIONES[self]

    @classmethod
    def desde_texto(cls, texto: str) -> "Estado | None":
        return cls.__members__.get(texto)


_DIAS_DE_PLAZO = {
    Prioridad.ALTA: 3,
    Prioridad.MEDIA: 7,
    Prioridad.BAJA: 15,
}

_PRIORIDAD_POR_TIPO = {
    TipoSolicitud.RECLAMO_NOTA: Prioridad.ALTA,
    TipoSolicitud.BAJA: Prioridad.ALTA,
    TipoSolicitud.EQUIVALENCIA: Prioridad.MEDIA,
    TipoSolicitud.CAMBIO_COMISION: Prioridad.MEDIA,
    TipoSolicitud.CERTIFICADO: Prioridad.BAJA,
}

_TRANSICIONES = {
    Estado.PENDIENTE: frozenset({Estado.EN_REVISION, Estado.RECHAZADA}),
    Estado.EN_REVISION: frozenset({Estado.RESUELTA, Estado.RECHAZADA}),
    Estado.RESUELTA: frozenset(),
    Estado.RECHAZADA: frozenset(),
}


# ---------------------------------------------------------------------------
# Entidades (Replace Data Value with Object): antes eran diccionarios sueltos.
# ---------------------------------------------------------------------------

@dataclass
class Estudiante:
    legajo: str
    nombre: str
    apellido: str
    email: str
    carrera: str


@dataclass(frozen=True)
class Responsable:
    id: int
    nombre: str
    area: str

    @property
    def descripcion(self) -> str:
        return f"{self.nombre} ({self.area})"


@dataclass(frozen=True)
class Evento:
    fecha: str
    descripcion: str


@dataclass
class Solicitud:
    id: int
    legajo: str
    tipo: TipoSolicitud
    descripcion: str
    prioridad: Prioridad
    estado: Estado
    responsable_id: int | None
    fecha: str
    dias_sla: int
    historial: list[Evento] = field(default_factory=list)

    @property
    def esta_finalizada(self) -> bool:
        return self.estado.es_final

    def registrar_evento(self, fecha: str, descripcion: str) -> None:
        self.historial.append(Evento(fecha, descripcion))

    def asignar(self, responsable: Responsable, fecha: str) -> None:
        self._exigir_abierta()
        self.responsable_id = responsable.id
        self.registrar_evento(fecha, f"Asignada a {responsable.descripcion}")

    def cambiar_estado(self, destino: Estado, fecha: str) -> None:
        self._exigir_abierta()
        if not self.estado.puede_pasar_a(destino):
            raise TransicionInvalida(f"transicion no permitida de {self.estado} a {destino}")
        if destino is Estado.EN_REVISION and self.responsable_id is None:
            raise TransicionInvalida("debe asignar un responsable antes de pasar a revision")
        self.registrar_evento(fecha, f"Cambio de {self.estado} a {destino}")
        self.estado = destino

    def _exigir_abierta(self) -> None:
        if self.esta_finalizada:
            raise TransicionInvalida(f"la solicitud {self.id} ya esta finalizada")
