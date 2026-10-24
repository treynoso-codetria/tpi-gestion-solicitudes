"""Utilidades compartidas por los tests de caja negra (ejecutan la app real por consola)."""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GOLDEN = Path(__file__).resolve().parent / "golden"
ARCHIVO_DATOS = "solicitudes.json"
PATRON_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


def ejecutar_cli(entrada, directorio):
    """Ejecuta main.py en `directorio` enviando `entrada` por stdin.

    Devuelve (salida_estandar, salida_error, codigo_de_retorno).
    """
    entorno = dict(os.environ, PYTHONPATH=str(RAIZ), PYTHONIOENCODING="utf-8")
    proceso = subprocess.run(
        [sys.executable, str(RAIZ / "main.py")],
        input=entrada,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=directorio,
        env=entorno,
        timeout=30,
        check=False,
    )
    return proceso.stdout, proceso.stderr, proceso.returncode


def leer_datos_normalizados(directorio):
    """Lee el archivo de datos reemplazando las fechas por un marcador fijo."""
    texto = (Path(directorio) / ARCHIVO_DATOS).read_text(encoding="utf-8")
    return json.loads(PATRON_FECHA.sub("<FECHA>", texto))


def directorio_temporal():
    return tempfile.TemporaryDirectory(prefix="tpi_")
