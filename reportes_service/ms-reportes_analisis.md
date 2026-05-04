# Análisis de Microservicio: ms-reportes [REP]

> **Documento generado a partir de:** Propuesta de Arquitectura y Requisitos Funcionales — ERP Universitario v1.0  
> **Fecha de generación:** Marzo 2026  
> **Microservicio analizado:** ms-reportes [REP]

---

## 1. Extracción Textual

A continuación se copian, sin modificar, todos los fragmentos del documento original que mencionan o son relevantes para el microservicio `ms-reportes`.

---

### Fragmento 1 — Sección 5: Arquitectura General › Módulo 6 — Transversales

> **Módulo 6 — Transversales**
>
> Servicios de soporte consumidos por los demás módulos: notificaciones, auditoría y reportes.
>
> - ms-notificaciones
> - ms-auditoria
> - ms-reportes

---

### Fragmento 2 — Sección 2: Objetivo del Sistema

> Proveer servicios transversales de notificaciones, auditoría y generación de reportes.

---

### Fragmento 3 — Sección 7.19: Especificación funcional de ms-reportes

> #### 7.19 ms-reportes [REP]
>
> **Propósito:** Genera reportes consolidados consumiendo datos de múltiples microservicios del sistema. Soporta plantillas de reporte configurables, programación automática de generación y exportación en formatos CSV y JSON.
>
> ##### Información que gestiona
>
> **Reportes:** Cada reporte generado. Se requiere almacenar: la plantilla utilizada, un nombre descriptivo, los parámetros con los que se generó (en formato JSON), el resultado almacenado en caché, el formato de salida (CSV o JSON), el estado (pendiente, generando, completado o error), quién lo solicitó, la fecha de solicitud, la fecha de generación y el tamaño del resultado en bytes. Se debe registrar la fecha de creación.
>
> **Plantillas de reporte:** Definición de los tipos de reporte disponibles. Se requiere almacenar: un nombre único, una descripción, los microservicios de los cuales se obtienen datos, los parámetros requeridos para la generación, la configuración de las consultas a realizar (en formato JSON) y el estado. Se debe registrar la fecha de creación y de actualización.
>
> **Programaciones:** Configuración para la generación automática de reportes. Se requiere almacenar: la plantilla del reporte, la periodicidad (diario, semanal o mensual), el día de ejecución, la hora de ejecución, los destinatarios que deben recibir el reporte, el estado (activa o pausada), la fecha de la última ejecución y la fecha de la próxima ejecución. Se debe registrar la fecha de creación y de actualización.
>
> ##### Requisitos funcionales
>
> - El sistema debe permitir solicitar la generación de un reporte proporcionando una plantilla y los parámetros requeridos.
> - El sistema debe consumir datos de los microservicios definidos en la plantilla, consolidarlos y generar el reporte.
> - El sistema debe almacenar el resultado generado como caché para evitar recalcular el mismo reporte si se solicita nuevamente con los mismos parámetros.
> - El sistema debe permitir descargar un reporte generado en formato CSV o JSON.
> - El sistema debe permitir crear, consultar, actualizar y eliminar plantillas de reporte.
> - El sistema debe permitir configurar la generación automática de reportes según una periodicidad definida (diaria, semanal o mensual). Los reportes programados deben ejecutarse automáticamente en la fecha y hora configuradas.
> - El sistema debe permitir ejecutar manualmente los reportes programados que estén pendientes.
> - El sistema debe permitir listar, crear, actualizar y desactivar programaciones de reportes.
>
> ##### Dependencias con otros servicios
>
> - Debe consultar al servicio de calificaciones para generar reportes de rendimiento académico y promedios por programa.
> - Debe consultar al servicio de inventario para generar reportes de estado de activos, depreciación y stock bajo.
> - Debe consultar al servicio de presupuesto para generar reportes de ejecución presupuestal por área y periodo.
> - Debe enviar registros de log al servicio de auditoría de forma asíncrona con cada operación realizada.

---

### Fragmento 4 — Sección 8: Mapa de Dependencias entre Microservicios

> | Microservicio | Consume datos de |
> |---|---|
> | ms-reportes | ms-calificaciones, ms-inventario, ms-presupuesto |
>
> Adicionalmente, todos los microservicios (excepto ms-autenticacion y ms-roles entre sí) consumen:
>
> - **ms-autenticacion** para validar sesiones activas.
> - **ms-roles** para validar permisos por funcionalidad.
> - **ms-auditoria** para enviar registros de log de forma asíncrona.

---

