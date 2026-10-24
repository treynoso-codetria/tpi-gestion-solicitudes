"""Persistencia del documento de datos (Move Method + Inversion de Dependencias).

La logica de negocio depende de la abstraccion `Almacenamiento`, no del disco.
Hay dos implementaciones intercambiables: un archivo JSON para produccion y
una en memoria para las pruebas. Ambas cumplen el mismo contrato (LSP), que se
verifica en tests/test_almacenamiento.py.
"""

import copy
import json
from pathlib import Path
from typing import Protocol


class ArchivoDeDatosDanado(Exception):
    """El archivo de datos existe pero no se puede interpretar."""


class Almacenamiento(Protocol):
    def cargar(self) -> dict | None:
        """Devuelve el documento guardado o None si todavia no hay datos."""

    def guardar(self, documento: dict) -> None:
        """Reemplaza el documento guardado."""


class AlmacenamientoJSON:
    def __init__(self, ruta: str | Path):
        self.ruta = Path(ruta)

    def cargar(self) -> dict | None:
        if not self.ruta.exists():
            return None
        try:
            with self.ruta.open("r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            # Antes: `except: pass` y el sistema sobrescribia el archivo (defecto D3).
            raise ArchivoDeDatosDanado(
                f"no se pudo leer {self.ruta.name} (archivo danado). "
                "El archivo no fue modificado; reviselo o restaure una copia."
            ) from error

    def guardar(self, documento: dict) -> None:
        with self.ruta.open("w", encoding="utf-8") as archivo:
            json.dump(documento, archivo, indent=2, ensure_ascii=False)


class AlmacenamientoEnMemoria:
    def __init__(self, documento: dict | None = None):
        self._documento = copy.deepcopy(documento)

    def cargar(self) -> dict | None:
        return copy.deepcopy(self._documento)

    def guardar(self, documento: dict) -> None:
        self._documento = copy.deepcopy(documento)
