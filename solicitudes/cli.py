"""Interfaz de consola (Extract Class: presentacion separada de la logica).

Es la unica parte del sistema que lee del teclado y escribe en pantalla. La
entrada y la salida se inyectan para poder probarla sin una terminal real.
"""

from collections.abc import Callable

from solicitudes.errores import ErrorDeNegocio
from solicitudes.modelo import Solicitud
from solicitudes.pedidos import DatosEstudiante, FiltroSolicitudes, PedidoSolicitud
from solicitudes.reporte import GeneradorReporte
from solicitudes.servicio import ServicioSolicitudes

MENU = """
=== GESTION DE SOLICITUDES ACADEMICAS ===
1. Registrar solicitud
2. Cambiar estado
3. Asignar responsable
4. Buscar / filtrar solicitudes
5. Reporte
6. Listar responsables
7. Actualizar email de estudiante
0. Salir"""

ENCABEZADO_LISTADO = "ID  LEGAJO  TIPO            PRIOR. ESTADO       RESPONSABLE"


class ConsolaSolicitudes:
    def __init__(self, servicio: ServicioSolicitudes, reporte: GeneradorReporte,
                 leer: Callable[[str], str] = input, escribir: Callable[[str], None] = print):
        self._servicio = servicio
        self._reporte = reporte
        self._leer = leer
        self._escribir = escribir
        self._acciones = {
            "1": self._registrar,
            "2": self._cambiar_estado,
            "3": self._asignar_responsable,
            "4": self._buscar,
            "5": self._mostrar_reporte,
            "6": self._listar_responsables,
            "7": self._actualizar_email,
        }

    def ejecutar(self) -> None:
        while True:
            self._escribir(MENU)
            opcion = self._leer("Opcion: ").strip()
            if opcion == "0":
                self._escribir("Hasta luego")
                return
            accion = self._acciones.get(opcion)
            if accion is None:
                self._escribir("Opcion invalida")
                continue
            try:
                accion()
            except ErrorDeNegocio as error:
                self._escribir(f"Error: {error}")

    # --- Opciones del menu ------------------------------------------------
    def _registrar(self) -> None:
        estudiante = DatosEstudiante(
            legajo=self._texto("Legajo: "),
            nombre=self._texto("Nombre: "),
            apellido=self._texto("Apellido: "),
            email=self._texto("Email: "),
            carrera=self._texto("Carrera: "),
        )
        pedido = PedidoSolicitud(
            estudiante=estudiante,
            tipo=self._codigo("Tipo (CERTIFICADO/EQUIVALENCIA/CAMBIO_COMISION/RECLAMO_NOTA/BAJA): "),
            descripcion=self._texto("Descripcion: "),
            prioridad=self._codigo("Prioridad (BAJA/MEDIA/ALTA, vacio = automatica): "),
        )
        solicitud = self._servicio.registrar(pedido)
        self._escribir(f"Solicitud registrada con ID {solicitud.id} "
                       f"(prioridad {solicitud.prioridad}, plazo {solicitud.dias_sla} dias)")

    def _cambiar_estado(self) -> None:
        id_solicitud = self._entero("ID de solicitud: ")
        if id_solicitud is None:
            return
        texto_estado = self._codigo("Nuevo estado (EN_REVISION/RESUELTA/RECHAZADA): ")
        solicitud = self._servicio.cambiar_estado(id_solicitud, texto_estado)
        self._escribir(f"Solicitud {solicitud.id} ahora esta en estado {solicitud.estado}")

    def _asignar_responsable(self) -> None:
        id_solicitud = self._entero("ID de solicitud: ")
        if id_solicitud is None:
            return
        self._listar_responsables()
        id_responsable = self._entero("ID de responsable: ")
        if id_responsable is None:
            return
        responsable = self._servicio.asignar_responsable(id_solicitud, id_responsable)
        self._escribir(f"Solicitud {id_solicitud} asignada a {responsable.descripcion}")

    def _buscar(self) -> None:
        filtro = FiltroSolicitudes(
            estado=self._codigo("Estado (vacio = todos): "),
            tipo=self._codigo("Tipo (vacio = todos): "),
            legajo=self._texto("Legajo (vacio = todos): "),
            prioridad=self._codigo("Prioridad (vacio = todas): "),
        )
        encontradas = self._servicio.buscar(filtro)
        if not encontradas:
            self._escribir("No se encontraron solicitudes")
            return
        self._escribir(ENCABEZADO_LISTADO)
        for solicitud in encontradas:
            self._escribir(self._fila(solicitud))

    def _mostrar_reporte(self) -> None:
        self._escribir(self._reporte.generar())

    def _listar_responsables(self) -> None:
        for responsable in self._servicio.listar_responsables():
            self._escribir(f"{responsable.id} - {responsable.descripcion}")

    def _actualizar_email(self) -> None:
        legajo = self._texto("Legajo: ")
        email = self._texto("Nuevo email: ")
        self._servicio.actualizar_email(legajo, email)
        self._escribir(f"Email actualizado para el legajo {legajo}")

    # --- Auxiliares de entrada/salida -----------------------------------
    def _fila(self, solicitud: Solicitud) -> str:
        responsable = self._servicio.obtener_responsable(solicitud.responsable_id)
        nombre = responsable.nombre if responsable is not None else "-"
        return (f"{solicitud.id:<4}{solicitud.legajo:<8}{solicitud.tipo:<16}"
                f"{solicitud.prioridad:<7}{solicitud.estado:<13}{nombre}")

    def _texto(self, mensaje: str) -> str:
        return self._leer(mensaje).strip()

    def _codigo(self, mensaje: str) -> str:
        return self._texto(mensaje).upper()

    def _entero(self, mensaje: str) -> int | None:
        try:
            return int(self._leer(mensaje))
        except ValueError:
            self._escribir("Error: ID invalido")
            return None
