# Diagnóstico de calidad — versión base (`estado-inicial`)

Analizado sobre `gestor.py` (314 líneas, una sola clase) con `radon` 6.0.1, `pylint` 4.1.3 y lectura manual.
Las salidas completas de las herramientas están en `docs/evidencias/antes/`.

## Métricas de partida

| Métrica | Valor | Referencia |
|---|---|---|
| Líneas de código (LOC) | 314 | — |
| Clases / métodos | 1 / 12 | — |
| Complejidad ciclomática máxima | 27 (`registrar_solicitud`, rango D) | ≤ 10 por método |
| Complejidad ciclomática promedio | 10,3 (rango C) | ≤ 5 |
| Índice de mantenibilidad (radon MI) | 14,59 | > 20 deseable |
| Puntaje pylint | 8,21 / 10 | ≥ 9,5 |
| Comentarios | 2 % | — |
| `print(...)` dentro de la clase de negocio | 51 | 0 |

## Code smells y debilidades técnicas

| ID | Smell | Ubicación | Evidencia | Impacto | Riesgo de mantenimiento | Prioridad |
|---|---|---|---|---|---|---|
| CS-01 | Large Class / God Class | `gestor.py:8-314` | `GestorSolicitudes` lee el teclado, valida, aplica reglas, persiste en JSON, arma reportes e imprime. | Toda modificación pasa por la misma clase; cambios no relacionados chocan entre sí. | Alto: viola SRP, imposible testear una parte aislada. | Alta |
| CS-02 | Long Method | `registrar_solicitud` (35-109, CC 27), `menu` (252-314, 62 sentencias), `buscar` (186-213, CC 21) | radon rango D; pylint `too-many-branches`, `too-many-statements`. | Difícil de leer y de probar por partes. | Alto: cualquier regla nueva agranda el método. | Alta |
| CS-03 | Long Parameter List | `registrar_solicitud(legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad)` (35) | 8 parámetros del mismo tipo (`str`); pylint `too-many-arguments`. | Fácil invertir argumentos sin que nada falle. | Medio | Media |
| CS-04 | Duplicated Code | Búsqueda por id (113-115 y 151-153); validación de email (43 y 174); lista de tipos válidos (46 y 187); condición "finalizada" (157, 238, 243); formato de fecha (102, 104, 143, 168) | Mismos bloques copiados. | Una regla que cambia debe actualizarse en varios lugares. | Alto: inconsistencias silenciosas. | Alta |
| CS-05 | Primitive Obsession y strings mágicos | Entidades como `dict`; `"RECHAZADA"` aparece 7 veces, `"RESUELTA"` 6, `"BAJA"` 6 | Sin tipos ni enumeraciones. | Un error de tipeo en un estado no lo detecta nadie. | Medio-alto | Media |
| CS-06 | Switch Statements (condicionales por tipo/estado) | Prioridad por tipo (66-77), plazo por prioridad (85-91), transiciones (121-141) | Cadenas `if/elif` sobre strings. | Agregar un tipo o estado obliga a editar 3+ métodos. | Alto: viola OCP. | Alta |
| CS-07 | Manejo de errores deficiente | `except:` desnudo (27, 278, 286, 292); errores como `print` + retornos heterogéneos (`-1`, `False`, `[]`) | pylint `bare-except`. | Los errores se pierden; origina el defecto D3. | Alto | Alta |
| CS-08 | Dependencias concretas (DIP) | `open(ARCHIVO)` (24, 31); `datetime.now()` (102, 104, 143, 168) | La lógica depende del disco y del reloj reales. | No se puede probar sin tocar el sistema de archivos. | Medio | Media |
| CS-09 | Mezcla de presentación y lógica (Divergent Change) | 51 `print` en la clase de negocio; `buscar` imprime la tabla y además devuelve la lista | — | Cambiar un mensaje obliga a tocar la lógica; no se puede reutilizar desde otra interfaz. | Medio | Media |
| CS-10 | Nombres poco descriptivos / desinformación | `d`, `x`, `s`, `r`, `c`, `p`, `lst`, `flag`, `sin`; `id` oculta el builtin (111, 149, 277) | pylint `redefined-builtin`. | El lector tiene que deducir qué es cada cosa. | Bajo-medio | Baja |
| CS-11 | Efecto secundario antes de validar (defecto D2) | 54-67 vs. 79-83 | El estudiante se crea o se le cambia el email antes de validar la prioridad. Si la prioridad es inválida, el registro se rechaza pero el estudiante queda creado. | Datos inconsistentes. | Alto | Alta |
| CS-12 | Cálculo sin guarda (defecto D1) | `reporte`, línea 225 | `c * 100 / total` con `total = 0` lanza `ZeroDivisionError` y cierra el programa. | El reporte falla en un sistema recién instalado. | Alto | Alta |
| CS-13 | Pérdida de datos ante archivo dañado (defecto D3) | `cargar` (22-28) + `__init__` (14-20) | Si el JSON está dañado, `except: pass` lo ignora, el sistema arranca vacío y sobrescribe el archivo. | Se pierden todas las solicitudes. | Crítico | Alta |
| CS-14 | Código muerto | `import os` (línea 2) | pylint `unused-import`. | Ruido. | Bajo | Baja |

## Defectos confirmados con tests

Los defectos D1, D2 y D3 se fijaron como tests en `tests/test_defectos_conocidos.py`, marcados `@unittest.expectedFailure`.
Esos tests describen el comportamiento correcto y fallan en la versión base.

## Priorización de la corrección

1. **Seguridad de los datos:** CS-13, CS-11 y CS-07. Pérdida o corrupción de información.
2. **Estructura:** CS-01, CS-02 y CS-06. Concentran la complejidad y bloquean la evolución.
3. **Duplicación y tipos:** CS-04, CS-05 y CS-03.
4. **Acoplamiento y legibilidad:** CS-08, CS-09, CS-10, CS-12 y CS-14.

## Red de seguridad antes de refactorizar

- `tests/test_golden_master.py` ejecuta un escenario de 35 operaciones (`tests/golden/escenario.txt`) por consola.
  Compara la salida y el JSON final con lo que produce esta versión.
  El escenario cubre el 94 % de las sentencias de `gestor.py` (`docs/evidencias/antes/cobertura_escenario.txt`).
- `tests/test_defectos_conocidos.py` contiene los tres defectos D1-D3.
