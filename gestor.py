from datetime import datetime

from solicitudes.almacenamiento import Almacenamiento
from solicitudes.modelo import Estado, TipoSolicitud
from solicitudes.pedidos import DatosEstudiante, PedidoSolicitud
from solicitudes.validaciones import es_email_valido


class GestorSolicitudes:
    # clase principal del sistema

    def __init__(self, almacenamiento: Almacenamiento):
        self.almacenamiento = almacenamiento
        self.datos = almacenamiento.cargar() or {
            "solicitudes": [], "estudiantes": [], "responsables": [], "ultimo_id": 0}
        if len(self.datos["responsables"]) == 0:
            # responsables por defecto
            self.datos["responsables"].append({"id": 1, "nombre": "Laura Gomez", "area": "Alumnado"})
            self.datos["responsables"].append({"id": 2, "nombre": "Martin Sosa", "area": "Bedelia"})
            self.datos["responsables"].append({"id": 3, "nombre": "Carla Ruiz", "area": "Coordinacion"})
            self.datos["responsables"].append({"id": 4, "nombre": "Diego Paz", "area": "Tesoreria"})
            self.guardar()

    def guardar(self):
        self.almacenamiento.guardar(self.datos)

    # ---------------------------------------------------------------
    # Metodos extraidos (antes el codigo estaba duplicado)
    # ---------------------------------------------------------------
    @staticmethod
    def _fecha_hoy():
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _esta_finalizada(solicitud):
        return Estado(solicitud["estado"]).es_final

    def _buscar_solicitud(self, id_solicitud):
        for solicitud in self.datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:
                return solicitud
        return None

    def _buscar_responsable(self, id_responsable):
        for responsable in self.datos["responsables"]:
            if responsable["id"] == id_responsable:
                return responsable
        return None

    def _buscar_estudiante(self, legajo):
        for estudiante in self.datos["estudiantes"]:
            if estudiante["legajo"] == legajo:
                return estudiante
        return None

    def _registrar_evento(self, solicitud, evento):
        solicitud["historial"].append({"fecha": self._fecha_hoy(), "evento": evento})

    def _registrar_o_actualizar_estudiante(self, datos: DatosEstudiante):
        estudiante = self._buscar_estudiante(datos.legajo)
        if estudiante is not None:
            estudiante["email"] = datos.email
            return
        self.datos["estudiantes"].append({
            "legajo": datos.legajo,
            "nombre": datos.nombre,
            "apellido": datos.apellido,
            "email": datos.email,
            "carrera": datos.carrera
        })

    @staticmethod
    def _transicion_permitida(solicitud, nuevo_estado):
        """Devuelve el mensaje de error o None si la transicion es valida."""
        actual = Estado(solicitud["estado"])
        if actual.es_final:
            return "Error: la solicitud " + str(solicitud["id"]) + " ya esta finalizada"
        if not actual.puede_pasar_a(nuevo_estado):
            return "Error: transicion no permitida de " + actual + " a " + nuevo_estado
        if nuevo_estado is Estado.EN_REVISION and solicitud["responsable"] is None:
            return "Error: debe asignar un responsable antes de pasar a revision"
        return None

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
        dias = prioridad.dias_de_plazo

        self.datos["ultimo_id"] = self.datos["ultimo_id"] + 1
        solicitud = {
            "id": self.datos["ultimo_id"],
            "legajo": pedido.estudiante.legajo,
            "tipo": pedido.tipo,
            "descripcion": pedido.descripcion,
            "prioridad": str(prioridad),
            "estado": str(Estado.PENDIENTE),
            "responsable": None,
            "fecha": self._fecha_hoy(),
            "dias_sla": dias,
            "historial": []
        }
        self._registrar_evento(solicitud, "Creada en estado PENDIENTE")
        self.datos["solicitudes"].append(solicitud)
        self.guardar()
        print("Solicitud registrada con ID " + str(solicitud["id"]) + " (prioridad " + prioridad + ", plazo " + str(dias) + " dias)")
        return solicitud["id"]

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        solicitud = self._buscar_solicitud(id_solicitud)
        if solicitud is None:
            print("Error: no existe la solicitud " + str(id_solicitud))
            return False
        nuevo_estado = Estado.desde_texto(nuevo_estado)
        if nuevo_estado is None:
            print("Error: estado invalido")
            return False
        error = self._transicion_permitida(solicitud, nuevo_estado)
        if error is not None:
            print(error)
            return False

        self._registrar_evento(solicitud, "Cambio de " + solicitud["estado"] + " a " + nuevo_estado)
        solicitud["estado"] = str(nuevo_estado)
        self.guardar()
        print("Solicitud " + str(id_solicitud) + " ahora esta en estado " + nuevo_estado)
        return True

    def asignar_responsable(self, id_solicitud, id_responsable):
        solicitud = self._buscar_solicitud(id_solicitud)
        if solicitud is None:
            print("Error: no existe la solicitud " + str(id_solicitud))
            return False
        if self._esta_finalizada(solicitud):
            print("Error: la solicitud " + str(id_solicitud) + " ya esta finalizada")
            return False
        responsable = self._buscar_responsable(id_responsable)
        if responsable is None:
            print("Error: no existe el responsable " + str(id_responsable))
            return False
        descripcion_responsable = responsable["nombre"] + " (" + responsable["area"] + ")"
        solicitud["responsable"] = responsable["id"]
        self._registrar_evento(solicitud, "Asignada a " + descripcion_responsable)
        self.guardar()
        print("Solicitud " + str(id_solicitud) + " asignada a " + descripcion_responsable)
        return True

    def actualizar_email(self, legajo, email):
        if not es_email_valido(email):
            print("Error: email invalido")
            return False
        estudiante = self._buscar_estudiante(legajo)
        if estudiante is None:
            print("Error: no existe el estudiante " + legajo)
            return False
        estudiante["email"] = email
        self.guardar()
        print("Email actualizado para el legajo " + legajo)
        return True

    @staticmethod
    def _cumple_filtros(solicitud, estado, tipo, legajo, prioridad):
        filtros = {"estado": estado, "tipo": tipo, "legajo": legajo, "prioridad": prioridad}
        return all(valor == "" or solicitud[campo] == valor for campo, valor in filtros.items())

    def buscar(self, estado, tipo, legajo, prioridad):
        if tipo != "" and TipoSolicitud.desde_texto(tipo) is None:
            print("Error: tipo de solicitud invalido")
            return []
        encontradas = [s for s in self.datos["solicitudes"]
                       if self._cumple_filtros(s, estado, tipo, legajo, prioridad)]
        if len(encontradas) == 0:
            print("No se encontraron solicitudes")
            return encontradas
        print("ID  LEGAJO  TIPO            PRIOR. ESTADO       RESPONSABLE")
        for solicitud in encontradas:
            responsable = self._buscar_responsable(solicitud["responsable"])
            nombre_responsable = responsable["nombre"] if responsable is not None else "-"
            print(str(solicitud["id"]).ljust(4) + solicitud["legajo"].ljust(8) + solicitud["tipo"].ljust(16)
                  + solicitud["prioridad"].ljust(7) + solicitud["estado"].ljust(13) + nombre_responsable)
        return encontradas

    def _contar(self, condicion):
        return sum(1 for solicitud in self.datos["solicitudes"] if condicion(solicitud))

    def reporte(self):
        total = len(self.datos["solicitudes"])
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total de solicitudes: " + str(total))
        print("--- Por estado ---")
        for estado in Estado:
            cantidad = self._contar(lambda s, e=estado: s["estado"] == e)
            porcentaje = cantidad * 100 / total
            print(estado.ljust(12) + str(cantidad).rjust(4) + "  (" + str(round(porcentaje, 1)) + "%)")
        print("--- Por tipo ---")
        for tipo in TipoSolicitud:
            cantidad = self._contar(lambda s, t=tipo: s["tipo"] == t)
            print(tipo.ljust(16) + str(cantidad).rjust(4))
        print("--- Carga por responsable (abiertas) ---")
        for responsable in self.datos["responsables"]:
            cantidad = self._contar(
                lambda s, r=responsable: s["responsable"] == r["id"] and not self._esta_finalizada(s))
            print((responsable["nombre"] + " (" + responsable["area"] + ")").ljust(28) + str(cantidad).rjust(4))
        sin_responsable = self._contar(lambda s: s["responsable"] is None and not self._esta_finalizada(s))
        print("Sin responsable".ljust(28) + str(sin_responsable).rjust(4))
        print("==================================")

    def listar_responsables(self):
        for responsable in self.datos["responsables"]:
            print(str(responsable["id"]) + " - " + responsable["nombre"] + " (" + responsable["area"] + ")")

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
