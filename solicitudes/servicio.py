"""Casos de uso del sistema.

No lee del teclado ni imprime: recibe datos, aplica las reglas y devuelve
resultados o lanza ErrorDeNegocio. Las dependencias (repositorio y reloj) se
reciben por constructor, lo que permite probarlo sin disco ni fecha real.
"""

from collections.abc import Callable
from datetime import date

from solicitudes.errores import DatosInvalidos, NoEncontrado, TransicionInvalida
from solicitudes.modelo import Estado, Estudiante, Responsable, Solicitud, TipoSolicitud
from solicitudes.pedidos import DatosEstudiante, FiltroSolicitudes, PedidoSolicitud
from solicitudes.repositorio import RepositorioSolicitudes
from solicitudes.validaciones import es_email_valido


class ServicioSolicitudes:
    def __init__(self, repositorio: RepositorioSolicitudes, reloj: Callable[[], date] = date.today):
        self._repositorio = repositorio
        self._reloj = reloj

    # --- Casos de uso ----------------------------------------------------
    def registrar(self, pedido: PedidoSolicitud) -> Solicitud:
        pedido.validar()
        self._registrar_o_actualizar_estudiante(pedido.estudiante)
        prioridad = pedido.prioridad_efectiva()
        hoy = self._hoy()
        solicitud = Solicitud(
            id=self._repositorio.proximo_id(),
            legajo=pedido.estudiante.legajo,
            tipo=TipoSolicitud(pedido.tipo),
            descripcion=pedido.descripcion,
            prioridad=prioridad,
            estado=Estado.PENDIENTE,
            responsable_id=None,
            fecha=hoy,
            dias_sla=prioridad.dias_de_plazo,
        )
        solicitud.registrar_evento(hoy, f"Creada en estado {Estado.PENDIENTE}")
        self._repositorio.agregar_solicitud(solicitud)
        self._repositorio.guardar_cambios()
        return solicitud

    def cambiar_estado(self, id_solicitud: int, texto_estado: str) -> Solicitud:
        solicitud = self._obtener_solicitud(id_solicitud)
        destino = Estado.desde_texto(texto_estado)
        if destino is None:
            raise DatosInvalidos("estado invalido")
        solicitud.cambiar_estado(destino, self._hoy())
        self._repositorio.guardar_cambios()
        return solicitud

    def asignar_responsable(self, id_solicitud: int, id_responsable: int) -> Responsable:
        solicitud = self._obtener_solicitud(id_solicitud)
        if solicitud.esta_finalizada:
            raise TransicionInvalida(f"la solicitud {id_solicitud} ya esta finalizada")
        responsable = self._repositorio.obtener_responsable(id_responsable)
        if responsable is None:
            raise NoEncontrado(f"no existe el responsable {id_responsable}")
        solicitud.asignar(responsable, self._hoy())
        self._repositorio.guardar_cambios()
        return responsable

    def actualizar_email(self, legajo: str, email: str) -> Estudiante:
        if not es_email_valido(email):
            raise DatosInvalidos("email invalido")
        estudiante = self._repositorio.obtener_estudiante(legajo)
        if estudiante is None:
            raise NoEncontrado(f"no existe el estudiante {legajo}")
        estudiante.email = email
        self._repositorio.guardar_cambios()
        return estudiante

    def buscar(self, filtro: FiltroSolicitudes) -> list[Solicitud]:
        filtro.validar()
        return [s for s in self._repositorio.listar_solicitudes() if filtro.acepta(s)]

    def listar_responsables(self) -> list[Responsable]:
        return self._repositorio.listar_responsables()

    def obtener_responsable(self, id_responsable: int | None) -> Responsable | None:
        return self._repositorio.obtener_responsable(id_responsable)

    # --- Auxiliares --------------------------------------------------------
    def _hoy(self) -> str:
        return self._reloj().isoformat()

    def _obtener_solicitud(self, id_solicitud: int) -> Solicitud:
        solicitud = self._repositorio.obtener_solicitud(id_solicitud)
        if solicitud is None:
            raise NoEncontrado(f"no existe la solicitud {id_solicitud}")
        return solicitud

    def _registrar_o_actualizar_estudiante(self, datos: DatosEstudiante) -> None:
        estudiante = self._repositorio.obtener_estudiante(datos.legajo)
        if estudiante is not None:
            estudiante.email = datos.email
            return
        self._repositorio.agregar_estudiante(
            Estudiante(datos.legajo, datos.nombre, datos.apellido, datos.email, datos.carrera))
