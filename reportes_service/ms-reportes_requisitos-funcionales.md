# Requisitos Funcionales — ms-reportes [REP]

> **Microservicio:** ms-reportes  
> **Código:** REP  
> **Módulo:** Módulo 6 — Transversales  
> **Stack:** FastAPI + Python + PostgreSQL  
> **Fecha de generación:** Marzo 2026  

---

## Tabla de Contenido

### Categoría 1: Requisitos Transversales

| ID | Nombre |
|---|---|
| REP-RF-001 | Validación de Sesión Activa |
| REP-RF-002 | Validación de Permisos por Funcionalidad |
| REP-RF-003 | Generación y Propagación de Request ID |
| REP-RF-004 | Registro de Auditoría Asíncrona |
| REP-RF-005 | Estructura de Respuesta Estándar |

### Categoría 2: Requisitos Funcionales por Entidad

#### Entidad: Plantilla de Reporte

| ID | Nombre |
|---|---|
| REP-RF-006 | Crear Plantilla de Reporte |
| REP-RF-007 | Consultar Plantilla de Reporte |
| REP-RF-008 | Listar Plantillas de Reporte |
| REP-RF-009 | Actualizar Plantilla de Reporte |
| REP-RF-010 | Eliminar Plantilla de Reporte |

#### Entidad: Reporte

| ID | Nombre |
|---|---|
| REP-RF-011 | Solicitar Generación de Reporte |
| REP-RF-012 | Generar Reporte Consolidado |
| REP-RF-013 | Consultar Estado de Reporte |
| REP-RF-014 | Descargar Reporte Generado |

#### Entidad: Programación

| ID | Nombre |
|---|---|
| REP-RF-015 | Crear Programación de Reporte |
| REP-RF-016 | Listar Programaciones de Reporte |
| REP-RF-017 | Actualizar Programación de Reporte |
| REP-RF-018 | Desactivar Programación de Reporte |
| REP-RF-019 | Ejecutar Automáticamente Reportes Programados |
| REP-RF-020 | Ejecutar Manualmente Reporte Programado |

### Categoría 3: Requisitos Sugeridos

| ID | Nombre |
|---|---|
| REP-RF-021 | Listar Reportes Generados |
| REP-RF-022 | Invalidar Caché de Reporte |
| REP-RF-023 | Reactivar Programación Pausada |
| REP-RF-024 | Consultar Detalle de Programación |

---

## Categoría 1: Requisitos Transversales

---

