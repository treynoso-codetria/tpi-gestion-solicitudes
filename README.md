# Gestión de Solicitudes Académicas

Sistema de consola para registrar solicitudes de estudiantes (certificados, equivalencias, cambios de comisión, reclamos de nota y bajas), clasificarlas por tipo, prioridad y estado, asignar responsables, buscarlas y obtener un reporte.

Trabajo Práctico Integrador de **Metodología de Sistemas II** (Tecnicatura Universitaria en Programación a Distancia, UTN). El objetivo del trabajo no es la funcionalidad, sino **mejorar la calidad interna** de una versión base con problemas, sin alterar su comportamiento externo.

## Requisitos

- Python 3.11 o superior. La aplicación usa solo la biblioteca estándar.
- Opcional, para medir la calidad: `pip install -r requirements-dev.txt`.

## Uso

```bash
python main.py
```

Los datos se guardan en `solicitudes.json`, en la carpeta desde donde se ejecuta. La primera vez se crean cuatro responsables de ejemplo.

| Opción | Operación |
|---|---|
| 1 | Registrar solicitud (si no se indica prioridad, se asigna según el tipo) |
| 2 | Cambiar estado: `PENDIENTE → EN_REVISION → RESUELTA / RECHAZADA`, o bien `PENDIENTE → RECHAZADA` |
| 3 | Asignar responsable (es obligatorio para pasar a revisión) |
| 4 | Buscar o filtrar por estado, tipo, legajo y prioridad |
| 5 | Reporte por estado, por tipo y por carga de cada responsable |
| 6 | Listar responsables |
| 7 | Actualizar el email de un estudiante |

Todos los datos de ejemplo del repositorio son sintéticos.

## Pruebas y métricas

```bash
python -m unittest discover -s tests -t .              # 56 tests
coverage run -m unittest discover -s tests -t . && coverage combine && coverage report
radon cc solicitudes main.py -s -a                       # complejidad ciclomática
radon mi solicitudes main.py -s                          # índice de mantenibilidad
pylint solicitudes main.py
```

| Métrica | `estado-inicial` | `estado-refactorizado` |
|---|---|---|
| CC máxima / promedio | 27 / 10,3 | 5 / 1,9 |
| Índice de mantenibilidad (peor archivo) | 14,6 | 53,4 |
| pylint | 8,21 / 10 | 9,91 / 10 |
| Tests | 0 | 56 |
| Cobertura de sentencias / ramas | — | 99,6 % / 95,5 % |
| Defectos conocidos abiertos | 4 (D1, D2, D3, CR-10) | 0 |

## Estructura

```
main.py                  punto de entrada: arma las dependencias
solicitudes/
  cli.py                 consola (unica parte que lee e imprime)
  servicio.py            casos de uso
  reporte.py             reporte resumido
  repositorio.py         entidades <-> documento JSON
  almacenamiento.py      archivo JSON / memoria (intercambiables)
  pedidos.py             objetos parametro y su validacion
  modelo.py              entidades, enumeraciones y reglas del dominio
  validaciones.py        reglas de formato
  errores.py             errores de negocio
tests/
  test_golden_master.py  caja negra: compara contra la version base
  test_defectos_conocidos.py
  test_*.py              pruebas unitarias y de contrato
  golden/                escenario y resultados esperados
docs/                    diagnostico, refactorings, code review, decisiones, evidencias
```

## Historial y tags

| Tag | Hito |
|---|---|
| `estado-inicial` | Versión base con los problemas a diagnosticar |
| `etapa-diagnostico` | Diagnóstico, golden master y defectos documentados |
| `etapa-refactoring` | Refactorings R1 a R7 aplicados |
| `etapa-pruebas` | Pruebas unitarias, de contrato y verificación antes/después |
| `etapa-docs` | Documentación técnica completa |
| `estado-refactorizado` | Estado final del código |

Para ver la versión base: `git checkout estado-inicial`.

## Documentación

- [Diagnóstico de code smells](docs/diagnostico.md)
- [Refactorings aplicados](docs/refactorings.md)
- [Arquitectura antes/después](docs/arquitectura.md)
- [Code review: checklist y observaciones](docs/code-review.md)
- [Decisiones técnicas](docs/decisiones-tecnicas.md)
- [Evidencias](docs/evidencias/)
- [Declaración de uso de IA](docs/uso-ia.md)

## Autor

Thomas Reynoso. Comisión M25 C4-09.
