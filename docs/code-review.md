# Code review — versión refactorizada

**Alcance:** commits `etapa-diagnostico..etapa-pruebas` (R1 a R7 y la suite de pruebas).
**Fuentes:** lectura completa del diff, `pylint 4.1.3`, `radon 6.0.1`, `coverage 7.17.0` y ejecución manual de la consola.
**Criterio de aprobación:** todos los ítems bloqueantes del checklist en ✅. Los no bloqueantes pueden quedar aceptados con justificación escrita.

## 1. Checklist técnico

| # | Área | Criterio | Bloqueante | Resultado inicial |
|---|---|---|---|---|
| 1 | Comportamiento | El golden master pasa: salida y JSON idénticos a `estado-inicial` | Sí | ✅ |
| 2 | Comportamiento | Los defectos D1-D3 tienen test de regresión y pasan | Sí | ✅ |
| 3 | Pruebas | Toda la suite pasa sin tests omitidos | Sí | ✅ (54 tests) |
| 4 | Pruebas | Cobertura de sentencias ≥ 80 % y de ramas ≥ 75 % en `solicitudes/` | Sí | ✅ (99,5 % / 95,5 %) |
| 5 | Pruebas | El punto de entrada (`main.py`) se incluye en la medición | No | ❌ CR-04 |
| 6 | SRP | Cada módulo tiene una sola razón para cambiar | Sí | ✅ |
| 7 | OCP | Agregar un tipo, estado o prioridad se hace solo en `modelo.py` | Sí | ✅ |
| 8 | LSP | Las implementaciones de `Almacenamiento` son intercambiables (test de contrato) | Sí | ✅ |
| 9 | ISP | Los consumidores dependen solo de lo que usan (`LectorSolicitudes`) | No | ✅ |
| 10 | DIP | La lógica no crea sus dependencias de infraestructura | Sí | ✅ |
| 11 | Complejidad | Ningún método supera CC 5 | No | ❌ CR-02 |
| 12 | Duplicación | Sin bloques duplicados (pylint `duplicate-code`) | No | ❌ CR-06 |
| 13 | Estilo | pylint sin advertencias de formato (largo de línea ≤ 100) | No | ❌ CR-01 |
| 14 | Estilo | Expresiones idiomáticas (pylint refactor) | No | ❌ CR-03 |
| 15 | Nombres | Nombres en español, descriptivos y sin abreviaturas crípticas | No | ✅ |
| 16 | Errores | Sin `except` desnudo; errores de negocio como excepciones específicas | Sí | ✅ |
| 17 | Errores | La aplicación nunca termina con una traza de Python ante entradas del usuario | Sí | ❌ CR-10 |
| 18 | Datos | Formato de `solicitudes.json` compatible con la versión base | Sí | ✅ |
| 19 | Datos | Sin datos personales reales en código, tests ni ejemplos | Sí | ✅ (datos sintéticos) |
| 20 | Repositorio | Commits atómicos con mensaje descriptivo; un refactoring por commit | No | ✅ |

## 2. Observaciones

| ID | Severidad | Ubicación | Observación | Acción |
|---|---|---|---|---|
| CR-01 | Menor | `cli.py:73`, `repositorio.py:11,74`, `reporte.py:34` | Cuatro líneas superan los 100 caracteres. | Extraer constantes y partir líneas. |
| CR-02 | Menor | `RepositorioSolicitudes.__init__` (CC 6) | El constructor carga, convierte y siembra datos. | Extract Method: `_documento_vacio()` y `_crear_responsables_iniciales_si_faltan()`. |
| CR-03 | Menor | `FiltroSolicitudes.acepta` | `buscado == "" or buscado == valor` puede expresarse como pertenencia. | Usar `buscado in ("", valor)`. |
| CR-04 | Menor | `.coveragerc` | `main.py` queda fuera de la medición. Solo lo ejercita el golden master. | Agregar `main` a `source`. |
| CR-05 | Informativa | `RepositorioSolicitudes.listar_solicitudes` | Devuelve las entidades vivas: un consumidor podría modificarlas sin llamar a `guardar_cambios()`. | Aceptado: es el patrón *unit of work* del servicio. Los únicos que escriben son los casos de uso. Queda documentado. |
| CR-06 | Menor | `ServicioSolicitudes._registrar_o_actualizar_estudiante` | La conversión de `DatosEstudiante` a `Estudiante` se escribe campo por campo fuera del objeto que tiene los datos (Feature Envy). | Move Method: `DatosEstudiante.crear_estudiante()`. Que los dos tipos tengan los mismos campos es intencional: uno es entrada inmutable y otro es una entidad mutable. |
| CR-07 | Informativa | `Solicitud` (10 atributos) | pylint `too-many-instance-attributes`. | Aceptado: refleja el registro persistido. Dividirla cambiaría el formato del JSON. |
| CR-08 | Informativa | `ConsolaSolicitudes`, `GeneradorReporte` | pylint `too-few-public-methods`. | Aceptado: falso positivo en clases de responsabilidad única con un punto de entrada. |
| CR-09 | Informativa | Mensajes de consola | Los textos no llevan tildes. | Aceptado: se conservan iguales a la versión base para no alterar el comportamiento externo. |
| CR-10 | **Mayor** | `ConsolaSolicitudes.ejecutar` | Si la entrada termina sin la opción 0 (Ctrl+D o fin de archivo), la aplicación muere con `EOFError` y muestra una traza. El defecto ya existía en la versión base y no lo detectó el diagnóstico. | Capturar `EOFError` y `KeyboardInterrupt` y salir con "Hasta luego". Se agrega un test de caja negra y uno unitario. |

## 3. Correcciones realizadas

Ver la sección 4. Se completa después de aplicar las correcciones.