| | | |
|---|---|---|
| **Código** | REP-RF-001 | |
| **Nombre** | Validación de Sesión Activa | |
| **Descripción** | Verifica que el usuario que realiza la petición tenga una sesión activa y válida antes de ejecutar cualquier lógica de negocio. Si la sesión no es válida, la petición es rechazada de inmediato. | |
| **Actores** | Cualquier usuario del sistema; ms-autenticacion | |
| | | |
| **Precondición** | La petición incluye el token de sesión del usuario. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El microservicio recibe la petición del usuario. |
| | 2 | Extrae el token de sesión del encabezado de la petición. |
| | 3 | Consulta a **ms-autenticacion** (servicio de autenticación) para verificar si el token corresponde a una sesión activa. Operación: validar sesión. Respuesta esperada: confirmación de sesión activa e identidad del usuario. |
| | 4 | Si la sesión es válida, el flujo continúa hacia la lógica de negocio. |
| | | |
| **Secuencia alterna** | 4A | Si ms-autenticacion responde que la sesión no es válida o está expirada, el microservicio rechaza la petición con código HTTP 401 y no procesa ninguna lógica adicional. |
| | | |
| **Excepciones** | E1 | Si ms-autenticacion no responde o retorna error, el microservicio debe rechazar la petición con código HTTP 503 para evitar procesar operaciones sin autenticación confirmada. |
| | | |
| **Postcondición** | La identidad del usuario ha sido confirmada y el flujo continúa hacia REP-RF-002. | |
| | | |
| **Comentarios** | Este requisito es invocado por todos los demás requisitos del microservicio como primer paso. Las referencias en otros requisitos se expresan como "Ejecutar REP-RF-001". | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-002 | |
| **Nombre** | Validación de Permisos por Funcionalidad | |
| **Descripción** | Verifica que el rol del usuario autenticado tiene el permiso requerido para ejecutar la funcionalidad solicitada. Si el usuario carece del permiso, la petición es rechazada. | |
| **Actores** | Usuario autenticado; ms-roles | |
| | | |
| **Precondición** | REP-RF-001 ha sido ejecutado exitosamente y la identidad del usuario está disponible. | |
| | El código de permiso de la funcionalidad solicitada está definido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Recupera la identidad y el rol del usuario confirmados en REP-RF-001. |
| | 2 | Determina el código de permiso asociado a la funcionalidad que se intenta ejecutar. |
| | 3 | Consulta a **ms-roles** (servicio de roles) para verificar si el rol del usuario tiene autorización sobre ese código de permiso. Operación: verificar permiso. Respuesta esperada: autorizado o no autorizado. |
| | 4 | Si el usuario tiene el permiso, el flujo continúa hacia la lógica de negocio. |
| | | |
| **Secuencia alterna** | 4A | Si ms-roles responde que el usuario no tiene el permiso, el microservicio rechaza la petición con código HTTP 403. |
| | | |
| **Excepciones** | E1 | Si ms-roles no responde o retorna error, el microservicio debe rechazar la petición con código HTTP 503. |
| | | |
| **Postcondición** | El usuario ha sido autorizado para ejecutar la funcionalidad y el flujo continúa hacia la lógica específica del requisito. | |
| | | |
| **Comentarios** | Este requisito es invocado por todos los requisitos funcionales luego de REP-RF-001. Las referencias en otros requisitos se expresan como "Ejecutar REP-RF-002". | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-003 | |
| **Nombre** | Generación y Propagación de Request ID | |
| **Descripción** | Genera un identificador único de rastreo para cada petición entrante o reutiliza el recibido si la petición proviene de otro microservicio. Este identificador se propaga en todas las llamadas a otros servicios y se incluye en la respuesta. | |
| **Actores** | El propio microservicio (proceso interno) | |
| | | |
| **Precondición** | El microservicio ha recibido una petición. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El microservicio inspecciona la petición entrante en busca de un identificador de rastreo existente (campo `request_id` en cabecera o cuerpo). |
| | 2 | Si no existe, genera un nuevo identificador con el formato `REP-{timestamp_unix}-{id_corto_aleatorio}` (ejemplo: `REP-1740000000-a3f8b2`). |
| | 3 | Si ya existe un identificador (petición proveniente de otro servicio), lo reutiliza sin modificarlo. |
| | 4 | Almacena el identificador en el contexto de la petición para su uso durante todo el ciclo de vida. |
| | 5 | Propaga el identificador en el encabezado de todas las llamadas realizadas a otros microservicios durante el procesamiento. |
| | 6 | Incluye el identificador tanto en los encabezados como en el cuerpo de la respuesta final (ver REP-RF-005). |
| | | |
| **Secuencia alterna** | — | No aplica. | 
| | | |
| **Excepciones** | E1 | Si falla la generación del identificador aleatorio, el microservicio debe reintentar la generación antes de continuar. |
| | | |
| **Postcondición** | Existe un `request_id` activo en el contexto de la petición que será incluido en la respuesta. | |
| | | |
| **Comentarios** | Este proceso ocurre automáticamente al inicio de cada petición, antes de REP-RF-001. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-004 | |
| **Nombre** | Registro de Auditoría Asíncrona | |
| **Descripción** | Al finalizar cada operación, genera un registro de log en formato JSON y lo envía de forma asíncrona a ms-auditoria. El envío no bloquea la respuesta al usuario ni interrumpe la operación si falla. | |
| **Actores** | El propio microservicio (proceso interno); ms-auditoria | |
| | | |
| **Precondición** | Una operación ha sido ejecutada (exitosa o fallida). | |
| | El `request_id` de la petición está disponible (REP-RF-003). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Al concluir la operación, el microservicio construye un objeto JSON con los siguientes campos: fecha y hora de la operación, `request_id`, nombre del microservicio (`ms-reportes`), funcionalidad ejecutada, método HTTP, código de respuesta HTTP, duración en milisegundos, identificador del usuario y detalle descriptivo de la operación. |
| | 2 | Envía el registro de forma asíncrona a **ms-auditoria** (servicio de auditoría). Operación: registrar log. El envío se realiza en segundo plano sin esperar respuesta. |
| | 3 | La respuesta ya ha sido enviada al usuario independientemente del resultado del envío a auditoría. |
| | | |
| **Secuencia alterna** | — | No aplica. |
| | | |
| **Excepciones** | E1 | Si el envío a ms-auditoria falla (timeout, error de red, servicio no disponible), el microservicio registra el fallo en su log local y continúa operando con normalidad. El fallo de auditoría no afecta la respuesta al usuario. |
| | | |
| **Postcondición** | El log de la operación fue enviado a ms-auditoria o, en caso de fallo, registrado localmente. | |
| | | |
| **Comentarios** | Ninguna credencial, token o dato sensible debe aparecer en texto plano en el registro de log (regla RT-04). | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-005 | |
| **Nombre** | Estructura de Respuesta Estándar | |
| **Descripción** | Define el formato uniforme que deben seguir todas las respuestas del microservicio, independientemente de si la operación fue exitosa o fallida. | |
| **Actores** | El propio microservicio (proceso interno) | |
| | | |
| **Precondición** | Una operación ha sido procesada y existe un resultado (exitoso o de error). | |
| | El `request_id` está disponible (REP-RF-003). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El microservicio construye el objeto de respuesta con los siguientes campos: `request_id` (identificador de rastreo), `success` (booleano indicador de éxito o error), `data` (datos resultantes de la operación, puede ser `null` en caso de error), `message` (mensaje descriptivo de la operación) y `timestamp` (fecha y hora de la respuesta en ISO 8601). |
| | 2 | Incluye el `request_id` tanto en el encabezado HTTP de la respuesta como en el cuerpo JSON. |
| | 3 | Retorna la respuesta con el código HTTP correspondiente al resultado de la operación. |
| | | |
| **Secuencia alterna** | — | No aplica. |
| | | |
| **Excepciones** | — | No aplica. |
| | | |
| **Postcondición** | La respuesta enviada al cliente cumple con la estructura estándar definida. | |
| | | |
| **Comentarios** | Esta estructura aplica a todas las respuestas del microservicio, incluyendo errores de validación (400), autenticación (401), permisos (403), no encontrado (404) y errores internos (500). | |

