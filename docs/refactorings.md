# Refactorings aplicados

Cada refactoring es un commit independiente. Después de cada uno se ejecutó la suite completa. El golden master (`tests/test_golden_master.py`) tuvo que seguir en verde: misma salida por consola y mismo `solicitudes.json` que la versión `estado-inicial`.

| ID | Técnica (catálogo de Fowler) | Smells que resuelve | Principio | Commit |
|---|---|---|---|---|
| R1 | Extract Method + Rename Variable | CS-02, CS-04, CS-10, CS-14 | SRP, Clean Code (nombres) | `729a78c` |
| R2 | Replace Magic Literal + Replace Conditional with Polymorphism (tablas en enumeraciones) | CS-05, CS-06 | OCP | `b07e3ad` |
| R3 | Introduce Parameter Object | CS-03, CS-04, CS-11 (defecto D2) | SRP, Clean Code (funciones) | `3b0f091` |
| R4 | Move Method (persistencia) + inyección de dependencias | CS-01, CS-07, CS-08, CS-13 (defecto D3) | DIP, LSP | `2c2413b` |
| R5 | Replace Data Value with Object + Move Method (reglas a la entidad) | CS-05, CS-07 | SRP, ISP | `f8a31c2` |
| R6 | Move Method / Extract Class (reporte) | CS-01, CS-09, CS-12 (defecto D1) | SRP, ISP | `5000633` |
| R7 | Extract Class (consola vs. casos de uso) + Replace Error Code with Exception + Introduce Parameter Object (filtro) | CS-01, CS-07, CS-08, CS-09 | SRP, DIP | `ae97784` |

---

## R1 — Extract Method y renombrado

**Antes**: la búsqueda de una solicitud por id estaba copiada en `cambiar_estado` y en `asignar_responsable`.

```python
s = None
for x in self.d["solicitudes"]:
    if x["id"] == id:
        s = x
if s == None:
    print("Error: no existe la solicitud " + str(id))
    return False
```

**Después**: se extrae un método con nombre que expresa la intención.

```python
def _buscar_solicitud(self, id_solicitud):
    for solicitud in self.datos["solicitudes"]:
        if solicitud["id"] == id_solicitud:
            return solicitud
    return None
```

Con el mismo criterio se extrajeron `_buscar_responsable`, `_buscar_estudiante`, `_email_valido`, `_esta_finalizada`, `_registrar_evento` y `_fecha_hoy`. El método `menu()`, de 62 sentencias, pasó a ser un diccionario de acciones con un método por opción.
**Resultado**: la CC máxima bajó de 27 a 9 y la CC promedio de 10,3 a 3,0.

## R2 — Enumeraciones en lugar de strings y condicionales

**Antes**: tres cadenas `if/elif` sobre strings. Agregar un tipo de solicitud obligaba a modificar `registrar_solicitud`, `buscar` y `reporte`.

```python
if tipo == "RECLAMO_NOTA":
    prioridad = "ALTA"
elif tipo == "BAJA":
    prioridad = "ALTA"
elif tipo == "EQUIVALENCIA":
    ...
```

**Después**: cada regla queda junto al concepto al que pertenece (`solicitudes/modelo.py`).

```python
class TipoSolicitud(StrEnum):
    ...
    @property
    def prioridad_por_defecto(self) -> Prioridad:
        return _PRIORIDAD_POR_TIPO[self]

_TRANSICIONES = {
    Estado.PENDIENTE: frozenset({Estado.EN_REVISION, Estado.RECHAZADA}),
    Estado.EN_REVISION: frozenset({Estado.RESUELTA, Estado.RECHAZADA}),
    Estado.RESUELTA: frozenset(),
    Estado.RECHAZADA: frozenset(),
}
```

**OCP**: un tipo, una prioridad o un estado nuevo se agrega solo en `modelo.py`.

## R3 — Introduce Parameter Object

**Antes**:

```python
def registrar_solicitud(self, legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad):
```

**Después**:

```python
@dataclass(frozen=True)
class PedidoSolicitud:
    estudiante: DatosEstudiante
    tipo: str
    descripcion: str
    prioridad: str = ""

    def validar(self) -> None: ...
```

El objeto se valida **completo** antes de que el servicio modifique datos. Eso corrige el defecto D2: un registro rechazado ya no deja creado al estudiante.

## R4 — Persistencia detrás de una abstracción (DIP)

**Antes**: `open(ARCHIVO)` dentro de la clase de negocio y `except: pass` al cargar. Con un archivo dañado, el sistema arrancaba vacío y lo sobrescribía (defecto D3).

**Después**: `GestorSolicitudes` recibe un `Almacenamiento` por constructor. Hay dos implementaciones intercambiables, `AlmacenamientoJSON` y `AlmacenamientoEnMemoria`. Un archivo dañado lanza `ArchivoDeDatosDanado` y `main.py` termina con código 1 sin tocar el archivo.

## R5 — Entidades del dominio

Los diccionarios se reemplazan por `Solicitud`, `Estudiante`, `Responsable` y `Evento`. Las reglas de asignación y de cambio de estado se mueven a `Solicitud`, que protege su consistencia y lanza `TransicionInvalida`. `RepositorioSolicitudes` es el único que conoce el formato del JSON, que se mantuvo idéntico al original. `LectorSolicitudes` expone solo lectura (ISP).

## R6 — Reporte en su propia clase

`GeneradorReporte` depende solo de `LectorSolicitudes`. Devuelve texto en lugar de imprimir y calcula el porcentaje con una guarda para `total = 0` (defecto D1).

## R7 — Consola separada de los casos de uso

`GestorSolicitudes` desaparece y se divide en:

- `ServicioSolicitudes` (casos de uso). No lee ni imprime; lanza `ErrorDeNegocio` y recibe el repositorio y el reloj por constructor.
- `ConsolaSolicitudes` (entrada/salida). Es el único lugar que imprime; recibe `leer` y `escribir` inyectables.
- `main.py`, que solo arma las dependencias.

**Antes**: `return -1`, `return False` o `return []` según el método, más un `print` del error.
**Después**: `raise NoEncontrado(...)`. La consola lo atrapa en un único lugar y muestra `Error: <mensaje>`.

---

## Incidente detectado por la red de seguridad

Durante R3, al reorganizar los imports, `buscar` y `reporte` quedaron usando `TipoSolicitud` sin importarlo. El golden master falló con `NameError` en la opción 4 del menú. El error se corrigió antes del commit. Sin la prueba de caja negra, ese error habría llegado al repositorio, porque ningún test unitario cubría todavía esa ruta.
