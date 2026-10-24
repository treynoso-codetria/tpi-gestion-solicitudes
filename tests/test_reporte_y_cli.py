import unittest

from solicitudes.cli import ConsolaSolicitudes
from solicitudes.reporte import GeneradorReporte
from tests.fabricas import pedido, servicio_en_memoria


class TestGeneradorReporte(unittest.TestCase):

    def setUp(self):
        self.servicio, repositorio, _ = servicio_en_memoria()
        self.reporte = GeneradorReporte(repositorio)

    def test_sin_solicitudes_muestra_ceros(self):
        # Regresion del defecto D1.
        texto = self.reporte.generar()
        self.assertIn("Total de solicitudes: 0", texto)
        self.assertIn("RECHAZADA      0  (0.0%)", texto)

    def test_porcentajes_y_carga_por_responsable(self):
        for _ in range(3):
            self.servicio.registrar(pedido())
        self.servicio.asignar_responsable(1, 1)
        self.servicio.cambiar_estado(2, "RECHAZADA")
        texto = self.reporte.generar()
        self.assertIn("PENDIENTE      2  (66.7%)", texto)
        self.assertIn("RECHAZADA      1  (33.3%)", texto)
        self.assertIn("Laura Gomez (Alumnado)         1", texto)
        self.assertIn("Sin responsable                1", texto)


class TestConsola(unittest.TestCase):
    """La consola se prueba inyectando la entrada y capturando la salida."""

    def ejecutar(self, *entradas):
        servicio, repositorio, _ = servicio_en_memoria()
        respuestas = iter(entradas)
        salida = []
        consola = ConsolaSolicitudes(servicio, GeneradorReporte(repositorio),
                                     leer=lambda _mensaje: next(respuestas), escribir=salida.append)
        consola.ejecutar()
        return salida

    def test_opcion_invalida_y_salida(self):
        salida = self.ejecutar("9", "0")
        self.assertIn("Opcion invalida", salida)
        self.assertEqual("Hasta luego", salida[-1])

    def test_id_no_numerico(self):
        salida = self.ejecutar("2", "abc", "0")
        self.assertIn("Error: ID invalido", salida)

    def test_error_de_negocio_se_muestra_y_el_menu_continua(self):
        salida = self.ejecutar("2", "5", "EN_REVISION", "6", "0")
        self.assertIn("Error: no existe la solicitud 5", salida)
        self.assertIn("1 - Laura Gomez (Alumnado)", salida)

    def test_registro_completo(self):
        salida = self.ejecutar("1", "10234", "Ana", "Lopez", "ana@mail.com", "TUP", "reclamo_nota",
                               "Reclamo nota del parcial", "", "0")
        self.assertIn("Solicitud registrada con ID 1 (prioridad ALTA, plazo 3 dias)", salida)


if __name__ == "__main__":
    unittest.main()
