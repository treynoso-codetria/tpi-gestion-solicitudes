# Arquitectura — antes y después

## Antes (`estado-inicial`)

```mermaid
classDiagram
    class GestorSolicitudes {
        -d : dict
        +cargar()
        +guardar()
        +registrar_solicitud(legajo, nombre, apellido, email, carrera, tipo, descripcion, prioridad)
        +cambiar_estado(id, nuevo)
        +asignar_responsable(id, id_resp)
        +actualizar_email(legajo, email)
        +buscar(estado, tipo, legajo, prioridad)
        +reporte()
        +listar_responsables()
        +menu()
    }
    GestorSolicitudes ..> ArchivoSolicitudesJSON : open() directo
    GestorSolicitudes ..> Reloj : datetime.now() directo
```

Una sola clase de 314 líneas lee el teclado, valida, aplica reglas, persiste e imprime.

## Después (`estado-refactorizado`)

```mermaid
classDiagram
    class ConsolaSolicitudes {
        +ejecutar()
    }
    class ServicioSolicitudes {
        +registrar(PedidoSolicitud) Solicitud
        +cambiar_estado(id, texto) Solicitud
        +asignar_responsable(id, id_resp) Responsable
        +actualizar_email(legajo, email) Estudiante
        +buscar(FiltroSolicitudes) list
    }
    class GeneradorReporte {
        +generar() str
    }
    class LectorSolicitudes {
        <<interface>>
        +listar_solicitudes()
        +listar_responsables()
    }
    class RepositorioSolicitudes
    class Almacenamiento {
        <<interface>>
        +cargar() dict
        +guardar(dict)
    }
    class AlmacenamientoJSON
    class AlmacenamientoEnMemoria
    class Solicitud {
        +asignar(Responsable, fecha)
        +cambiar_estado(Estado, fecha)
    }
    class PedidoSolicitud {
        +validar()
    }

    ConsolaSolicitudes --> ServicioSolicitudes
    ConsolaSolicitudes --> GeneradorReporte
    ServicioSolicitudes --> RepositorioSolicitudes
    ServicioSolicitudes ..> PedidoSolicitud
    GeneradorReporte --> LectorSolicitudes
    RepositorioSolicitudes ..|> LectorSolicitudes
    RepositorioSolicitudes --> Almacenamiento
    AlmacenamientoJSON ..|> Almacenamiento
    AlmacenamientoEnMemoria ..|> Almacenamiento
    RepositorioSolicitudes --> Solicitud
```

## Módulos

| Módulo | Responsabilidad única | Depende de |
|---|---|---|
| `main.py` | Armar las dependencias y arrancar | todos (raíz de composición) |
| `solicitudes/cli.py` | Leer del teclado y mostrar resultados | servicio, reporte |
| `solicitudes/servicio.py` | Casos de uso | repositorio, pedidos, modelo |
| `solicitudes/reporte.py` | Construir el texto del reporte | `LectorSolicitudes` |
| `solicitudes/repositorio.py` | Traducir entidades ↔ documento | `Almacenamiento` |
| `solicitudes/almacenamiento.py` | Leer y escribir el documento | disco (solo `AlmacenamientoJSON`) |
| `solicitudes/pedidos.py` | Objetos de entrada y su validación | modelo, validaciones |
| `solicitudes/modelo.py` | Entidades, enumeraciones y reglas del dominio | errores |
| `solicitudes/validaciones.py` | Reglas de formato | — |
| `solicitudes/errores.py` | Jerarquía de errores de negocio | — |

Las dependencias apuntan hacia el dominio (`modelo.py`), que no depende de la consola ni del disco.
