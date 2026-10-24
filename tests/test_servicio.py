"""Pruebas unitarias de los casos de uso, sin disco ni fecha real (patron AAA)."""

import unittest

from solicitudes.errores import DatosInvalidos, NoEncontrado, TransicionInvalida
from solicitudes.modelo import Estado, Prioridad
from solicitudes.pedidos import FiltroSolicitudes
from tests.fabricas import pedido, servicio_en_memoria


class TestRegistrarSolicitud(unittest.TestCase):

    def setUp(self):
        self.servicio, self.repositorio, self.almacenamiento = servicio_en_memoria()

    def test_registra_con_prioridad_y_plazo_segun_el_tipo(self):
        # Arrange
        datos = pedido(tipo="RECLAMO_NOTA", descripcion="Reclamo por nota del parcial 2")
        # Act
        solicitud = self.servicio.registrar(datos)
        # Assert
        self.assertEqual(1, solicitud.id)
        self.assertIs(Prioridad.ALTA, solicitud.prioridad)
        self.assertEqual(3, solicitud.dias_sla)
        self.assertIs(Estado.PENDIENTE, solicitud.estado)
        self.assertEqual("2026-10-24", solicitud.fecha)

    def test_persiste_la_solicitud(self):
        self.servicio.registrar(pedido())
        documento = self.almacenamiento.cargar()
        self.assertEqual(1, len(documento["solicitudes"]))
        self.assertEqual(1, documento["ultimo_id"])

    def test_los_ids_son_correlativos(self):
        ids = [self.servicio.registrar(pedido()).id for _ in range(3)]
        self.assertEqual([1, 2, 3], ids)

    def test_estudiante_existente_actualiza_su_email(self):
        self.servicio.registrar(pedido(email="ana@mail.com"))
        self.servicio.registrar(pedido(email="ana@alumnos.utn.edu.ar"))
        self.assertEqual("ana@alumnos.utn.edu.ar", self.repositorio.obtener_estudiante("10234").email)

    def test_pedido_invalido_no_modifica_ningun_dato(self):
        # Regresion del defecto D2.
        with self.assertRaises(DatosInvalidos):
            self.servicio.registrar(pedido(legajo="20001", prioridad="URGENTE"))
        self.assertIsNone(self.repositorio.obtener_estudiante("20001"))
        self.assertEqual([], self.repositorio.listar_solicitudes())


class TestCambiarEstadoYAsignar(unittest.TestCase):

    def setUp(self):
        self.servicio, self.repositorio, _ = servicio_en_memoria()
        self.id_solicitud = self.servicio.registrar(pedido()).id

    def test_asignar_y_pasar_a_revision(self):
        responsable = self.servicio.asignar_responsable(self.id_solicitud, 3)
        solicitud = self.servicio.cambiar_estado(self.id_solicitud, "EN_REVISION")
        self.assertEqual("Carla Ruiz", responsable.nombre)
        self.assertIs(Estado.EN_REVISION, solicitud.estado)

    def test_estado_inexistente(self):
        with self.assertRaisesRegex(DatosInvalidos, "estado invalido"):
            self.servicio.cambiar_estado(self.id_solicitud, "CERRADA")

    def test_solicitud_inexistente(self):
        with self.assertRaisesRegex(NoEncontrado, "no existe la solicitud 99"):
            self.servicio.cambiar_estado(99, "EN_REVISION")
        with self.assertRaisesRegex(NoEncontrado, "no existe la solicitud 99"):
            self.servicio.asignar_responsable(99, 1)

    def test_responsable_inexistente(self):
        with self.assertRaisesRegex(NoEncontrado, "no existe el responsable 9"):
            self.servicio.asignar_responsable(self.id_solicitud, 9)

    def test_finalizada_se_informa_antes_que_responsable_inexistente(self):
        self.servicio.cambiar_estado(self.id_solicitud, "RECHAZADA")
        with self.assertRaisesRegex(TransicionInvalida, "ya esta finalizada"):
            self.servicio.asignar_responsable(self.id_solicitud, 9)


class TestActualizarEmailYBuscar(unittest.TestCase):

    def setUp(self):
        self.servicio, _, _ = servicio_en_memoria()
        self.servicio.registrar(pedido(legajo="10234", tipo="CERTIFICADO"))
        self.servicio.registrar(pedido(legajo="10567", tipo="BAJA", descripcion="Baja de la materia Ingles II"))

    def test_actualizar_email(self):
        estudiante = self.servicio.actualizar_email("10567", "nuevo@mail.com")
        self.assertEqual("nuevo@mail.com", estudiante.email)

    def test_actualizar_email_invalido_o_inexistente(self):
        with self.assertRaisesRegex(DatosInvalidos, "email invalido"):
            self.servicio.actualizar_email("10567", "correo-invalido")
        with self.assertRaisesRegex(NoEncontrado, "no existe el estudiante 99999"):
            self.servicio.actualizar_email("99999", "a@b.com")

    def test_buscar_por_prioridad(self):
        encontradas = self.servicio.buscar(FiltroSolicitudes(prioridad="ALTA"))
        self.assertEqual(["10567"], [s.legajo for s in encontradas])

    def test_buscar_sin_resultados(self):
        self.assertEqual([], self.servicio.buscar(FiltroSolicitudes(legajo="00000")))


if __name__ == "__main__":
    unittest.main()
