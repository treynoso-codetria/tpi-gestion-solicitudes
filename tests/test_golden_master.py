"""Test de caracterizacion (golden master).

Ejecuta un escenario completo por consola (tests/golden/escenario.txt) y compara
la salida y el archivo de datos resultante contra lo que producia la version
base (tag `estado-inicial`). Si el refactoring altera el comportamiento externo,
este test falla.

Para regenerar los archivos esperados (solo si un cambio de comportamiento es
intencional y esta documentado):  python -m tests.test_golden_master --regenerar
"""

import json
import sys
import unittest

from tests.utilidades import GOLDEN, directorio_temporal, ejecutar_cli, leer_datos_normalizados

ESCENARIO = GOLDEN / "escenario.txt"
SALIDA_ESPERADA = GOLDEN / "salida_esperada.txt"
DATOS_ESPERADOS = GOLDEN / "datos_esperados.json"


class TestGoldenMaster(unittest.TestCase):

    def setUp(self):
        self._tmp = directorio_temporal()
        self.directorio = self._tmp.name
        entrada = ESCENARIO.read_text(encoding="utf-8")
        self.salida, self.errores, self.codigo = ejecutar_cli(entrada, self.directorio)

    def tearDown(self):
        self._tmp.cleanup()

    def test_el_programa_termina_sin_errores(self):
        self.assertEqual(0, self.codigo, self.errores)
        self.assertEqual("", self.errores)

    def test_la_salida_por_consola_no_cambia(self):
        esperada = SALIDA_ESPERADA.read_text(encoding="utf-8")
        self.assertEqual(esperada, self.salida)

    def test_el_archivo_de_datos_no_cambia(self):
        esperados = json.loads(DATOS_ESPERADOS.read_text(encoding="utf-8"))
        self.assertEqual(esperados, leer_datos_normalizados(self.directorio))


def regenerar():
    with directorio_temporal() as directorio:
        salida, errores, codigo = ejecutar_cli(ESCENARIO.read_text(encoding="utf-8"), directorio)
        if codigo != 0:
            raise SystemExit(errores)
        SALIDA_ESPERADA.write_text(salida, encoding="utf-8")
        datos = leer_datos_normalizados(directorio)
        DATOS_ESPERADOS.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Archivos golden regenerados")


if __name__ == "__main__":
    if "--regenerar" in sys.argv:
        regenerar()
    else:
        unittest.main()