---

## Categoría 2: Requisitos Funcionales por Entidad

### Entidad: Plantilla de Reporte

---

| | | |
|---|---|---|
| **Código** | REP-RF-006 | |
| **Nombre** | Crear Plantilla de Reporte | |
| **Descripción** | Permite registrar una nueva plantilla de reporte en el sistema, definiendo los microservicios fuente, los parámetros requeridos y la configuración de consultas que se usará para generar reportes. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | El nombre de la plantilla no existe previamente en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003 (generación de Request ID). |
| | 2 | Ejecutar REP-RF-001 (validación de sesión). |
| | 3 | Ejecutar REP-RF-002 (validación de permisos). |
| | 4 | Recibe y valida el cuerpo de la petición: `nombre` (único, obligatorio), `descripcion` (obligatoria), `microservicios_fuente` (lista, obligatorio), `parametros_requeridos` (JSON, obligatorio), `configuracion_consultas` (JSON, obligatorio) y `estado` (valor por defecto: `activa`). |
| | 5 | Verifica que el `nombre` de la plantilla no exista ya en el sistema. |
| | 6 | Persiste la nueva plantilla en la base de datos con `fecha_creacion` y `fecha_actualizacion` con la fecha/hora actual. |
| | 7 | Construye y retorna la respuesta (REP-RF-005) con los datos de la plantilla creada y código HTTP 201. |
| | 8 | Ejecutar REP-RF-004 (auditoría asíncrona). |
| | | |
| **Secuencia alterna** | 5A | Si el nombre ya existe, retorna error con código HTTP 409 y mensaje descriptivo. |
| | | |
| **Excepciones** | E1 | Si algún campo obligatorio está ausente o tiene formato inválido, retorna HTTP 400 con detalle de los campos fallidos. |
| | E2 | Si ocurre un error al persistir en base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La plantilla queda registrada en estado `activa` y disponible para ser utilizada en la generación de reportes. | |
| | | |
| **Comentarios** | El campo `configuracion_consultas` debe ser un JSON válido que defina cómo consultar cada microservicio fuente. Su estructura exacta queda [Por definir] según el diseño técnico del servicio. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-007 | |
| **Nombre** | Consultar Plantilla de Reporte | |
| **Descripción** | Permite obtener el detalle completo de una plantilla de reporte específica a partir de su identificador. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La plantilla con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la plantilla como parámetro de ruta. |
| | 5 | Busca la plantilla en la base de datos por su identificador. |
| | 6 | Retorna la respuesta (REP-RF-005) con el detalle completo de la plantilla y código HTTP 200. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la plantilla no existe, retorna HTTP 404 con mensaje descriptivo. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario recibe el detalle completo de la plantilla solicitada. | |
| | | |
| **Comentarios** | [Por definir] si se debe restringir la consulta de plantillas inactivas o si son visibles para todos los roles autorizados. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-008 | |
| **Nombre** | Listar Plantillas de Reporte | |
| **Descripción** | Permite obtener el listado de plantillas de reporte registradas en el sistema, con posibilidad de filtrar por estado. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe parámetros de consulta opcionales: `estado` (activa/inactiva), paginación (`page`, `page_size`). |
| | 5 | Consulta la base de datos aplicando los filtros recibidos. |
| | 6 | Retorna la respuesta (REP-RF-005) con la lista de plantillas y metadatos de paginación, código HTTP 200. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 6A | Si no existen plantillas con los filtros aplicados, retorna lista vacía con código HTTP 200. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario recibe el listado de plantillas que cumplen con los criterios de búsqueda. | |
| | | |
| **Comentarios** | [Por definir] criterios adicionales de filtrado (por nombre, por microservicio fuente). | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-009 | |
| **Nombre** | Actualizar Plantilla de Reporte | |
| **Descripción** | Permite modificar los datos de una plantilla de reporte existente, incluyendo su descripción, configuración de consultas, parámetros y estado. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La plantilla con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la plantilla (ruta) y los campos a actualizar en el cuerpo. |
| | 5 | Verifica que la plantilla exista. |
| | 6 | Si se cambia el `nombre`, verifica que el nuevo nombre no esté en uso por otra plantilla. |
| | 7 | Actualiza los campos recibidos y registra la `fecha_actualizacion` con la fecha/hora actual. |
| | 8 | Retorna la respuesta (REP-RF-005) con los datos actualizados, código HTTP 200. |
| | 9 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la plantilla no existe, retorna HTTP 404. |
| | 6A | Si el nuevo nombre ya está en uso, retorna HTTP 409. |
| | | |
| **Excepciones** | E1 | Si el cuerpo de la petición contiene campos con formato inválido, retorna HTTP 400. |
| | E2 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La plantilla queda actualizada con los nuevos valores y la `fecha_actualizacion` reflejada. | |
| | | |
| **Comentarios** | Se debe evaluar el impacto de modificar una plantilla que ya tiene reportes o programaciones activas asociadas. [Por definir] si se deben invalidar los cachés de reportes generados con la versión anterior. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-010 | |
| **Nombre** | Eliminar Plantilla de Reporte | |
| **Descripción** | Permite eliminar una plantilla de reporte del sistema. Si existen reportes o programaciones asociadas, la eliminación debe ser evaluada para evitar inconsistencias. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La plantilla con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la plantilla como parámetro de ruta. |
| | 5 | Verifica que la plantilla exista. |
| | 6 | Verifica que no existan programaciones activas o reportes pendientes/generando asociados a esta plantilla. |
| | 7 | Elimina la plantilla de la base de datos (o la marca como eliminada si se aplica borrado lógico). |
| | 8 | Retorna la respuesta (REP-RF-005) con mensaje de confirmación, código HTTP 200. |
| | 9 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la plantilla no existe, retorna HTTP 404. |
| | 6A | Si existen programaciones activas o reportes en proceso asociados, retorna HTTP 409 con detalle de los registros dependientes. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La plantilla ya no está disponible para la generación de nuevos reportes. | |
| | | |
| **Comentarios** | [Por definir] si la eliminación es física o lógica (cambio de estado a `eliminada`). Se recomienda borrado lógico para preservar la trazabilidad de reportes históricos. | |