### Fragmento 5 — Sección 6: Reglas Transversales del Sistema (aplican a ms-reportes)

> **6.1 Validación de Sesión Obligatoria**
> Toda operación realizada por un usuario a través de cualquier microservicio debe ser precedida por una validación de sesión activa. El microservicio que recibe la petición del usuario debe consultar al servicio de autenticación para confirmar que la sesión es válida antes de ejecutar cualquier lógica de negocio. Si la sesión no es válida, el sistema debe rechazar la petición inmediatamente sin procesarla.
>
> **6.2 Validación de Permisos por Funcionalidad**
> Cada funcionalidad del sistema tiene asociado un código de permiso único. Después de validar la sesión, el microservicio debe consultar al servicio de roles para verificar que el rol del usuario tiene autorización para ejecutar la funcionalidad solicitada. Si el usuario no tiene el permiso correspondiente, el sistema debe rechazar la petición.
>
> **6.3 Tokens de Aplicación para Comunicación entre Servicios**
> Cada microservicio posee un token de aplicación único que lo identifica ante los demás servicios. Este token es fijo (no expira ni se renueva automáticamente) y solo puede ser actualizado de forma manual por un administrador. Los tokens se almacenan cifrados con AES-256 y se transmiten cifrados en cada petición entre servicios. Cualquier microservicio puede comunicarse con cualquier otro siempre que posea un token activo y válido.
>
> **6.4 Cifrado de Credenciales**
> Las contraseñas de los usuarios nunca se almacenan en texto plano. Se guardan como hash generado con bcrypt con un factor de costo mínimo de 12. Además, las contraseñas se transmiten cifradas desde el cliente hacia el servidor utilizando AES-256 con codificación Base64. El servidor descifra la contraseña recibida antes de compararla con el hash almacenado. Los tokens de aplicación siguen la misma política: se almacenan cifrados y se transmiten cifrados. En ningún caso deben aparecer credenciales en texto plano en logs, respuestas del sistema ni archivos de configuración.
>
> **6.5 Trazabilidad Distribuida (Request ID)**
> Cada petición que ingresa al sistema recibe un identificador único de rastreo con el formato: código del servicio que la recibe, seguido de un timestamp Unix y un identificador corto aleatorio (ejemplo: `PED-1740000000-a3f8b2`). Este identificador se propaga a todos los microservicios que participan en el procesamiento de la petición. Si un servicio recibe una petición que ya trae un identificador de rastreo (porque proviene de otro servicio), debe reutilizarlo en lugar de generar uno nuevo. Toda respuesta del sistema, independientemente de si la operación fue exitosa o fallida, debe incluir este identificador tanto en las cabeceras como en el cuerpo de la respuesta.
>
> **6.6 Auditoría y Logs en Formato JSON**
> Cada operación realizada en cualquier microservicio debe generar un registro de log en formato JSON que contenga: la fecha y hora de la operación, el identificador de rastreo de la petición, el nombre del microservicio, la funcionalidad ejecutada, el método utilizado, el código de respuesta, la duración en milisegundos, el identificador del usuario que realizó la operación y un detalle descriptivo. Estos registros se envían de forma asíncrona al servicio de auditoría, de manera que el envío no bloquee ni retrase la respuesta al usuario. Si el envío al servicio de auditoría falla, el microservicio debe continuar operando normalmente.
>
> **6.7 Estructura de Respuesta Estándar**
> Todas las respuestas del sistema deben seguir una estructura uniforme que incluya: el identificador de rastreo de la petición, un indicador de éxito o error, los datos resultantes de la operación, un mensaje descriptivo y la fecha y hora de la respuesta.

---

## 2. Información General

| Campo | Detalle |
|---|---|
| **Nombre** | ms-reportes |
| **Código** | REP |
| **Módulo** | Módulo 6 — Transversales |
| **Stack** | FastAPI + Python + PostgreSQL |

**Propósito:**  
`ms-reportes` es el servicio encargado de generar reportes consolidados del sistema, consumiendo datos de múltiples microservicios según plantillas configurables. Soporta exportación en formatos CSV y JSON, almacenamiento de resultados en caché y programación automática de generación periódica.

**Rol dentro del sistema:**  
Actúa como capa de inteligencia transversal que agrega y presenta información de los módulos Académico, Financiero y de Recursos. Es consumido por usuarios con rol administrativo que requieren visibilidad consolidada del estado institucional. No produce datos propios de negocio; su valor reside en la consolidación y presentación de datos existentes en otros servicios.

---

## 3. Reglas de Negocio

