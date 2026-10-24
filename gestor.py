import json
import os
from datetime import datetime

ARCHIVO = "solicitudes.json"


class GestorSolicitudes:
    # clase principal del sistema

    def __init__(self):
        self.d = {"solicitudes": [], "estudiantes": [], "responsables": [], "ultimo_id": 0}
        self.cargar()
        if len(self.d["responsables"]) == 0:
            # responsables por defecto
            self.d["responsables"].append({"id": 1, "nombre": "Laura Gomez", "area": "Alumnado"})
            self.d["responsables"].append({"id": 2, "nombre": "Martin Sosa", "area": "Bedelia"})
            self.d["responsables"].append({"id": 3, "nombre": "Carla Ruiz", "area": "Coordinacion"})
            self.d["responsables"].append({"id": 4, "nombre": "Diego Paz", "area": "Tesoreria"})
            self.guardar()

    def cargar(self):
        try:
            f = open(ARCHIVO, "r", encoding="utf-8")
            self.d = json.load(f)
            f.close()
        except:
            pass

    def guardar(self):
        f = open(ARCHIVO, "w", encoding="utf-8")
        json.dump(self.d, f, indent=2, ensure_ascii=False)
        f.close()

    def registrar_solicitud(self, legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad):
        # validaciones
        if legajo == "" or not legajo.isdigit() or len(legajo) < 5:
            print("Error: legajo invalido")
            return -1
        if nombre.strip() == "" or apellido.strip() == "":
            print("Error: nombre y apellido son obligatorios")
            return -1
        if "@" not in email or "." not in email.split("@")[-1]:
            print("Error: email invalido")
            return -1
        if tipo != "CERTIFICADO" and tipo != "EQUIVALENCIA" and tipo != "CAMBIO_COMISION" and tipo != "RECLAMO_NOTA" and tipo != "BAJA":
            print("Error: tipo de solicitud invalido")
            return -1
        if len(descripcion.strip()) < 10:
            print("Error: la descripcion debe tener al menos 10 caracteres")
            return -1

        # buscar o crear estudiante
        existe = False
        for e in self.d["estudiantes"]:
            if e["legajo"] == legajo:
                existe = True
                e["email"] = email
        if existe == False:
            self.d["estudiantes"].append({
                "legajo": legajo,
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "carrera": carrera
            })

        # calcular prioridad
        if prioridad == "":
            if tipo == "RECLAMO_NOTA":
                prioridad = "ALTA"
            elif tipo == "BAJA":
                prioridad = "ALTA"
            elif tipo == "EQUIVALENCIA":
                prioridad = "MEDIA"
            elif tipo == "CAMBIO_COMISION":
                prioridad = "MEDIA"
            else:
                prioridad = "BAJA"
        else:
            if prioridad != "BAJA" and prioridad != "MEDIA" and prioridad != "ALTA":
                print("Error: prioridad invalida")
                return -1

        # dias de plazo segun prioridad
        if prioridad == "ALTA":
            dias = 3
        elif prioridad == "MEDIA":
            dias = 7
        else:
            dias = 15

        self.d["ultimo_id"] = self.d["ultimo_id"] + 1
        x = {
            "id": self.d["ultimo_id"],
            "legajo": legajo,
            "tipo": tipo,
            "descripcion": descripcion,
            "prioridad": prioridad,
            "estado": "PENDIENTE",
            "responsable": None,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "dias_sla": dias,
            "historial": [{"fecha": datetime.now().strftime("%Y-%m-%d"), "evento": "Creada en estado PENDIENTE"}]
        }
        self.d["solicitudes"].append(x)
        self.guardar()
        print("Solicitud registrada con ID " + str(x["id"]) + " (prioridad " + prioridad + ", plazo " + str(dias) + " dias)")
        return x["id"]

    def cambiar_estado(self, id, nuevo):
        s = None
        for x in self.d["solicitudes"]:
            if x["id"] == id:
                s = x
        if s == None:
            print("Error: no existe la solicitud " + str(id))
            return False
        if nuevo != "PENDIENTE" and nuevo != "EN_REVISION" and nuevo != "RESUELTA" and nuevo != "RECHAZADA":
            print("Error: estado invalido")
            return False

        if s["estado"] == "PENDIENTE":
            if nuevo == "EN_REVISION":
                if s["responsable"] == None:
                    print("Error: debe asignar un responsable antes de pasar a revision")
                    return False
            elif nuevo == "RECHAZADA":
                pass
            else:
                print("Error: transicion no permitida de " + s["estado"] + " a " + nuevo)
                return False
        elif s["estado"] == "EN_REVISION":
            if nuevo == "RESUELTA" or nuevo == "RECHAZADA":
                pass
            else:
                print("Error: transicion no permitida de " + s["estado"] + " a " + nuevo)
                return False
        else:
            print("Error: la solicitud " + str(id) + " ya esta finalizada")
            return False

        s["historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "evento": "Cambio de " + s["estado"] + " a " + nuevo})
        s["estado"] = nuevo
        self.guardar()
        print("Solicitud " + str(id) + " ahora esta en estado " + nuevo)
        return True

    def asignar_responsable(self, id, id_resp):
        s = None
        for x in self.d["solicitudes"]:
            if x["id"] == id:
                s = x
        if s == None:
            print("Error: no existe la solicitud " + str(id))
            return False
        if s["estado"] == "RESUELTA" or s["estado"] == "RECHAZADA":
            print("Error: la solicitud " + str(id) + " ya esta finalizada")
            return False
        r = None
        for x in self.d["responsables"]:
            if x["id"] == id_resp:
                r = x
        if r == None:
            print("Error: no existe el responsable " + str(id_resp))
            return False
        s["responsable"] = r["id"]
        s["historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d"), "evento": "Asignada a " + r["nombre"] + " (" + r["area"] + ")"})
        self.guardar()
        print("Solicitud " + str(id) + " asignada a " + r["nombre"] + " (" + r["area"] + ")")
        return True

    def actualizar_email(self, legajo, email):
        if "@" not in email or "." not in email.split("@")[-1]:
            print("Error: email invalido")
            return False
        for e in self.d["estudiantes"]:
            if e["legajo"] == legajo:
                e["email"] = email
                self.guardar()
                print("Email actualizado para el legajo " + legajo)
                return True
        print("Error: no existe el estudiante " + legajo)
        return False

    def buscar(self, estado, tipo, legajo, prioridad):
        if tipo != "" and tipo != "CERTIFICADO" and tipo != "EQUIVALENCIA" and tipo != "CAMBIO_COMISION" and tipo != "RECLAMO_NOTA" and tipo != "BAJA":
            print("Error: tipo de solicitud invalido")
            return []
        lst = []
        for x in self.d["solicitudes"]:
            flag = True
            if estado != "" and x["estado"] != estado:
                flag = False
            if tipo != "" and x["tipo"] != tipo:
                flag = False
            if legajo != "" and x["legajo"] != legajo:
                flag = False
            if prioridad != "" and x["prioridad"] != prioridad:
                flag = False
            if flag:
                lst.append(x)
        if len(lst) == 0:
            print("No se encontraron solicitudes")
            return lst
        print("ID  LEGAJO  TIPO            PRIOR. ESTADO       RESPONSABLE")
        for x in lst:
            nom = "-"
            for r in self.d["responsables"]:
                if r["id"] == x["responsable"]:
                    nom = r["nombre"]
            print(str(x["id"]).ljust(4) + x["legajo"].ljust(8) + x["tipo"].ljust(16) + x["prioridad"].ljust(7) + x["estado"].ljust(13) + nom)
        return lst

    def reporte(self):
        total = len(self.d["solicitudes"])
        print("===== REPORTE DE SOLICITUDES =====")
        print("Total de solicitudes: " + str(total))
        print("--- Por estado ---")
        for est in ["PENDIENTE", "EN_REVISION", "RESUELTA", "RECHAZADA"]:
            c = 0
            for x in self.d["solicitudes"]:
                if x["estado"] == est:
                    c = c + 1
            p = c * 100 / total
            print(est.ljust(12) + str(c).rjust(4) + "  (" + str(round(p, 1)) + "%)")
        print("--- Por tipo ---")
        for t in ["CERTIFICADO", "EQUIVALENCIA", "CAMBIO_COMISION", "RECLAMO_NOTA", "BAJA"]:
            c = 0
            for x in self.d["solicitudes"]:
                if x["tipo"] == t:
                    c = c + 1
            print(t.ljust(16) + str(c).rjust(4))
        print("--- Carga por responsable (abiertas) ---")
        for r in self.d["responsables"]:
            c = 0
            for x in self.d["solicitudes"]:
                if x["responsable"] == r["id"] and x["estado"] != "RESUELTA" and x["estado"] != "RECHAZADA":
                    c = c + 1
            print((r["nombre"] + " (" + r["area"] + ")").ljust(28) + str(c).rjust(4))
        sin = 0
        for x in self.d["solicitudes"]:
            if x["responsable"] == None and x["estado"] != "RESUELTA" and x["estado"] != "RECHAZADA":
                sin = sin + 1
        print("Sin responsable".ljust(28) + str(sin).rjust(4))
        print("==================================")

    def listar_responsables(self):
        for r in self.d["responsables"]:
            print(str(r["id"]) + " - " + r["nombre"] + " (" + r["area"] + ")")

    def menu(self):
        while True:
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
            op = input("Opcion: ").strip()
            if op == "1":
                legajo = input("Legajo: ").strip()
                nombre = input("Nombre: ").strip()
                apellido = input("Apellido: ").strip()
                email = input("Email: ").strip()
                carrera = input("Carrera: ").strip()
                tipo = input("Tipo (CERTIFICADO/EQUIVALENCIA/CAMBIO_COMISION/RECLAMO_NOTA/BAJA): ").strip().upper()
                descripcion = input("Descripcion: ").strip()
                prioridad = input("Prioridad (BAJA/MEDIA/ALTA, vacio = automatica): ").strip().upper()
                self.registrar_solicitud(legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad)
            elif op == "2":
                try:
                    id = int(input("ID de solicitud: "))
                except:
                    print("Error: ID invalido")
                    continue
                nuevo = input("Nuevo estado (EN_REVISION/RESUELTA/RECHAZADA): ").strip().upper()
                self.cambiar_estado(id, nuevo)
            elif op == "3":
                try:
                    id = int(input("ID de solicitud: "))
                except:
                    print("Error: ID invalido")
                    continue
                self.listar_responsables()
                try:
                    id_resp = int(input("ID de responsable: "))
                except:
                    print("Error: ID invalido")
                    continue
                self.asignar_responsable(id, id_resp)
            elif op == "4":
                estado = input("Estado (vacio = todos): ").strip().upper()
                tipo = input("Tipo (vacio = todos): ").strip().upper()
                legajo = input("Legajo (vacio = todos): ").strip()
                prioridad = input("Prioridad (vacio = todas): ").strip().upper()
                self.buscar(estado, tipo, legajo, prioridad)
            elif op == "5":
                self.reporte()
            elif op == "6":
                self.listar_responsables()
            elif op == "7":
                legajo = input("Legajo: ").strip()
                email = input("Nuevo email: ").strip()
                self.actualizar_email(legajo, email)
            elif op == "0":
                print("Hasta luego")
                break
            else:
                print("Opcion invalida")