---

### Entidad: Reporte

---

| | | |
|---|---|---|
| **Código** | REP-RF-011 | |
| **Nombre** | Solicitar Generación de Reporte | |
| **Descripción** | Permite a un usuario solicitar la generación de un reporte proporcionando una plantilla activa y los parámetros requeridos por dicha plantilla. Si existe un reporte en caché con los mismos parámetros, lo retorna directamente. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La plantilla referenciada existe y está en estado `activa`. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el cuerpo de la petición: `plantilla_id` (obligatorio), `parametros` (JSON con los parámetros requeridos por la plantilla), `formato_salida` (CSV o JSON, obligatorio) y `nombre` (nombre descriptivo, obligatorio). |
| | 5 | Valida que la plantilla exista y esté en estado `activa`. |
| | 6 | Valida que todos los parámetros requeridos por la plantilla estén presentes en la petición. |
| | 7 | Valida que el `formato_salida` sea `CSV` o `JSON` (regla RE-03). |
| | 8 | Verifica si existe un reporte completado en caché con la misma `plantilla_id` y `parámetros` (regla RE-02). |
| | 9a | Si existe caché, retorna el reporte almacenado directamente con código HTTP 200 (regla RE-02). Ir al paso 11. |
| | 9b | Si no existe caché, crea un registro de reporte con estado `pendiente`, `solicitado_por` del usuario autenticado y `fecha_solicitud` actual. |
| | 10 | Dispara de forma asíncrona el proceso de generación (REP-RF-012). Retorna al usuario el identificador del reporte creado con código HTTP 202. |
| | 11 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la plantilla no existe o está inactiva, retorna HTTP 404 o HTTP 422 respectivamente. |
| | 6A | Si algún parámetro requerido está ausente, retorna HTTP 400 con detalle. |
| | 7A | Si el formato no es válido, retorna HTTP 400. |
| | | |
| **Excepciones** | E1 | Si ocurre error al crear el registro en base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | Se ha creado un registro de reporte en estado `pendiente` (o se ha retornado el caché). El proceso de generación ha sido iniciado de forma asíncrona. | |
| | | |
| **Comentarios** | La lógica de comparación de caché debe normalizar los parámetros JSON para evitar falsos negativos por diferencias de orden de claves. [Por definir] el tiempo de vigencia del caché. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-012 | |
| **Nombre** | Generar Reporte Consolidado | |
| **Descripción** | Proceso interno (asíncrono) que ejecuta la generación del reporte: consulta los microservicios fuente definidos en la plantilla, consolida los datos, genera el resultado en el formato solicitado y lo almacena como caché. | |
| **Actores** | El propio microservicio (proceso interno); ms-calificaciones; ms-inventario; ms-presupuesto | |
| | | |
| **Precondición** | Existe un registro de reporte en estado `pendiente` (creado por REP-RF-011 o REP-RF-020). | |
| | La plantilla asociada está activa y tiene `configuracion_consultas` válida. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Cambia el estado del reporte a `generando`. |
| | 2 | Lee la `configuracion_consultas` y `microservicios_fuente` de la plantilla para determinar qué servicios consultar y con qué parámetros. |
| | 3 | Para cada microservicio fuente definido en la plantilla, realiza la consulta correspondiente usando el token de aplicación de ms-reportes (regla RT-03): |
| | | — Si la plantilla incluye **ms-calificaciones**: consulta rendimiento académico y promedios por programa según los parámetros del reporte. Respuesta esperada: datos de calificaciones y promedios. |
| | | — Si la plantilla incluye **ms-inventario**: consulta estado de activos, depreciación y stock bajo. Respuesta esperada: datos de inventario y activos. |
| | | — Si la plantilla incluye **ms-presupuesto**: consulta ejecución presupuestal por área y periodo. Respuesta esperada: datos de ejecución presupuestal. |
| | 4 | Consolida los datos obtenidos de todos los microservicios fuente según la lógica definida en `configuracion_consultas`. |
| | 5 | Genera el resultado en el formato solicitado (`CSV` o `JSON`). |
| | 6 | Almacena el resultado consolidado en `resultado_cache`, registra `fecha_generacion`, `tamano_bytes` y cambia el estado del reporte a `completado`. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 3A | Si algún microservicio fuente retorna error o no responde, registra el detalle del error y cambia el estado del reporte a `error`. No sigue procesando. |
| | | |
| **Excepciones** | E1 | Si falla la consolidación o la generación del formato, cambia el estado del reporte a `error` y registra la causa. |
| | E2 | Si falla el almacenamiento del resultado en base de datos, cambia el estado del reporte a `error`. |
| | | |
| **Postcondición** | El reporte está en estado `completado` con su resultado almacenado en caché, o en estado `error` con la causa registrada. | |
| | | |
| **Comentarios** | Las llamadas a microservicios fuente deben incluir el `request_id` de la petición original para mantener la trazabilidad distribuida (regla RT-05). [Por definir] timeout máximo para las consultas a microservicios fuente. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-013 | |
| **Nombre** | Consultar Estado de Reporte | |
| **Descripción** | Permite al usuario verificar el estado actual de un reporte (pendiente, generando, completado o error) y sus datos básicos a partir de su identificador. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | El reporte con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador del reporte como parámetro de ruta. |
| | 5 | Busca el reporte en la base de datos por su identificador. |
| | 6 | Retorna la respuesta (REP-RF-005) con los datos del reporte (excluyendo el `resultado_cache`) y código HTTP 200. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si el reporte no existe, retorna HTTP 404. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario conoce el estado actual del reporte solicitado. | |
| | | |
| **Comentarios** | El campo `resultado_cache` no debe incluirse en esta respuesta por su potencial tamaño. Para obtener el resultado, usar REP-RF-014. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-014 | |
| **Nombre** | Descargar Reporte Generado | |
| **Descripción** | Permite al usuario descargar el resultado de un reporte que ha completado su generación, en el formato de salida configurado (CSV o JSON). | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | El reporte con el identificador proporcionado existe y está en estado `completado` (regla RE-04). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador del reporte como parámetro de ruta. |
| | 5 | Busca el reporte en la base de datos y verifica que su estado sea `completado`. |
| | 6 | Recupera el `resultado_cache` del reporte. |
| | 7 | Retorna el contenido como descarga con el `Content-Type` y `Content-Disposition` apropiados según el `formato_salida` (`text/csv` o `application/json`). |
| | 8 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si el reporte no existe, retorna HTTP 404. |
| | 5B | Si el reporte existe pero no está en estado `completado`, retorna HTTP 422 indicando que el reporte no está disponible para descarga (regla RE-04). |
| | | |
| **Excepciones** | E1 | Si el `resultado_cache` está vacío o corrupto, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario ha descargado el contenido del reporte en el formato solicitado. | |
| | | |
| **Comentarios** | Solo se admiten los formatos `CSV` y `JSON` (regla RE-03). El encabezado `Content-Disposition` debe incluir un nombre de archivo sugerido basado en el nombre del reporte. | |

