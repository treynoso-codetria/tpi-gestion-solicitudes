"""Pruebas de contrato del Almacenamiento (Principio de Sustitucion de Liskov).

La misma bateria se ejecuta sobre las dos implementaciones. Si alguna no
cumple el contrato, no puede reemplazar a la otra sin romper el sistema.
"""

import tempfile
import unittest
from pathlib import Path

from solicitudes.almacenamiento import AlmacenamientoEnMemoria, AlmacenamientoJSON, ArchivoDeDatosDanado
from solicitudes.repositorio import RepositorioSolicitudes

DOCUMENTO = {"solicitudes": [], "estudiantes": [], "responsables": [{"id": 1, "nombre": "A", "area": "B"}],
             "ultimo_id": 0}


class ContratoAlmacenamiento:
    """Mixin: cada subclase define crear_almacenamiento()."""

    def crear_almacenamiento(self):
        raise NotImplementedError

    def test_sin_datos_devuelve_none(self):
        self.assertIsNone(self.crear_almacenamiento().cargar())

    def test_devuelve_lo_que_se_guardo(self):
        almacenamiento = self.crear_almacenamiento()
        almacenamiento.guardar(DOCUMENTO)
        self.assertEqual(DOCUMENTO, almacenamiento.cargar())

    def test_modificar_lo_cargado_no_altera_lo_guardado(self):
        almacenamiento = self.crear_almacenamiento()
        almacenamiento.guardar(DOCUMENTO)
        almacenamiento.cargar()["ultimo_id"] = 99
        self.assertEqual(0, almacenamiento.cargar()["ultimo_id"])

    def test_el_repositorio_funciona_con_esta_implementacion(self):
        almacenamiento = self.crear_almacenamiento()
        RepositorioSolicitudes(almacenamiento)
        self.assertEqual(4, len(almacenamiento.cargar()["responsables"]))


class TestAlmacenamientoEnMemoria(ContratoAlmacenamiento, unittest.TestCase):

    def crear_almacenamiento(self):
        return AlmacenamientoEnMemoria()


class TestAlmacenamientoJSON(ContratoAlmacenamiento, unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ruta = Path(self._tmp.name) / "datos.json"

    def tearDown(self):
        self._tmp.cleanup()

    def crear_almacenamiento(self):
        return AlmacenamientoJSON(self.ruta)

    def test_archivo_danado_lanza_error_y_no_se_modifica(self):
        self.ruta.write_text("{ incompleto", encoding="utf-8")
        with self.assertRaisesRegex(ArchivoDeDatosDanado, "no se pudo leer datos.json"):
            self.crear_almacenamiento().cargar()
        self.assertEqual("{ incompleto", self.ruta.read_text(encoding="utf-8"))

    def test_conserva_tildes_legibles(self):
        documento = dict(DOCUMENTO, responsables=[{"id": 1, "nombre": "Martín", "area": "Bedelía"}])
        self.crear_almacenamiento().guardar(documento)
        self.assertIn("Martín", self.ruta.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
