# Decisiones técnicas

Registro breve de las decisiones de diseño, en formato ADR simplificado (contexto → decisión → consecuencias).

## DT-01 — Golden master antes de refactorizar

- **Contexto:** la versión base no tenía ningún test y las operaciones imprimían en lugar de devolver valores. No había forma de escribir tests unitarios sin cambiar primero el código.
- **Decisión:** antes de tocar el código, fijar el comportamiento con un test de caja negra que ejecuta 35 operaciones por consola. El test compara la salida y el JSON resultante con lo que producía la versión base.
- **Consecuencias:** cualquier cambio de comportamiento accidental se detecta. Durante R3 detectó un import faltante. Su costo es que los textos de la consola quedan "congelados". Para cambiar un mensaje a propósito hay que regenerar los archivos golden y documentarlo.

## DT-02 — Conservar el formato del archivo de datos

- **Contexto:** pasar de diccionarios a entidades invitaba a cambiar el formato del JSON (por ejemplo, renombrar `responsable` a `responsable_id`).
- **Decisión:** mantener el esquema exacto. La traducción vive solo en `RepositorioSolicitudes`.
- **Consecuencias:** los archivos existentes siguen funcionando sin migración. El costo es aceptar algunos nombres heredados, como `dias_sla` y `responsable`, en el formato persistido.

## DT-03 — Enumeraciones con tablas en lugar del patrón State completo

- **Contexto:** las transiciones de estado son pocas y no tienen comportamiento propio por estado, más allá de las transiciones permitidas.
- **Decisión:** representar los estados con un `StrEnum` y una tabla de transiciones. No se crea una clase por estado.
- **Consecuencias:** cumple OCP para estados y transiciones con mucho menos código. Si en el futuro cada estado tuviera lógica distinta (notificaciones o vencimientos, por ejemplo), conviene evolucionar al patrón State.

## DT-04 — Inyección por constructor sin framework

- **Contexto:** se necesitaba probar la lógica sin disco y sin fecha real (DIP).
- **Decisión:** `ServicioSolicitudes(repositorio, reloj)` y `RepositorioSolicitudes(almacenamiento)`. `main.py` arma el grafo de objetos.
- **Consecuencias:** los tests usan `AlmacenamientoEnMemoria` y `reloj_fijo` sin *mocks* ni librerías externas. La aplicación sigue usando solo la biblioteca estándar.

## DT-05 — Corregir defectos dentro del refactoring

- **Contexto:** el diagnóstico encontró tres defectos (D1-D3) y el code review uno más (CR-10). Corregir un defecto cambia el comportamiento externo.
- **Decisión:** primero se documentó cada defecto con un test `expectedFailure`, que describe el comportamiento correcto. Luego se corrigió en el refactoring que tocaba esa zona y se quitó la marca.
- **Consecuencias:** el comportamiento externo **se mantiene** en todos los casos del golden master y **mejora** solo en los cuatro casos documentados. Cada mejora tiene su test, que falla en `estado-inicial` y pasa en la versión final.

## DT-06 — Herramientas de análisis solo en desarrollo

- **Contexto:** se necesitaban métricas objetivas antes y después.
- **Decisión:** usar `radon` (complejidad y mantenibilidad), `pylint` (estilo y smells) y `coverage` (sentencias y ramas, incluyendo subprocesos). Se declaran en `requirements-dev.txt`; la aplicación no las necesita para ejecutarse.
- **Consecuencias:** las mediciones son reproducibles con los comandos del README.