---

### Entidad: Programación

---

| | | |
|---|---|---|
| **Código** | REP-RF-015 | |
| **Nombre** | Crear Programación de Reporte | |
| **Descripción** | Permite configurar la generación automática de un reporte definiendo la plantilla, la periodicidad, la hora de ejecución y los destinatarios que recibirán el resultado. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La plantilla referenciada existe y está en estado `activa`. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe y valida el cuerpo de la petición: `plantilla_id` (obligatorio), `periodicidad` (diario/semanal/mensual, obligatorio), `dia_ejecucion` (obligatorio para semanal y mensual), `hora_ejecucion` (obligatorio), `destinatarios` (lista, obligatorio) y `estado` (valor por defecto: `activa`). |
| | 5 | Valida que la `periodicidad` sea uno de los valores permitidos: `diario`, `semanal` o `mensual` (regla RE-05). |
| | 6 | Valida que la plantilla referenciada exista y esté activa. |
| | 7 | Calcula la `proxima_ejecucion` en base a la `periodicidad`, `dia_ejecucion` y `hora_ejecucion` configurados. |
| | 8 | Persiste la programación con `fecha_creacion` y `fecha_actualizacion` actuales y `ultima_ejecucion` nula. |
| | 9 | Retorna la respuesta (REP-RF-005) con los datos de la programación creada, código HTTP 201. |
| | 10 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la `periodicidad` no es válida, retorna HTTP 400. |
| | 6A | Si la plantilla no existe o está inactiva, retorna HTTP 404 o HTTP 422. |
| | | |
| **Excepciones** | E1 | Si algún campo obligatorio falta o tiene formato inválido, retorna HTTP 400. |
| | E2 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La programación queda registrada y el scheduler del sistema la considerará para ejecuciones automáticas futuras. | |
| | | |
| **Comentarios** | [Por definir] el mecanismo de notificación a los destinatarios (¿integración con ms-notificaciones?). [Por definir] la estructura de `destinatarios` (IDs de usuario, roles o correos electrónicos). | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-016 | |
| **Nombre** | Listar Programaciones de Reporte | |
| **Descripción** | Permite obtener el listado de programaciones de generación de reportes registradas, con opción de filtrar por estado o plantilla. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe parámetros de consulta opcionales: `estado` (activa/pausada), `plantilla_id`, paginación. |
| | 5 | Consulta la base de datos aplicando los filtros recibidos. |
| | 6 | Retorna la respuesta (REP-RF-005) con la lista de programaciones, código HTTP 200. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 6A | Si no existen programaciones con los filtros, retorna lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario recibe el listado de programaciones que cumplen los criterios. | |
| | | |
| **Comentarios** | Los datos de la lista deben incluir `proxima_ejecucion` y `ultima_ejecucion` para facilitar el monitoreo. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-017 | |
| **Nombre** | Actualizar Programación de Reporte | |
| **Descripción** | Permite modificar la configuración de una programación existente: periodicidad, hora, día de ejecución o destinatarios. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La programación con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la programación (ruta) y los campos a modificar. |
| | 5 | Verifica que la programación exista. |
| | 6 | Valida los nuevos valores: si se modifica la `periodicidad`, debe ser un valor permitido (regla RE-05). |
| | 7 | Actualiza los campos y recalcula `proxima_ejecucion` si se modificó la periodicidad, día u hora. |
| | 8 | Registra `fecha_actualizacion` con la fecha/hora actual. |
| | 9 | Retorna la respuesta (REP-RF-005) con los datos actualizados, código HTTP 200. |
| | 10 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la programación no existe, retorna HTTP 404. |
| | 6A | Si algún valor es inválido, retorna HTTP 400 con detalle. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La programación queda actualizada y se reflejan los nuevos valores en las próximas ejecuciones. | |
| | | |
| **Comentarios** | [Por definir] si se permite cambiar la `plantilla_id` asociada o si eso requiere crear una nueva programación. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-018 | |
| **Nombre** | Desactivar Programación de Reporte | |
| **Descripción** | Permite pausar una programación activa, evitando que sus reportes se generen automáticamente hasta que sea reactivada. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La programación con el identificador proporcionado existe y está en estado `activa`. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la programación como parámetro de ruta. |
| | 5 | Verifica que la programación exista y esté en estado `activa`. |
| | 6 | Cambia el estado de la programación a `pausada` y registra `fecha_actualizacion`. |
| | 7 | Retorna la respuesta (REP-RF-005) con confirmación, código HTTP 200. |
| | 8 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la programación no existe, retorna HTTP 404. |
| | 5B | Si la programación ya está en estado `pausada`, retorna HTTP 422 con mensaje informativo. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La programación queda en estado `pausada` y no se ejecutará automáticamente hasta ser reactivada. | |
| | | |
| **Comentarios** | Las programaciones pausadas no se ejecutan automáticamente (regla RE-06), pero sí pueden ejecutarse manualmente mediante REP-RF-020. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-019 | |
| **Nombre** | Ejecutar Automáticamente Reportes Programados | |
| **Descripción** | Proceso interno ejecutado por el scheduler del sistema en la fecha y hora configuradas, que genera automáticamente los reportes de las programaciones activas cuya `proxima_ejecucion` ha llegado. | |
| **Actores** | Scheduler interno del microservicio | |
| | | |
| **Precondición** | Existe al menos una programación en estado `activa` cuya `proxima_ejecucion` es igual o anterior a la fecha/hora actual (regla RE-06). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El scheduler evalúa periódicamente las programaciones activas con `proxima_ejecucion` <= fecha/hora actual. |
| | 2 | Para cada programación elegible, crea un registro de reporte en estado `pendiente` asociado a la plantilla configurada y con los parámetros definidos en la programación. |
| | 3 | Dispara el proceso de generación REP-RF-012 para cada reporte creado. |
| | 4 | Actualiza `ultima_ejecucion` con la fecha/hora actual. |
| | 5 | Calcula y actualiza `proxima_ejecucion` en base a la `periodicidad` configurada. |
| | 6 | Ejecutar REP-RF-004 por cada ejecución. |
| | | |
| **Secuencia alterna** | 3A | Si la generación del reporte falla (REP-RF-012 termina en estado `error`), registra el fallo pero actualiza igualmente `ultima_ejecucion` y `proxima_ejecucion` para no bloquear futuras ejecuciones. |
| | | |
| **Excepciones** | E1 | Si el scheduler falla al evaluar las programaciones, registra el error en log local y reintenta en el siguiente ciclo. |
| | | |
| **Postcondición** | Los reportes programados elegibles han sido generados (o han fallado con su error registrado) y las programaciones tienen actualizados sus campos `ultima_ejecucion` y `proxima_ejecucion`. | |
| | | |
| **Comentarios** | [Por definir] la frecuencia de evaluación del scheduler (ej: cada minuto, cada 5 minutos). [Por definir] si los destinatarios son notificados mediante ms-notificaciones al completarse la generación. | |

