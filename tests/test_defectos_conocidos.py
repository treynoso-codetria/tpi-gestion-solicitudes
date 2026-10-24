"""Defectos detectados durante el diagnostico (etapa 3).

Cada test describe el comportamiento CORRECTO esperado. En la version base
fallan, por eso estan marcados con @unittest.expectedFailure. Cuando el
refactoring corrige el defecto, se quita la marca y el test pasa a ser una
prueba de regresion normal.
"""

import unittest
from pathlib import Path

from tests.utilidades import ARCHIVO_DATOS, directorio_temporal, ejecutar_cli

REGISTRO_CON_PRIORIDAD_INVALIDA = "\n".join([
    "1", "20001", "Eva", "Mansilla", "eva@mail.com", "Tecnicatura en Programacion",
    "CERTIFICADO", "Certificado analitico parcial", "URGENTE",
])


class TestDefectosConocidos(unittest.TestCase):

    def setUp(self):
        self._tmp = directorio_temporal()
        self.directorio = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_d1_reporte_sin_solicitudes_no_debe_fallar(self):
        salida, errores, codigo = ejecutar_cli("5\n0\n", self.directorio)
        self.assertEqual(0, codigo, errores)
        self.assertIn("Total de solicitudes: 0", salida)
        self.assertIn("PENDIENTE      0  (0.0%)", salida)

    def test_d2_registro_rechazado_no_debe_crear_al_estudiante(self):
        entrada = REGISTRO_CON_PRIORIDAD_INVALIDA + "\n7\n20001\neva.nueva@mail.com\n0\n"
        salida, _, _ = ejecutar_cli(entrada, self.directorio)
        self.assertIn("Error: prioridad invalida", salida)
        self.assertIn("Error: no existe el estudiante 20001", salida)

    def test_d3_archivo_danado_no_debe_sobrescribirse(self):
        archivo = Path(self.directorio) / ARCHIVO_DATOS
        contenido_original = '{"solicitudes": [ {"id": 1, '
        archivo.write_text(contenido_original, encoding="utf-8")
        salida, _, codigo = ejecutar_cli("0\n", self.directorio)
        self.assertEqual(contenido_original, archivo.read_text(encoding="utf-8"))
        self.assertNotEqual(0, codigo)
        self.assertIn("Error: no se pudo leer solicitudes.json", salida)


if __name__ == "__main__":
    unittest.main()