### 3.1 Reglas Transversales (aplican a todos los microservicios, incluido ms-reportes)

- **RT-01 — Validación de sesión obligatoria:** Antes de ejecutar cualquier operación, debe consultar a `ms-autenticacion` para verificar que la sesión del usuario es activa y válida. Si la sesión no es válida, debe rechazar la petición de inmediato sin procesar ninguna lógica.

- **RT-02 — Validación de permisos por funcionalidad:** Tras validar la sesión, debe consultar a `ms-roles` para confirmar que el rol del usuario tiene el permiso correspondiente a la funcionalidad solicitada. Si no tiene permiso, debe rechazar la petición.

- **RT-03 — Token de aplicación para comunicación entre servicios:** Debe identificarse ante los servicios de los que consume datos (`ms-calificaciones`, `ms-inventario`, `ms-presupuesto`, `ms-auditoria`) mediante su token de aplicación único, almacenado y transmitido cifrado con AES-256.

- **RT-04 — Cifrado de credenciales:** Ninguna credencial, token ni contraseña debe aparecer en texto plano en logs, respuestas ni configuraciones.

- **RT-05 — Trazabilidad distribuida (Request ID):** Cada petición entrante debe recibir un identificador de rastreo con formato `REP-{timestamp}-{id_corto}`. Si la petición proviene de otro servicio y ya trae un identificador, debe reutilizarlo. El identificador debe incluirse en cabeceras y cuerpo de toda respuesta.

- **RT-06 — Auditoría asíncrona:** Cada operación debe generar un registro de log en formato JSON y enviarlo de forma asíncrona a `ms-auditoria`. El envío no debe bloquear la respuesta al usuario. Si el envío falla, el servicio debe continuar operando normalmente.

- **RT-07 — Estructura de respuesta estándar:** Toda respuesta debe incluir: identificador de rastreo, indicador de éxito o error, datos resultantes, mensaje descriptivo y fecha/hora de la respuesta.

### 3.2 Reglas Específicas del Microservicio

- **RE-01 — Generación basada en plantilla:** No se puede generar un reporte sin una plantilla válida y activa que defina los microservicios fuente, los parámetros requeridos y la configuración de consultas.

- **RE-02 — Caché de resultados:** Si se solicita un reporte con los mismos parámetros de una generación anterior, el sistema debe devolver el resultado almacenado en caché sin volver a calcularlo.

- **RE-03 — Formatos de exportación permitidos:** Los reportes solo pueden descargarse en formato CSV o JSON. No se admiten otros formatos de salida.

- **RE-04 — Estados del reporte:** Un reporte pasa por los estados: `pendiente → generando → completado` o `pendiente → generando → error`. No puede descargarse un reporte que no esté en estado `completado`.

- **RE-05 — Periodicidades válidas para programaciones:** Las programaciones automáticas solo admiten periodicidades `diario`, `semanal` o `mensual`.

- **RE-06 — Estados de programación:** Una programación puede estar en estado `activa` o `pausada`. Los reportes programados solo se ejecutan automáticamente si la programación está en estado `activa`.

- **RE-07 — Ejecución manual de reportes programados:** El sistema debe permitir forzar manualmente la ejecución de reportes programados que se encuentren pendientes, independientemente de su fecha de próxima ejecución.

- **RE-08 — Datos de programación auditables:** Toda programación debe registrar su fecha de creación, fecha de actualización, fecha de última ejecución y fecha de próxima ejecución.

---

## 4. Entidades y Datos

### 4.1 Reporte

> **Cada reporte generado.** Se requiere almacenar: la plantilla utilizada, un nombre descriptivo, los parámetros con los que se generó (en formato JSON), el resultado almacenado en caché, el formato de salida (CSV o JSON), el estado (pendiente, generando, completado o error), quién lo solicitó, la fecha de solicitud, la fecha de generación y el tamaño del resultado en bytes. Se debe registrar la fecha de creación.

| Atributo | Detalle |
|---|---|
| `plantilla` | Referencia a la plantilla utilizada para la generación |
| `nombre` | Nombre descriptivo del reporte |
| `parametros` | Parámetros de generación en formato JSON |
| `resultado_cache` | Resultado almacenado en caché |
| `formato_salida` | CSV o JSON |
| `estado` | pendiente, generando, completado o error |
| `solicitado_por` | Usuario que solicitó el reporte |
| `fecha_solicitud` | Fecha y hora de la solicitud |
| `fecha_generacion` | Fecha y hora en que se completó la generación |
| `tamano_bytes` | Tamaño del resultado en bytes |
| `fecha_creacion` | Fecha de creación del registro |