---

| | | |
|---|---|---|
| **Código** | REP-RF-020 | |
| **Nombre** | Ejecutar Manualmente Reporte Programado | |
| **Descripción** | Permite forzar la ejecución inmediata de un reporte programado, independientemente de su `proxima_ejecucion` y sin importar si la programación está activa o pausada (regla RE-07). | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La programación con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la programación como parámetro de ruta. |
| | 5 | Verifica que la programación exista. |
| | 6 | Crea un registro de reporte en estado `pendiente` con la plantilla y parámetros definidos en la programación. |
| | 7 | Dispara el proceso de generación REP-RF-012 de forma asíncrona. |
| | 8 | Actualiza `ultima_ejecucion` con la fecha/hora actual. La `proxima_ejecucion` no se modifica (la ejecución manual no altera el calendario automático). |
| | 9 | Retorna la respuesta (REP-RF-005) con el identificador del reporte creado, código HTTP 202. |
| | 10 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la programación no existe, retorna HTTP 404. |
| | | |
| **Excepciones** | E1 | Si ocurre error al crear el registro de reporte, retorna HTTP 500. |
| | | |
| **Postcondición** | Se ha creado un nuevo reporte en estado `pendiente` y su generación ha sido iniciada. La `proxima_ejecucion` de la programación no ha sido modificada. | |
| | | |
| **Comentarios** | La ejecución manual aplica tanto a programaciones activas como pausadas (regla RE-07). No reemplaza ni reinicia el ciclo automático. | |

