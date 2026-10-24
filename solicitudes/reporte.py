"""Reporte resumido de solicitudes (Move Method desde GestorSolicitudes).

Depende solo de LectorSolicitudes (ISP): no puede modificar datos. Devuelve el
texto del reporte en lugar de imprimirlo, asi puede mostrarse en consola,
guardarse en un archivo o verificarse en un test.
"""

from collections.abc import Callable

from solicitudes.modelo import Estado, Solicitud, TipoSolicitud
from solicitudes.repositorio import LectorSolicitudes

ANCHO_RESPONSABLE = 28


class GeneradorReporte:
    def __init__(self, lector: LectorSolicitudes):
        self._lector = lector

    def generar(self) -> str:
        solicitudes = self._lector.listar_solicitudes()
        lineas = ["===== REPORTE DE SOLICITUDES =====", f"Total de solicitudes: {len(solicitudes)}"]
        lineas += self._seccion_por_estado(solicitudes)
        lineas += self._seccion_por_tipo(solicitudes)
        lineas += self._seccion_por_responsable(solicitudes)
        lineas.append("==================================")
        return "\n".join(lineas)

    @staticmethod
    def _seccion_por_estado(solicitudes: list[Solicitud]) -> list[str]:
        lineas = ["--- Por estado ---"]
        for estado in Estado:
            cantidad = _contar(solicitudes, lambda s, e=estado: s.estado is e)
            lineas.append(f"{estado:<12}{cantidad:>4}  ({_porcentaje(cantidad, len(solicitudes))}%)")
        return lineas

    @staticmethod
    def _seccion_por_tipo(solicitudes: list[Solicitud]) -> list[str]:
        lineas = ["--- Por tipo ---"]
        for tipo in TipoSolicitud:
            cantidad = _contar(solicitudes, lambda s, t=tipo: s.tipo is t)
            lineas.append(f"{tipo:<16}{cantidad:>4}")
        return lineas

    def _seccion_por_responsable(self, solicitudes: list[Solicitud]) -> list[str]:
        abiertas = [s for s in solicitudes if not s.esta_finalizada]
        lineas = ["--- Carga por responsable (abiertas) ---"]
        for responsable in self._lector.listar_responsables():
            cantidad = _contar(abiertas, lambda s, r=responsable: s.responsable_id == r.id)
            lineas.append(f"{responsable.descripcion:<{ANCHO_RESPONSABLE}}{cantidad:>4}")
        sin_responsable = _contar(abiertas, lambda s: s.responsable_id is None)
        lineas.append(f"{'Sin responsable':<{ANCHO_RESPONSABLE}}{sin_responsable:>4}")
        return lineas


def _contar(solicitudes: list[Solicitud], condicion: Callable[[Solicitud], bool]) -> int:
    return sum(1 for solicitud in solicitudes if condicion(solicitud))


def _porcentaje(cantidad: int, total: int) -> float:
    # Antes: division por cero con total = 0 (defecto D1).
    if total == 0:
        return 0.0
    return round(cantidad * 100 / total, 1)