---

### 4.2 Plantilla de Reporte

> **Definición de los tipos de reporte disponibles.** Se requiere almacenar: un nombre único, una descripción, los microservicios de los cuales se obtienen datos, los parámetros requeridos para la generación, la configuración de las consultas a realizar (en formato JSON) y el estado. Se debe registrar la fecha de creación y de actualización.

| Atributo | Detalle |
|---|---|
| `nombre` | Nombre único de la plantilla |
| `descripcion` | Descripción del tipo de reporte |
| `microservicios_fuente` | Microservicios de los cuales se obtienen datos |
| `parametros_requeridos` | Parámetros que debe proporcionar quien solicite el reporte |
| `configuracion_consultas` | Configuración de las consultas a realizar (JSON) |
| `estado` | Estado de la plantilla (activa/inactiva) |
| `fecha_creacion` | Fecha de creación del registro |
| `fecha_actualizacion` | Fecha de la última actualización |

---

### 4.3 Programación

> **Configuración para la generación automática de reportes.** Se requiere almacenar: la plantilla del reporte, la periodicidad (diario, semanal o mensual), el día de ejecución, la hora de ejecución, los destinatarios que deben recibir el reporte, el estado (activa o pausada), la fecha de la última ejecución y la fecha de la próxima ejecución. Se debe registrar la fecha de creación y de actualización.

| Atributo | Detalle |
|---|---|
| `plantilla` | Referencia a la plantilla del reporte programado |
| `periodicidad` | diario, semanal o mensual |
| `dia_ejecucion` | Día de ejecución según la periodicidad configurada |
| `hora_ejecucion` | Hora a la que se ejecuta el reporte |
| `destinatarios` | Usuarios o roles que deben recibir el reporte generado |
| `estado` | activa o pausada |
| `ultima_ejecucion` | Fecha y hora de la última ejecución realizada |
| `proxima_ejecucion` | Fecha y hora calculada para la próxima ejecución |
| `fecha_creacion` | Fecha de creación del registro |
| `fecha_actualizacion` | Fecha de la última actualización |

---

## 5. Funcionalidades Requeridas

> - El sistema debe permitir solicitar la generación de un reporte proporcionando una plantilla y los parámetros requeridos.
> - El sistema debe consumir datos de los microservicios definidos en la plantilla, consolidarlos y generar el reporte.
> - El sistema debe almacenar el resultado generado como caché para evitar recalcular el mismo reporte si se solicita nuevamente con los mismos parámetros.
> - El sistema debe permitir descargar un reporte generado en formato CSV o JSON.
> - El sistema debe permitir crear, consultar, actualizar y eliminar plantillas de reporte.
> - El sistema debe permitir configurar la generación automática de reportes según una periodicidad definida (diaria, semanal o mensual). Los reportes programados deben ejecutarse automáticamente en la fecha y hora configuradas.
> - El sistema debe permitir ejecutar manualmente los reportes programados que estén pendientes.
> - El sistema debe permitir listar, crear, actualizar y desactivar programaciones de reportes.

---

## 6. Dependencias (de quién dependo)

| Microservicio | Información / Funcionalidad consumida | Contexto de uso |
|---|---|---|
| **ms-autenticacion** | Validación de sesión activa del usuario | Antes de ejecutar cualquier operación (regla transversal RT-01) |
| **ms-roles** | Validación de permisos por funcionalidad | Después de validar sesión, antes de ejecutar la operación (regla transversal RT-02) |
| **ms-calificaciones** | Datos de rendimiento académico y promedios por programa | Al generar reportes académicos según la plantilla configurada |
| **ms-inventario** | Estado de activos, depreciación y stock bajo | Al generar reportes de inventario y activos según la plantilla configurada |
| **ms-presupuesto** | Datos de ejecución presupuestal por área y periodo | Al generar reportes financieros según la plantilla configurada |
| **ms-auditoria** | Recepción de registros de log | De forma asíncrona con cada operación realizada (regla transversal RT-06) |

---

## 7. Consumidores (quién depende de mí)

No se encontró información relevante en el documento que indique que algún otro microservicio del sistema consuma datos o servicios de `ms-reportes`. Según el mapa de dependencias de la Sección 8, ningún microservicio declara a `ms-reportes` como fuente de datos.

`ms-reportes` es un servicio terminal de consulta: agrega y presenta información, pero no es fuente de datos para otros servicios del sistema.

---

*Fin del documento de análisis — ms-reportes [REP]*