---

## Categoría 3: Requisitos Sugeridos

---

> **Justificación REP-RF-021:** El documento especifica la capacidad de solicitar y descargar reportes individuales, pero no define explícitamente un endpoint para listar todos los reportes generados. Esta funcionalidad es esencial para que los usuarios administradores puedan monitorear el historial de reportes solicitados, verificar estados y acceder a generaciones anteriores sin conocer el ID exacto.

| | | |
|---|---|---|
| **Código** | REP-RF-021 | |
| **Nombre** | Listar Reportes Generados | |
| **Descripción** | Permite obtener el historial de reportes generados en el sistema, con opción de filtrar por estado, plantilla, usuario solicitante o rango de fechas. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe parámetros de consulta opcionales: `estado`, `plantilla_id`, `solicitado_por`, `fecha_desde`, `fecha_hasta`, paginación. |
| | 5 | Consulta la base de datos aplicando los filtros. |
| | 6 | Retorna la respuesta (REP-RF-005) con el listado de reportes (sin incluir `resultado_cache`) y metadatos de paginación, código HTTP 200. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 6A | Si no existen reportes con los filtros aplicados, retorna lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario recibe el historial de reportes que cumplen los criterios. | |
| | | |
| **Comentarios** | El campo `resultado_cache` debe excluirse del listado para evitar respuestas de gran tamaño. Para obtener el contenido del reporte, usar REP-RF-014. | |

---

