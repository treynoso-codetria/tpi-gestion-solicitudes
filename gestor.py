from datetime import datetime

from solicitudes.almacenamiento import Almacenamiento
from solicitudes.errores import ErrorDeNegocio
from solicitudes.modelo import Estado, Estudiante, Solicitud, TipoSolicitud
from solicitudes.pedidos import DatosEstudiante, PedidoSolicitud
from solicitudes.reporte import GeneradorReporte
from solicitudes.repositorio import RepositorioSolicitudes
from solicitudes.validaciones import es_email_valido


class GestorSolicitudes:
    # clase principal del sistema

    def __init__(self, almacenamiento: Almacenamiento):
        self.repositorio = RepositorioSolicitudes(almacenamiento)
        self.generador_reporte = GeneradorReporte(self.repositorio)

    @staticmethod
    def _fecha_hoy():
        return datetime.now().strftime("%Y-%m-%d")

    def _registrar_o_actualizar_estudiante(self, datos: DatosEstudiante):
        estudiante = self.repositorio.obtener_estudiante(datos.legajo)
        if estudiante is not None:
            estudiante.email = datos.email
            return
        self.repositorio.agregar_estudiante(Estudiante(
            datos.legajo, datos.nombre, datos.apellido, datos.email, datos.carrera))

    # ---------------------------------------------------------------
    # Operaciones
    # ---------------------------------------------------------------
    def registrar_solicitud(self, pedido: PedidoSolicitud):
        error = pedido.error_de_validacion()
        if error is not None:
            print(error)
            return -1

        self._registrar_o_actualizar_estudiante(pedido.estudiante)
        prioridad = pedido.prioridad_efectiva()
        solicitud = Solicitud(
            id=self.repositorio.proximo_id(),
            legajo=pedido.estudiante.legajo,
            tipo=TipoSolicitud(pedido.tipo),
            descripcion=pedido.descripcion,
            prioridad=prioridad,
            estado=Estado.PENDIENTE,
            responsable_id=None,
            fecha=self._fecha_hoy(),
            dias_sla=prioridad.dias_de_plazo,
        )
        solicitud.registrar_evento(self._fecha_hoy(), "Creada en estado PENDIENTE")
        self.repositorio.agregar_solicitud(solicitud)
        self.repositorio.guardar_cambios()
        print(f"Solicitud registrada con ID {solicitud.id} (prioridad {prioridad}, "
              f"plazo {solicitud.dias_sla} dias)")
        return solicitud.id

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        solicitud = self.repositorio.obtener_solicitud(id_solicitud)
        if solicitud is None:
            print("Error: no existe la solicitud " + str(id_solicitud))
            return False
        destino = Estado.desde_texto(nuevo_estado)
        if destino is None:
            print("Error: estado invalido")
            return False
        try:
            solicitud.cambiar_estado(destino, self._fecha_hoy())
        except ErrorDeNegocio as error:
            print(f"Error: {error}")
            return False
        self.repositorio.guardar_cambios()
        print(f"Solicitud {id_solicitud} ahora esta en estado {destino}")
        return True

    def asignar_responsable(self, id_solicitud, id_responsable):
        solicitud = self.repositorio.obtener_solicitud(id_solicitud)
        if solicitud is None:
            print("Error: no existe la solicitud " + str(id_solicitud))
            return False
        if solicitud.esta_finalizada:
            print("Error: la solicitud " + str(id_solicitud) + " ya esta finalizada")
            return False
        responsable = self.repositorio.obtener_responsable(id_responsable)
        if responsable is None:
            print("Error: no existe el responsable " + str(id_responsable))
            return False
        solicitud.asignar(responsable, self._fecha_hoy())
        self.repositorio.guardar_cambios()
        print(f"Solicitud {id_solicitud} asignada a {responsable.descripcion}")
        return True

    def actualizar_email(self, legajo, email):
        if not es_email_valido(email):
            print("Error: email invalido")
            return False
        estudiante = self.repositorio.obtener_estudiante(legajo)
        if estudiante is None:
            print("Error: no existe el estudiante " + legajo)
            return False
        estudiante.email = email
        self.repositorio.guardar_cambios()
        print("Email actualizado para el legajo " + legajo)
        return True

    @staticmethod
    def _cumple_filtros(solicitud, estado, tipo, legajo, prioridad):
        filtros = {"estado": estado, "tipo": tipo, "legajo": legajo, "prioridad": prioridad}
        return all(valor == "" or getattr(solicitud, campo) == valor for campo, valor in filtros.items())

    def buscar(self, estado, tipo, legajo, prioridad):
        if tipo != "" and TipoSolicitud.desde_texto(tipo) is None:
            print("Error: tipo de solicitud invalido")
            return []
        encontradas = [s for s in self.repositorio.listar_solicitudes()
                       if self._cumple_filtros(s, estado, tipo, legajo, prioridad)]
        if len(encontradas) == 0:
            print("No se encontraron solicitudes")
            return encontradas
        print("ID  LEGAJO  TIPO            PRIOR. ESTADO       RESPONSABLE")
        for solicitud in encontradas:
            responsable = self.repositorio.obtener_responsable(solicitud.responsable_id)
            nombre_responsable = responsable.nombre if responsable is not None else "-"
            print(str(solicitud.id).ljust(4) + solicitud.legajo.ljust(8) + solicitud.tipo.ljust(16)
                  + solicitud.prioridad.ljust(7) + solicitud.estado.ljust(13) + nombre_responsable)
        return encontradas

    def reporte(self):
        print(self.generador_reporte.generar())

    def listar_responsables(self):
        for responsable in self.repositorio.listar_responsables():
            print(f"{responsable.id} - {responsable.descripcion}")

    @staticmethod
    def _pedir_entero(mensaje):
        try:
            return int(input(mensaje))
        except ValueError:
            print("Error: ID invalido")
            return None

    def _opcion_registrar(self):
        estudiante = DatosEstudiante(
            legajo=input("Legajo: ").strip(),
            nombre=input("Nombre: ").strip(),
            apellido=input("Apellido: ").strip(),
            email=input("Email: ").strip(),
            carrera=input("Carrera: ").strip(),
        )
        pedido = PedidoSolicitud(
            estudiante=estudiante,
            tipo=input("Tipo (CERTIFICADO/EQUIVALENCIA/CAMBIO_COMISION/RECLAMO_NOTA/BAJA): ").strip().upper(),
            descripcion=input("Descripcion: ").strip(),
            prioridad=input("Prioridad (BAJA/MEDIA/ALTA, vacio = automatica): ").strip().upper(),
        )
        self.registrar_solicitud(pedido)

    def _opcion_cambiar_estado(self):
        id_solicitud = self._pedir_entero("ID de solicitud: ")
        if id_solicitud is None:
            return
        nuevo_estado = input("Nuevo estado (EN_REVISION/RESUELTA/RECHAZADA): ").strip().upper()
        self.cambiar_estado(id_solicitud, nuevo_estado)

    def _opcion_asignar(self):
        id_solicitud = self._pedir_entero("ID de solicitud: ")
        if id_solicitud is None:
            return
        self.listar_responsables()
        id_responsable = self._pedir_entero("ID de responsable: ")
        if id_responsable is None:
            return
        self.asignar_responsable(id_solicitud, id_responsable)

    def _opcion_buscar(self):
        estado = input("Estado (vacio = todos): ").strip().upper()
        tipo = input("Tipo (vacio = todos): ").strip().upper()
        legajo = input("Legajo (vacio = todos): ").strip()
        prioridad = input("Prioridad (vacio = todas): ").strip().upper()
        self.buscar(estado, tipo, legajo, prioridad)

    def _opcion_actualizar_email(self):
        legajo = input("Legajo: ").strip()
        email = input("Nuevo email: ").strip()
        self.actualizar_email(legajo, email)

    @staticmethod
    def _mostrar_menu():
        print("")
        print("=== GESTION DE SOLICITUDES ACADEMICAS ===")
        print("1. Registrar solicitud")
        print("2. Cambiar estado")
        print("3. Asignar responsable")
        print("4. Buscar / filtrar solicitudes")
        print("5. Reporte")
        print("6. Listar responsables")
        print("7. Actualizar email de estudiante")
        print("0. Salir")

    def menu(self):
        acciones = {
            "1": self._opcion_registrar,
            "2": self._opcion_cambiar_estado,
            "3": self._opcion_asignar,
            "4": self._opcion_buscar,
            "5": self.reporte,
            "6": self.listar_responsables,
            "7": self._opcion_actualizar_email,
        }
        while True:
            self._mostrar_menu()
            opcion = input("Opcion: ").strip()
            if opcion == "0":
                print("Hasta luego")
                break
            accion = acciones.get(opcion)
            if accion is None:
                print("Opcion invalida")
            else:
                accion()
