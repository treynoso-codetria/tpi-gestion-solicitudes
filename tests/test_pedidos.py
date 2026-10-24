import unittest

from solicitudes.errores import DatosInvalidos
from solicitudes.modelo import Estado, Prioridad, Solicitud, TipoSolicitud
from solicitudes.pedidos import FiltroSolicitudes
from tests.fabricas import pedido


class TestValidacionDelPedido(unittest.TestCase):

    def test_pedido_valido_no_lanza_error(self):
        pedido().validar()

    def test_valores_limite(self):
        casos_invalidos = {
            "legajo de 4 digitos": pedido(legajo="1234"),
            "legajo con letras": pedido(legajo="12a45"),
            "nombre vacio": pedido(nombre="   "),
            "email sin arroba": pedido(email="ana.mail.com"),
            "email sin punto en dominio": pedido(email="ana@mail"),
            "tipo inexistente": pedido(tipo="TRAMITE"),
            "descripcion de 9 caracteres": pedido(descripcion="123456789"),
            "prioridad inexistente": pedido(prioridad="URGENTE"),
        }
        for caso, pedido_invalido in casos_invalidos.items():
            with self.subTest(caso=caso), self.assertRaises(DatosInvalidos):
                pedido_invalido.validar()

    def test_limites_validos(self):
        pedido(legajo="12345", descripcion="1234567890").validar()

    def test_el_orden_de_validacion_se_mantiene(self):
        # Con varios datos mal, se informa el primero, igual que en la version base.
        invalido = pedido(legajo="1", email="x", tipo="X")
        with self.assertRaisesRegex(DatosInvalidos, "legajo invalido"):
            invalido.validar()

    def test_prioridad_efectiva(self):
        self.assertIs(Prioridad.ALTA, pedido(tipo="RECLAMO_NOTA").prioridad_efectiva())
        self.assertIs(Prioridad.BAJA, pedido(tipo="RECLAMO_NOTA", prioridad="BAJA").prioridad_efectiva())


class TestFiltroSolicitudes(unittest.TestCase):

    def setUp(self):
        self.solicitud = Solicitud(1, "10234", TipoSolicitud.EQUIVALENCIA, "Equivalencia de Matematica",
                                   Prioridad.MEDIA, Estado.PENDIENTE, None, "2026-10-24", 7)

    def test_filtro_vacio_acepta_todo(self):
        self.assertTrue(FiltroSolicitudes().acepta(self.solicitud))

    def test_todos_los_criterios_deben_coincidir(self):
        self.assertTrue(FiltroSolicitudes(estado="PENDIENTE", legajo="10234").acepta(self.solicitud))
        self.assertFalse(FiltroSolicitudes(estado="PENDIENTE", legajo="99999").acepta(self.solicitud))

    def test_tipo_invalido_en_el_filtro(self):
        with self.assertRaisesRegex(DatosInvalidos, "tipo de solicitud invalido"):
            FiltroSolicitudes(tipo="XYZ").validar()


if __name__ == "__main__":
    unittest.main()