> **Justificación REP-RF-022:** El documento establece el uso de caché para evitar regenerar reportes con los mismos parámetros, pero no define un mecanismo explícito para invalidar esa caché cuando los datos subyacentes han cambiado o la plantilla ha sido modificada. Esta funcionalidad es necesaria para garantizar la vigencia de los datos reportados.

| | | |
|---|---|---|
| **Código** | REP-RF-022 | |
| **Nombre** | Invalidar Caché de Reporte | |
| **Descripción** | Permite forzar la invalidación del resultado en caché de un reporte completado, de modo que la próxima solicitud con los mismos parámetros genere un nuevo resultado actualizado. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | El reporte con el identificador proporcionado existe y está en estado `completado`. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador del reporte como parámetro de ruta. |
| | 5 | Verifica que el reporte exista y esté en estado `completado`. |
| | 6 | Limpia el campo `resultado_cache` del reporte y cambia su estado a `pendiente`. |
| | 7 | Retorna la respuesta (REP-RF-005) con confirmación, código HTTP 200. |
| | 8 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si el reporte no existe, retorna HTTP 404. |
| | 5B | Si el reporte no está en estado `completado`, retorna HTTP 422. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El caché del reporte ha sido eliminado. La próxima solicitud con los mismos parámetros disparará una nueva generación. | |
| | | |
| **Comentarios** | [Por definir] si se debe ofrecer también una invalidación masiva de caché por plantilla. | |

---

> **Justificación REP-RF-023:** El documento define la operación de desactivar programaciones (REP-RF-018) y menciona el estado `activa` vs `pausada`, pero no contempla explícitamente la operación inversa: reactivar una programación pausada. Esta operación es necesaria para completar el ciclo de vida de gestión de programaciones sin necesidad de eliminar y recrear la programación.

| | | |
|---|---|---|
| **Código** | REP-RF-023 | |
| **Nombre** | Reactivar Programación Pausada | |
| **Descripción** | Permite volver a activar una programación que se encuentra en estado `pausada`, reanudando su ciclo de ejecución automática. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La programación con el identificador proporcionado existe y está en estado `pausada`. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la programación como parámetro de ruta. |
| | 5 | Verifica que la programación exista y esté en estado `pausada`. |
| | 6 | Cambia el estado a `activa` y recalcula `proxima_ejecucion` en base a la `periodicidad`, `dia_ejecucion` y `hora_ejecucion` configurados. |
| | 7 | Registra `fecha_actualizacion` con la fecha/hora actual. |
| | 8 | Retorna la respuesta (REP-RF-005) con los datos actualizados, código HTTP 200. |
| | 9 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la programación no existe, retorna HTTP 404. |
| | 5B | Si la programación ya está en estado `activa`, retorna HTTP 422 con mensaje informativo. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | La programación está en estado `activa` con `proxima_ejecucion` recalculada y será considerada en las próximas evaluaciones del scheduler. | |
| | | |
| **Comentarios** | Al reactivar, la `proxima_ejecucion` debe calcularse desde la fecha/hora actual, no desde la fecha en que fue pausada, para evitar ejecuciones acumuladas. | |

---

> **Justificación REP-RF-024:** El documento define la operación de listar programaciones (REP-RF-016) pero no contempla una operación de consulta individual con el detalle completo de una programación. Esta operación es necesaria para facilitar la edición informada (pre-carga de formularios) y la auditoría específica de una programación.

| | | |
|---|---|---|
| **Código** | REP-RF-024 | |
| **Nombre** | Consultar Detalle de Programación | |
| **Descripción** | Permite obtener el detalle completo de una programación de reporte específica a partir de su identificador. | |
| **Actores** | Usuario administrador | |
| | | |
| **Precondición** | El usuario tiene una sesión activa. | |
| | La programación con el identificador proporcionado existe en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar REP-RF-003. |
| | 2 | Ejecutar REP-RF-001. |
| | 3 | Ejecutar REP-RF-002. |
| | 4 | Recibe el identificador de la programación como parámetro de ruta. |
| | 5 | Busca la programación en la base de datos por su identificador. |
| | 6 | Retorna la respuesta (REP-RF-005) con todos los campos de la programación, incluyendo `ultima_ejecucion`, `proxima_ejecucion` y datos de la plantilla asociada, código HTTP 200. |
| | 7 | Ejecutar REP-RF-004. |
| | | |
| **Secuencia alterna** | 5A | Si la programación no existe, retorna HTTP 404. |
| | | |
| **Excepciones** | E1 | Si ocurre error de base de datos, retorna HTTP 500. |
| | | |
| **Postcondición** | El usuario recibe el detalle completo de la programación. | |
| | | |
| **Comentarios** | La respuesta debe incluir el resumen de la plantilla asociada (nombre, estado) para evitar que el cliente necesite una segunda llamada. | |

---

*Fin del documento de requisitos funcionales — ms-reportes [REP]*
