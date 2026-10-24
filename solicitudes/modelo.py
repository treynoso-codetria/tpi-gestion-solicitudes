"""Vocabulario del dominio: estados, tipos y prioridades de una solicitud.

Cada regla que antes estaba repartida en cadenas if/elif (prioridad por tipo,
plazo por prioridad, transiciones de estado) vive ahora junto al concepto al
que pertenece. Agregar un tipo, una prioridad o un estado nuevo se hace en
este archivo, sin tocar el resto del sistema (principio Abierto/Cerrado).
"""

from enum import StrEnum


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
