"""Repositorio: traduce entre las entidades del dominio y el documento persistido.

Es el unico lugar que conoce el formato del archivo de datos. El formato se
mantuvo identico al de la version base, de modo que los archivos existentes
siguen funcionando.
"""

from typing import Protocol

from solicitudes.almacenamiento import Almacenamiento
from solicitudes.modelo import (
    Estado, Estudiante, Evento, Prioridad, Responsable, Solicitud, TipoSolicitud,
)

RESPONSABLES_INICIALES = (
    Responsable(1, "Laura Gomez", "Alumnado"),
    Responsable(2, "Martin Sosa", "Bedelia"),
    Responsable(3, "Carla Ruiz", "Coordinacion"),
    Responsable(4, "Diego Paz", "Tesoreria"),
)


class LectorSolicitudes(Protocol):
    """Interfaz de solo lectura (ISP): el reporte no necesita poder escribir."""

    def listar_solicitudes(self) -> list[Solicitud]: ...

    def listar_responsables(self) -> list[Responsable]: ...


class RepositorioSolicitudes:
    def __init__(self, almacenamiento: Almacenamiento):
        self._almacenamiento = almacenamiento
        documento = almacenamiento.cargar() or _documento_vacio()
        self._solicitudes = [_solicitud_desde_dict(d) for d in documento["solicitudes"]]
        self._estudiantes = [Estudiante(**d) for d in documento["estudiantes"]]
        self._responsables = [Responsable(**d) for d in documento["responsables"]]
        self._ultimo_id = documento["ultimo_id"]
        self._crear_responsables_iniciales_si_faltan()

    def _crear_responsables_iniciales_si_faltan(self) -> None:
        if not self._responsables:
            self._responsables = list(RESPONSABLES_INICIALES)
            self.guardar_cambios()

    # --- Lectura --------------------------------------------------------
    def listar_solicitudes(self) -> list[Solicitud]:
        return list(self._solicitudes)

    def listar_responsables(self) -> list[Responsable]:
        return list(self._responsables)

    def obtener_solicitud(self, id_solicitud: int) -> Solicitud | None:
        return next((s for s in self._solicitudes if s.id == id_solicitud), None)

    def obtener_responsable(self, id_responsable: int | None) -> Responsable | None:
        return next((r for r in self._responsables if r.id == id_responsable), None)

    def obtener_estudiante(self, legajo: str) -> Estudiante | None:
        return next((e for e in self._estudiantes if e.legajo == legajo), None)

    # --- Escritura ------------------------------------------------------
    def proximo_id(self) -> int:
        self._ultimo_id += 1
        return self._ultimo_id

    def agregar_solicitud(self, solicitud: Solicitud) -> None:
        self._solicitudes.append(solicitud)

    def agregar_estudiante(self, estudiante: Estudiante) -> None:
        self._estudiantes.append(estudiante)

    def guardar_cambios(self) -> None:
        self._almacenamiento.guardar({
            "solicitudes": [_solicitud_a_dict(s) for s in self._solicitudes],
            "estudiantes": [vars(e).copy() for e in self._estudiantes],
            "responsables": [vars(r).copy() for r in self._responsables],
            "ultimo_id": self._ultimo_id,
        })


def _documento_vacio() -> dict:
    return {"solicitudes": [], "estudiantes": [], "responsables": [], "ultimo_id": 0}


def _solicitud_desde_dict(datos: dict) -> Solicitud:
    return Solicitud(
        id=datos["id"],
        legajo=datos["legajo"],
        tipo=TipoSolicitud(datos["tipo"]),
        descripcion=datos["descripcion"],
        prioridad=Prioridad(datos["prioridad"]),
        estado=Estado(datos["estado"]),
        responsable_id=datos["responsable"],
        fecha=datos["fecha"],
        dias_sla=datos["dias_sla"],
        historial=[Evento(e["fecha"], e["evento"]) for e in datos["historial"]],
    )


def _solicitud_a_dict(solicitud: Solicitud) -> dict:
    return {
        "id": solicitud.id,
        "legajo": solicitud.legajo,
        "tipo": str(solicitud.tipo),
        "descripcion": solicitud.descripcion,
        "prioridad": str(solicitud.prioridad),
        "estado": str(solicitud.estado),
        "responsable": solicitud.responsable_id,
        "fecha": solicitud.fecha,
        "dias_sla": solicitud.dias_sla,
        "historial": [{"fecha": e.fecha, "evento": e.descripcion} for e in solicitud.historial],
    }
