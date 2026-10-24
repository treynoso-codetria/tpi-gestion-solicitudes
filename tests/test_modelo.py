import unittest

from solicitudes.errores import TransicionInvalida
from solicitudes.modelo import Estado, Prioridad, Responsable, Solicitud, TipoSolicitud

RESPONSABLE = Responsable(2, "Martin Sosa", "Bedelia")


def solicitud_pendiente(responsable_id=None):
    return Solicitud(1, "10234", TipoSolicitud.CERTIFICADO, "Certificado de alumno regular",
                     Prioridad.BAJA, Estado.PENDIENTE, responsable_id, "2026-10-24", 15)


class TestReglasDeEnumeraciones(unittest.TestCase):

    def test_prioridad_por_defecto_de_cada_tipo(self):
        esperadas = {
            TipoSolicitud.RECLAMO_NOTA: Prioridad.ALTA,
            TipoSolicitud.BAJA: Prioridad.ALTA,
            TipoSolicitud.EQUIVALENCIA: Prioridad.MEDIA,
            TipoSolicitud.CAMBIO_COMISION: Prioridad.MEDIA,
            TipoSolicitud.CERTIFICADO: Prioridad.BAJA,
        }
        for tipo, prioridad in esperadas.items():
            with self.subTest(tipo=tipo):
                self.assertIs(prioridad, tipo.prioridad_por_defecto)

    def test_dias_de_plazo_por_prioridad(self):
        self.assertEqual((3, 7, 15), (Prioridad.ALTA.dias_de_plazo, Prioridad.MEDIA.dias_de_plazo,
                                      Prioridad.BAJA.dias_de_plazo))

    def test_estados_finales(self):
        self.assertEqual({Estado.RESUELTA, Estado.RECHAZADA}, {e for e in Estado if e.es_final})

    def test_desde_texto_devuelve_none_si_no_existe(self):
        self.assertIsNone(Estado.desde_texto("CERRADA"))
        self.assertIsNone(TipoSolicitud.desde_texto("tramite"))
        self.assertIs(Prioridad.MEDIA, Prioridad.desde_texto("MEDIA"))


class TestSolicitud(unittest.TestCase):

    def test_asignar_registra_responsable_y_evento(self):
        # Arrange
        solicitud = solicitud_pendiente()
        # Act
        solicitud.asignar(RESPONSABLE, "2026-10-24")
        # Assert
        self.assertEqual(2, solicitud.responsable_id)
        self.assertEqual("Asignada a Martin Sosa (Bedelia)", solicitud.historial[-1].descripcion)

    def test_no_pasa_a_revision_sin_responsable(self):
        solicitud = solicitud_pendiente()
        with self.assertRaisesRegex(TransicionInvalida, "debe asignar un responsable"):
            solicitud.cambiar_estado(Estado.EN_REVISION, "2026-10-24")
        self.assertIs(Estado.PENDIENTE, solicitud.estado)

    def test_ciclo_completo_pendiente_revision_resuelta(self):
        solicitud = solicitud_pendiente(responsable_id=2)
        solicitud.cambiar_estado(Estado.EN_REVISION, "2026-10-24")
        solicitud.cambiar_estado(Estado.RESUELTA, "2026-10-25")
        self.assertIs(Estado.RESUELTA, solicitud.estado)
        self.assertEqual(["Cambio de PENDIENTE a EN_REVISION", "Cambio de EN_REVISION a RESUELTA"],
                         [e.descripcion for e in solicitud.historial])

    def test_pendiente_puede_rechazarse_sin_responsable(self):
        solicitud = solicitud_pendiente()
        solicitud.cambiar_estado(Estado.RECHAZADA, "2026-10-24")
        self.assertTrue(solicitud.esta_finalizada)

    def test_transiciones_no_permitidas(self):
        casos = [(Estado.PENDIENTE, Estado.RESUELTA), (Estado.PENDIENTE, Estado.PENDIENTE),
                 (Estado.EN_REVISION, Estado.PENDIENTE), (Estado.EN_REVISION, Estado.EN_REVISION)]
        for origen, destino in casos:
            with self.subTest(origen=origen, destino=destino):
                solicitud = solicitud_pendiente(responsable_id=2)
                solicitud.estado = origen
                with self.assertRaisesRegex(TransicionInvalida, "transicion no permitida"):
                    solicitud.cambiar_estado(destino, "2026-10-24")

    def test_solicitud_finalizada_no_admite_cambios(self):
        solicitud = solicitud_pendiente(responsable_id=2)
        solicitud.estado = Estado.RESUELTA
        with self.assertRaisesRegex(TransicionInvalida, "ya esta finalizada"):
            solicitud.cambiar_estado(Estado.RECHAZADA, "2026-10-24")
        with self.assertRaisesRegex(TransicionInvalida, "ya esta finalizada"):
            solicitud.asignar(RESPONSABLE, "2026-10-24")


if __name__ == "__main__":
    unittest.main()
