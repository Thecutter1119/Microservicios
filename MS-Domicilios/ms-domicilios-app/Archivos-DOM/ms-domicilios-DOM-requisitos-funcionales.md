# Requisitos Funcionales — ms-domicilios [DOM]

| Campo | Detalle |
|---|---|
| **Microservicio** | ms-domicilios |
| **Código** | DOM |
| **Módulo** | Módulo 4 — Logística y Proveedores |
| **Versión del documento** | 1.0 |
| **Fecha** | Febrero 2026 |

---

## Tabla de Contenido

### Categoría 1 — Requisitos Transversales
- [DOM-RF-001](#dom-rf-001) — Validación de Sesión Activa
- [DOM-RF-002](#dom-rf-002) — Validación de Permisos por Funcionalidad
- [DOM-RF-003](#dom-rf-003) — Generación y Propagación de Request ID
- [DOM-RF-004](#dom-rf-004) — Registro de Auditoría Asíncrono
- [DOM-RF-005](#dom-rf-005) — Estructura de Respuesta Estándar

### Categoría 2 — Requisitos Funcionales por Entidad

#### Entidad: Repartidores
- [DOM-RF-006](#dom-rf-006) — Crear Repartidor
- [DOM-RF-007](#dom-rf-007) — Consultar Repartidor por ID
- [DOM-RF-008](#dom-rf-008) — Actualizar Repartidor
- [DOM-RF-009](#dom-rf-009) — Listar Repartidores Disponibles por Zona de Cobertura

#### Entidad: Entregas
- [DOM-RF-010](#dom-rf-010) — Crear Entrega
- [DOM-RF-011](#dom-rf-011) — Consultar Entrega por ID
- [DOM-RF-012](#dom-rf-012) — Actualizar Datos de Entrega
- [DOM-RF-013](#dom-rf-013) — Asignar Repartidor a Entrega
- [DOM-RF-014](#dom-rf-014) — Actualizar Estado de Entrega

#### Entidad: Seguimiento
- [DOM-RF-015](#dom-rf-015) — Registrar Punto de Seguimiento Manual
- [DOM-RF-016](#dom-rf-016) — Consultar Historial de Seguimiento de una Entrega

#### Entidad: Calificaciones
- [DOM-RF-017](#dom-rf-017) — Registrar Calificación de Entrega

### Categoría 3 — Requisitos Sugeridos
- [DOM-RF-018](#dom-rf-018) — Listar Entregas con Filtros
- [DOM-RF-019](#dom-rf-019) — Calcular Costo de Envío
- [DOM-RF-020](#dom-rf-020) — Consultar Calificaciones de un Repartidor
- [DOM-RF-021](#dom-rf-021) — Cambiar Estado de Repartidor

---

## Categoría 1 — Requisitos Transversales

---

<a id="dom-rf-001"></a>
### DOM-RF-001 — Validación de Sesión Activa

| | | |
|---|---|---|
| **Código** | DOM-RF-001 | |
| **Nombre** | Validación de Sesión Activa | |
| **Descripción** | Antes de ejecutar cualquier lógica de negocio, el microservicio debe verificar que el usuario posee una sesión válida consultando a ms-autenticacion. Si la sesión es inválida, la petición se rechaza inmediatamente. | |
| **Actores** | Cualquier usuario o sistema que realice una petición a ms-domicilios; ms-autenticacion [AUTH] | |
| | | |
| **Precondición** | La petición entrante incluye las credenciales o token de sesión del usuario en las cabeceras. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | El microservicio recibe la petición del usuario. |
| | 2 | Extrae el token de sesión de las cabeceras de la petición. |
| | 3 | Invoca a **ms-autenticacion [AUTH]** — operación: validar sesión — enviando el token cifrado con AES-256. Se espera como respuesta: confirmación de sesión válida e identidad del usuario (ID de usuario y rol). |
| | 4 | ms-autenticacion responde confirmando que la sesión es activa y válida. |
| | 5 | El flujo continúa hacia DOM-RF-002. |
| | | |
| **Secuencia alterna** | 4A | ms-autenticacion responde que la sesión no existe o ha expirado → el microservicio retorna HTTP 401 con estructura estándar (DOM-RF-005) indicando sesión inválida. No se ejecuta ninguna lógica de negocio. |
| | | |
| **Excepciones** | E1 | ms-autenticacion no responde o devuelve error de comunicación → retornar HTTP 503 con mensaje descriptivo. |
| | | |
| **Postcondición** | El microservicio dispone del ID de usuario y su rol para continuar con la validación de permisos. | |
| | | |
| **Comentarios** | Este requisito es referenciado por todos los demás requisitos funcionales mediante la instrucción "Ejecutar DOM-RF-001". | |

---

<a id="dom-rf-002"></a>
### DOM-RF-002 — Validación de Permisos por Funcionalidad

| | | |
|---|---|---|
| **Código** | DOM-RF-002 | |
| **Nombre** | Validación de Permisos por Funcionalidad | |
| **Descripción** | Tras validar la sesión, el microservicio debe consultar a ms-roles para verificar que el rol del usuario tiene autorización para ejecutar la funcionalidad solicitada. Si no tiene el permiso, la petición se rechaza. | |
| **Actores** | Usuario autenticado; ms-roles [ROL] | |
| | | |
| **Precondición** | DOM-RF-001 ejecutado exitosamente. Se dispone del ID de usuario y rol. | |
| | La funcionalidad solicitada tiene un código de permiso único definido en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Determinar el código de permiso correspondiente a la funcionalidad solicitada. |
| | 2 | Invocar a **ms-roles [ROL]** — operación: verificar permiso — enviando el rol del usuario y el código de permiso requerido, con token de aplicación de DOM cifrado. Se espera como respuesta: autorizado / no autorizado. |
| | 3 | ms-roles responde confirmando que el rol tiene el permiso. |
| | 4 | El flujo continúa hacia la lógica de negocio de la funcionalidad solicitada. |
| | | |
| **Secuencia alterna** | 3A | ms-roles responde que el rol no tiene el permiso → retornar HTTP 403 con estructura estándar (DOM-RF-005) indicando acceso denegado. |
| | | |
| **Excepciones** | E1 | ms-roles no responde o devuelve error → retornar HTTP 503. |
| | | |
| **Postcondición** | El usuario está autorizado para ejecutar la funcionalidad. La lógica de negocio puede continuar. | |
| | | |
| **Comentarios** | Los códigos de permiso específicos por funcionalidad son [Por definir] junto con el equipo de ms-roles. | |

---

<a id="dom-rf-003"></a>
### DOM-RF-003 — Generación y Propagación de Request ID

| | | |
|---|---|---|
| **Código** | DOM-RF-003 | |
| **Nombre** | Generación y Propagación de Request ID | |
| **Descripción** | Cada petición que ingresa a ms-domicilios debe recibir un identificador único de rastreo. Si la petición ya trae un Request ID (originado en otro microservicio), debe reutilizarse. El Request ID se incluye en cabeceras y cuerpo de toda respuesta. | |
| **Actores** | ms-domicilios (proceso interno) | |
| | | |
| **Precondición** | El microservicio ha recibido una petición entrante. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Inspeccionar las cabeceras de la petición entrante en busca de un Request ID preexistente. |
| | 2 | Si no existe Request ID, generar uno con el formato: `DOM-{timestamp Unix}-{id corto aleatorio}` (ej: `DOM-1740000000-a3f8b2`). |
| | 3 | Almacenar el Request ID en el contexto de la petición actual. |
| | 4 | Propagar el Request ID en todas las llamadas salientes hacia otros microservicios durante el procesamiento de esta petición. |
| | 5 | Incluir el Request ID tanto en las cabeceras como en el cuerpo de la respuesta (DOM-RF-005). |
| | | |
| **Secuencia alterna** | 2A | Ya existe un Request ID en la petición → reutilizarlo sin generar uno nuevo. |
| | | |
| **Excepciones** | E1 | Error al generar el ID aleatorio → [Por definir] política de reintento o ID de fallback. |
| | | |
| **Postcondición** | El Request ID está disponible en el contexto para ser usado en logs, respuestas y llamadas externas. | |
| | | |
| **Comentarios** | Este requisito es referenciado por todos los demás requisitos mediante "Ejecutar DOM-RF-003". | |

---

<a id="dom-rf-004"></a>
### DOM-RF-004 — Registro de Auditoría Asíncrono

| | | |
|---|---|---|
| **Código** | DOM-RF-004 | |
| **Nombre** | Registro de Auditoría Asíncrono | |
| **Descripción** | Tras ejecutar cualquier operación, ms-domicilios debe enviar un registro de log en formato JSON a ms-auditoria de forma asíncrona (fire-and-forget). El fallo en el envío no interrumpe la operación principal. | |
| **Actores** | ms-domicilios (proceso interno); ms-auditoria [AUD] | |
| | | |
| **Precondición** | La operación principal ha concluido (exitosa o con error de negocio). | |
| | El Request ID de la petición está disponible en el contexto. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Construir el objeto de log en formato JSON con los campos: fecha/hora, Request ID, nombre del microservicio (`ms-domicilios`), funcionalidad ejecutada, método HTTP, código de respuesta, duración en ms, ID del usuario y detalle descriptivo. |
| | 2 | Enviar el objeto de log de forma asíncrona a **ms-auditoria [AUD]** — operación: registrar log — usando el token de aplicación de DOM. |
| | 3 | No esperar confirmación; la respuesta al usuario ya ha sido (o será) enviada independientemente. |
| | | |
| **Secuencia alterna** | — | No aplica (fire-and-forget). |
| | | |
| **Excepciones** | E1 | ms-auditoria no responde o devuelve error → registrar el fallo localmente (log interno) y continuar. El servicio DOM sigue operando con normalidad. |
| | | |
| **Postcondición** | El log ha sido enviado a ms-auditoria. En caso de fallo, el incidente queda registrado localmente. | |
| | | |
| **Comentarios** | El mecanismo de cola o broker para el envío asíncrono es [Por definir] (puede ser una cola en memoria, Celery, etc.). | |

---

<a id="dom-rf-005"></a>
### DOM-RF-005 — Estructura de Respuesta Estándar

| | | |
|---|---|---|
| **Código** | DOM-RF-005 | |
| **Nombre** | Estructura de Respuesta Estándar | |
| **Descripción** | Todas las respuestas emitidas por ms-domicilios, tanto exitosas como de error, deben seguir una estructura JSON uniforme que incluya los campos definidos por la regla transversal §6.7. | |
| **Actores** | ms-domicilios (proceso interno) | |
| | | |
| **Precondición** | El microservicio ha terminado de procesar una petición (con éxito o con error). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Construir el objeto de respuesta JSON con los siguientes campos obligatorios: `request_id` (DOM-RF-003), `success` (booleano), `data` (resultado de la operación o `null`), `message` (descripción del resultado) y `timestamp` (fecha/hora de la respuesta). |
| | 2 | Incluir el `request_id` también en las cabeceras HTTP de la respuesta. |
| | 3 | Retornar la respuesta con el código HTTP correspondiente a la operación. |
| | | |
| **Secuencia alterna** | — | No aplica. La estructura es la misma para respuestas exitosas y de error; solo varía el campo `success` y el contenido de `data`/`message`. |
| | | |
| **Excepciones** | E1 | Error interno al construir la respuesta → retornar HTTP 500 con estructura mínima que incluya al menos `request_id` y `message`. |
| | | |
| **Postcondición** | El cliente recibe una respuesta estructurada de forma predecible. | |
| | | |
| **Comentarios** | Los códigos HTTP utilizados por cada operación específica se documentan en cada requisito individual. | |

---

## Categoría 2 — Requisitos Funcionales por Entidad

---

## Entidad: Repartidores

---

<a id="dom-rf-006"></a>
### DOM-RF-006 — Crear Repartidor

| | | |
|---|---|---|
| **Código** | DOM-RF-006 | |
| **Nombre** | Crear Repartidor | |
| **Descripción** | Permite registrar un nuevo repartidor en el sistema, asociándolo a un usuario existente y definiendo su información de vehículo, zona de cobertura y estado inicial. | |
| **Actores** | Administrador logístico (rol con permiso de creación de repartidores) | |
| | | |
| **Precondición** | El usuario que realiza la operación tiene sesión activa y permiso para crear repartidores. | |
| | El usuario del sistema que se asociará al repartidor existe en ms-autenticacion. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos — código de permiso: [Por definir]). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Recibir y validar el payload: `usuario` (ID), `nombre`, `telefono`, `tipo_vehiculo`, `placa_vehiculo`, `zona_cobertura`. Todos los campos son obligatorios. |
| | 5 | Verificar que no exista otro repartidor activo con la misma `placa_vehiculo`. |
| | 6 | Asignar estado inicial `disponible` y `calificacion_promedio = null`. |
| | 7 | Persistir el nuevo registro de repartidor en la base de datos con `fecha_registro` y `fecha_actualizacion` = ahora. |
| | 8 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 9 | Retornar HTTP 201 con el repartidor creado en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | Ya existe un repartidor con la misma placa → retornar HTTP 409 indicando conflicto de placa duplicada. |
| | | |
| **Excepciones** | E1 | Error de base de datos al persistir → retornar HTTP 500. |
| | E2 | Payload incompleto o con tipos inválidos → retornar HTTP 400 con detalle de los campos fallidos. |
| | | |
| **Postcondición** | El repartidor queda registrado en estado `disponible` y disponible para ser asignado a entregas. | |
| | | |
| **Comentarios** | [Por definir] si se requiere validar que el ID de `usuario` exista en ms-autenticacion en el momento de la creación. | |

---

<a id="dom-rf-007"></a>
### DOM-RF-007 — Consultar Repartidor por ID

| | | |
|---|---|---|
| **Código** | DOM-RF-007 | |
| **Nombre** | Consultar Repartidor por ID | |
| **Descripción** | Permite obtener la información completa de un repartidor específico a partir de su identificador único. | |
| **Actores** | Usuario autenticado con permiso de consulta de repartidores | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permiso de consulta. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID del repartidor del path de la petición. |
| | 5 | Buscar el repartidor en la base de datos por su ID. |
| | 6 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 7 | Retornar HTTP 200 con los datos del repartidor en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | El repartidor no existe → retornar HTTP 404. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El solicitante recibe la información actualizada del repartidor. | |
| | | |
| **Comentarios** | — | |

---

<a id="dom-rf-008"></a>
### DOM-RF-008 — Actualizar Repartidor

| | | |
|---|---|---|
| **Código** | DOM-RF-008 | |
| **Nombre** | Actualizar Repartidor | |
| **Descripción** | Permite modificar los datos de un repartidor existente, tales como teléfono, tipo de vehículo, placa y zona de cobertura. | |
| **Actores** | Administrador logístico con permiso de actualización de repartidores | |
| | | |
| **Precondición** | El repartidor identificado existe en el sistema. | |
| | El usuario tiene sesión activa y permiso de actualización. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID del repartidor y el payload con los campos a actualizar. |
| | 5 | Verificar que el repartidor existe. |
| | 6 | Si se modifica `placa_vehiculo`, verificar que no esté en uso por otro repartidor. |
| | 7 | Actualizar los campos indicados y registrar `fecha_actualizacion` = ahora. |
| | 8 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 9 | Retornar HTTP 200 con los datos actualizados en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | El repartidor no existe → retornar HTTP 404. |
| | 6A | La nueva placa ya está registrada en otro repartidor → retornar HTTP 409. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | Los datos del repartidor quedan actualizados y `fecha_actualizacion` refleja el momento del cambio. | |
| | | |
| **Comentarios** | El estado del repartidor (`disponible`, `en ruta`, `inactivo`) se gestiona mediante DOM-RF-021 (requisito sugerido). | |

---

<a id="dom-rf-009"></a>
### DOM-RF-009 — Listar Repartidores Disponibles por Zona de Cobertura

| | | |
|---|---|---|
| **Código** | DOM-RF-009 | |
| **Nombre** | Listar Repartidores Disponibles por Zona de Cobertura | |
| **Descripción** | Retorna la lista de repartidores cuyo estado es `disponible` y cuya zona de cobertura coincide con el criterio de búsqueda proporcionado. | |
| **Actores** | Usuario autenticado con permiso de consulta de repartidores; proceso interno de asignación (DOM-RF-013) | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permiso de consulta. | |
| | Se proporciona al menos un criterio de filtro de zona de cobertura. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el parámetro `zona_cobertura` de la petición (query param). |
| | 5 | Consultar la base de datos: repartidores con `estado = 'disponible'` y `zona_cobertura` coincidente. |
| | 6 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 7 | Retornar HTTP 200 con la lista de repartidores en estructura **DOM-RF-005** (lista puede estar vacía). |
| | | |
| **Secuencia alterna** | 5A | No se encuentran repartidores con los criterios dados → retornar HTTP 200 con lista vacía. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El solicitante recibe únicamente repartidores en estado disponible para la zona solicitada. | |
| | | |
| **Comentarios** | El tipo de dato y formato de `zona_cobertura` es [Por definir] (texto libre, código geográfico, polígono, etc.). | |

---

## Entidad: Entregas

---

<a id="dom-rf-010"></a>
### DOM-RF-010 — Crear Entrega

| | | |
|---|---|---|
| **Código** | DOM-RF-010 | |
| **Nombre** | Crear Entrega | |
| **Descripción** | Permite crear una nueva entrega a partir de un pedido existente, definiendo las direcciones de origen y destino. El costo de envío se calcula automáticamente y la entrega queda en estado inicial pendiente de asignación de repartidor. | |
| **Actores** | Operador logístico con permiso de creación de entregas | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permiso de creación de entregas. | |
| | El ID del pedido que origina la entrega es proporcionado. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Recibir y validar el payload: `pedido` (ID), `direccion_origen`, `direccion_destino`. |
| | 5 | Invocar a **ms-pedidos [PED]** — operación: obtener pedido por ID — enviando el `pedido_id` y el token de aplicación de DOM. Se espera como respuesta: datos del pedido (solicitante, ítems, proveedor, estado). |
| | 6 | Verificar que el pedido existe y que su estado es compatible con crear una entrega ([Por definir] los estados válidos de pedido para este fin). |
| | 7 | Verificar que no exista ya una entrega activa para el mismo pedido. |
| | 8 | Calcular el costo de envío ejecutando **DOM-RF-019**. |
| | 9 | Persistir la entrega con estado inicial `asignada` (pendiente de repartidor), `repartidor_asignado = null`, `fecha_asignacion = null`, `costo_envio` calculado, `fecha_creacion` = ahora. |
| | 10 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 11 | Retornar HTTP 201 con la entrega creada en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | ms-pedidos no encuentra el pedido → retornar HTTP 404 indicando pedido no encontrado. |
| | 6A | El estado del pedido no es compatible → retornar HTTP 422 con mensaje descriptivo. |
| | 7A | Ya existe una entrega activa para el pedido → retornar HTTP 409. |
| | | |
| **Excepciones** | E1 | ms-pedidos no responde → retornar HTTP 503. |
| | E2 | Error de base de datos al persistir → retornar HTTP 500. |
| | | |
| **Postcondición** | La entrega queda registrada y lista para que se le asigne un repartidor (DOM-RF-013). | |
| | | |
| **Comentarios** | [Por definir] si la creación de la entrega debe dispararse automáticamente desde ms-pedidos o siempre de forma manual. | |

---

<a id="dom-rf-011"></a>
### DOM-RF-011 — Consultar Entrega por ID

| | | |
|---|---|---|
| **Código** | DOM-RF-011 | |
| **Nombre** | Consultar Entrega por ID | |
| **Descripción** | Permite obtener la información completa de una entrega específica a partir de su identificador único. | |
| **Actores** | Usuario autenticado con permiso de consulta de entregas | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permiso de consulta. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega del path de la petición. |
| | 5 | Buscar la entrega en la base de datos por su ID. |
| | 6 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 7 | Retornar HTTP 200 con los datos de la entrega en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El solicitante recibe la información actualizada de la entrega. | |
| | | |
| **Comentarios** | — | |

---

<a id="dom-rf-012"></a>
### DOM-RF-012 — Actualizar Datos de Entrega

| | | |
|---|---|---|
| **Código** | DOM-RF-012 | |
| **Nombre** | Actualizar Datos de Entrega | |
| **Descripción** | Permite modificar campos editables de una entrega existente, como las observaciones o las fechas de recogida/entrega. No incluye el cambio de estado (DOM-RF-014) ni la asignación de repartidor (DOM-RF-013). | |
| **Actores** | Operador logístico con permiso de actualización de entregas | |
| | | |
| **Precondición** | La entrega existe en el sistema. | |
| | El usuario tiene sesión activa y permiso de actualización. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega y el payload con los campos a actualizar. |
| | 5 | Verificar que la entrega existe. |
| | 6 | Validar que los campos a modificar son editables en el estado actual de la entrega. |
| | 7 | Aplicar los cambios y actualizar `fecha_actualizacion` = ahora. |
| | 8 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 9 | Retornar HTTP 200 con los datos actualizados en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | 6A | Se intenta modificar un campo no editable en el estado actual → retornar HTTP 422. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | Los datos editables de la entrega quedan actualizados. | |
| | | |
| **Comentarios** | [Por definir] la lista exacta de campos editables según el estado de la entrega. | |

---

<a id="dom-rf-013"></a>
### DOM-RF-013 — Asignar Repartidor a Entrega

| | | |
|---|---|---|
| **Código** | DOM-RF-013 | |
| **Nombre** | Asignar Repartidor a Entrega | |
| **Descripción** | Permite asignar un repartidor a una entrega, validando que el repartidor esté disponible y que su zona de cobertura coincida con la dirección de destino de la entrega. Al asignar, el estado del repartidor cambia a `en ruta` y se registra la fecha de asignación. | |
| **Actores** | Operador logístico con permiso de asignación de repartidores | |
| | | |
| **Precondición** | La entrega existe y no tiene repartidor asignado (o el permiso permite reasignación). | |
| | El usuario tiene sesión activa y permiso de asignación. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega y el ID del repartidor del payload. |
| | 5 | Verificar que la entrega existe y está en un estado que permite asignación (`asignada`). |
| | 6 | Verificar que el repartidor existe y su estado es `disponible` (Regla 7). |
| | 7 | Verificar que la `zona_cobertura` del repartidor corresponde con la `direccion_destino` de la entrega (Regla 8). |
| | 8 | Actualizar la entrega: `repartidor_asignado` = ID del repartidor, `fecha_asignacion` = ahora, `fecha_actualizacion` = ahora. |
| | 9 | Actualizar el estado del repartidor a `en ruta`. |
| | 10 | Invocar a **ms-notificaciones [NOT]** — operación: enviar notificación — con el ID del solicitante del pedido y el mensaje de cambio de estado. (Asíncrono o con manejo de fallo tolerante). |
| | 11 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 12 | Retornar HTTP 200 con la entrega actualizada en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | 5B | La entrega está en un estado que no permite asignación → retornar HTTP 422. |
| | 6A | El repartidor no existe → retornar HTTP 404. |
| | 6B | El repartidor no está disponible → retornar HTTP 409 indicando repartidor no disponible. |
| | 7A | La zona de cobertura del repartidor no corresponde → retornar HTTP 422 indicando incompatibilidad de zona. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | E2 | ms-notificaciones no responde → registrar el intento fallido en el log; no afecta la respuesta principal. |
| | | |
| **Postcondición** | La entrega tiene repartidor asignado con `fecha_asignacion` registrada. El repartidor pasa a estado `en ruta`. El solicitante es notificado. | |
| | | |
| **Comentarios** | [Por definir] si se permite la reasignación de repartidor y bajo qué condiciones. | |

---

<a id="dom-rf-014"></a>
### DOM-RF-014 — Actualizar Estado de Entrega

| | | |
|---|---|---|
| **Código** | DOM-RF-014 | |
| **Nombre** | Actualizar Estado de Entrega | |
| **Descripción** | Permite cambiar el estado de una entrega siguiendo las transiciones válidas definidas. Cada cambio de estado genera automáticamente un punto de seguimiento y dispara una notificación al solicitante. | |
| **Actores** | Operador logístico / repartidor con permiso de actualización de estado de entrega | |
| | | |
| **Precondición** | La entrega existe y tiene un estado que permite la transición solicitada. | |
| | El usuario tiene sesión activa y permiso de actualización de estado. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega y el nuevo estado del payload. |
| | 5 | Verificar que la entrega existe. |
| | 6 | Validar que la transición de estado sea permitida según las reglas: `asignada → en camino → entregada`; también se permite `asignada/en camino → fallida` o `→ devuelta` (Regla 14). |
| | 7 | Actualizar el estado de la entrega. Si el nuevo estado es `entregada`, registrar `fecha_entrega` = ahora. Si es `en camino`, registrar `fecha_recogida` = ahora (si aún no está registrada). Actualizar `fecha_actualizacion` = ahora. |
| | 8 | Generar automáticamente un punto de seguimiento (Regla 9): persistir en la entidad Seguimiento con el nuevo estado, la latitud y longitud actuales (si se proporcionan), la fecha/hora actual y una nota descriptiva del cambio de estado. |
| | 9 | Invocar a **ms-notificaciones [NOT]** — operación: enviar notificación de cambio de estado — con el ID del solicitante y el detalle del nuevo estado. |
| | 10 | Si el estado cambia a `entregada`, `fallida` o `devuelta`: actualizar el estado del repartidor asignado a `disponible`. |
| | 11 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 12 | Retornar HTTP 200 con la entrega actualizada en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | 6A | La transición de estado no está permitida → retornar HTTP 422 con mensaje indicando la transición inválida. |
| | | |
| **Excepciones** | E1 | Error al persistir el punto de seguimiento → revertir el cambio de estado y retornar HTTP 500. |
| | E2 | ms-notificaciones no responde → registrar el fallo en el log y continuar con la respuesta exitosa. |
| | E3 | Error de base de datos general → retornar HTTP 500. |
| | | |
| **Postcondición** | El estado de la entrega está actualizado. Se ha generado un punto de seguimiento automático. El solicitante ha sido notificado. El repartidor (si aplica) queda disponible nuevamente. | |
| | | |
| **Comentarios** | La latitud y longitud para el punto de seguimiento automático pueden ser opcionales si no se dispone de ellas en el momento del cambio de estado. | |

---

## Entidad: Seguimiento

---

<a id="dom-rf-015"></a>
### DOM-RF-015 — Registrar Punto de Seguimiento Manual

| | | |
|---|---|---|
| **Código** | DOM-RF-015 | |
| **Nombre** | Registrar Punto de Seguimiento Manual | |
| **Descripción** | Permite registrar manualmente un punto de rastreo geográfico para una entrega en curso, con coordenadas de latitud/longitud y una nota descriptiva. | |
| **Actores** | Repartidor / operador con permiso de registro de seguimiento | |
| | | |
| **Precondición** | La entrega existe y está en estado `en camino`. | |
| | El usuario tiene sesión activa y permiso de registro de seguimiento. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega y el payload: `latitud`, `longitud`, `nota` (opcional). |
| | 5 | Verificar que la entrega existe y está en estado `en camino`. |
| | 6 | Validar que `latitud` y `longitud` son coordenadas geográficas válidas. |
| | 7 | Persistir el nuevo punto de seguimiento con el estado actual de la entrega y `fecha_hora` = ahora. |
| | 8 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 9 | Retornar HTTP 201 con el punto de seguimiento creado en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | 5B | La entrega no está en estado `en camino` → retornar HTTP 422 indicando que solo se pueden agregar puntos durante el trayecto. |
| | 6A | Coordenadas fuera de rango válido → retornar HTTP 400. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El punto de seguimiento queda registrado y disponible en el historial de la entrega. | |
| | | |
| **Comentarios** | Los puntos automáticos generados por DOM-RF-014 usan el mismo modelo de datos pero son insertados internamente. | |

---

<a id="dom-rf-016"></a>
### DOM-RF-016 — Consultar Historial de Seguimiento de una Entrega

| | | |
|---|---|---|
| **Código** | DOM-RF-016 | |
| **Nombre** | Consultar Historial de Seguimiento de una Entrega | |
| **Descripción** | Retorna el listado completo y ordenado cronológicamente de todos los puntos de seguimiento registrados para una entrega específica. | |
| **Actores** | Usuario autenticado con permiso de consulta de seguimiento | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permiso de consulta. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega del path de la petición. |
| | 5 | Verificar que la entrega existe. |
| | 6 | Consultar todos los puntos de seguimiento asociados a la entrega, ordenados por `fecha_hora` ascendente. |
| | 7 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 8 | Retornar HTTP 200 con la lista de puntos de seguimiento en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | 6A | La entrega no tiene puntos de seguimiento → retornar HTTP 200 con lista vacía. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El solicitante obtiene el historial completo de rastreo de la entrega. | |
| | | |
| **Comentarios** | — | |

---

## Entidad: Calificaciones

---

<a id="dom-rf-017"></a>
### DOM-RF-017 — Registrar Calificación de Entrega

| | | |
|---|---|---|
| **Código** | DOM-RF-017 | |
| **Nombre** | Registrar Calificación de Entrega | |
| **Descripción** | Permite al solicitante calificar el servicio de una entrega que se encuentre en estado `entregada`. La puntuación debe estar entre 1 y 5. Tras registrar la calificación, el sistema actualiza automáticamente la calificación promedio del repartidor. | |
| **Actores** | Solicitante del pedido con permiso de calificación de entregas | |
| | | |
| **Precondición** | La entrega existe y está en estado `entregada` (Regla 10). | |
| | La entrega aún no ha sido calificada por el mismo usuario. | |
| | El usuario tiene sesión activa y permiso de calificación. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID de la entrega y el payload: `puntuacion` (entero 1–5), `comentario` (opcional). |
| | 5 | Verificar que la entrega existe y está en estado `entregada`. |
| | 6 | Verificar que el usuario actual no ha calificado ya esta entrega (evitar calificaciones duplicadas). |
| | 7 | Validar que `puntuacion` esté en el rango [1, 5] (Regla 12). |
| | 8 | Persistir la calificación: `entrega` = ID, `calificador` = ID del usuario, `puntuacion`, `comentario`, `fecha` = ahora. |
| | 9 | Calcular el nuevo promedio del repartidor: `SUM(puntuaciones de todas sus calificaciones) / COUNT(calificaciones)` (Regla 11). |
| | 10 | Actualizar `calificacion_promedio` en el registro del repartidor. |
| | 11 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 12 | Retornar HTTP 201 con la calificación registrada en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | La entrega no existe → retornar HTTP 404. |
| | 5B | La entrega no está en estado `entregada` → retornar HTTP 422 indicando que solo se pueden calificar entregas completadas (Regla 10). |
| | 6A | El usuario ya calificó esta entrega → retornar HTTP 409 indicando calificación duplicada. |
| | 7A | Puntuación fuera del rango [1, 5] → retornar HTTP 400. |
| | | |
| **Excepciones** | E1 | Error al actualizar el promedio del repartidor → registrar en log; la calificación ya fue persistida; el promedio puede recalcularse en un proceso compensatorio. |
| | E2 | Error de base de datos general → retornar HTTP 500. |
| | | |
| **Postcondición** | La calificación queda registrada. La `calificacion_promedio` del repartidor está actualizada. | |
| | | |
| **Comentarios** | [Por definir] si solo el solicitante original del pedido puede calificar o también otros roles. | |

---

## Categoría 3 — Requisitos Sugeridos

---

<a id="dom-rf-018"></a>
### DOM-RF-018 — Listar Entregas con Filtros

> **Justificación:** El documento indica que el sistema debe "crear, consultar y actualizar entregas", pero solo define la consulta por ID. Para la operación cotidiana de un módulo logístico es indispensable poder listar y filtrar entregas (por estado, repartidor, fecha, pedido), ya que los operadores necesitan ver el panel de control de entregas activas o históricas.

| | | |
|---|---|---|
| **Código** | DOM-RF-018 | |
| **Nombre** | Listar Entregas con Filtros | |
| **Descripción** | Retorna una lista paginada de entregas, permitiendo filtrar por estado, repartidor, rango de fechas y pedido de origen. | |
| **Actores** | Usuario autenticado con permiso de consulta de entregas | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permiso de consulta. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer los parámetros de filtro opcionales de la petición: `estado`, `repartidor_id`, `fecha_desde`, `fecha_hasta`, `pedido_id`, más parámetros de paginación (`page`, `page_size`). |
| | 5 | Construir y ejecutar la consulta a la base de datos aplicando los filtros proporcionados y paginación. |
| | 6 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 7 | Retornar HTTP 200 con la lista paginada de entregas y metadatos de paginación en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | No se encuentran entregas con los criterios dados → retornar HTTP 200 con lista vacía. |
| | | |
| **Excepciones** | E1 | Parámetros de paginación inválidos → retornar HTTP 400. |
| | E2 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El solicitante recibe el conjunto de entregas que cumplen los criterios indicados. | |
| | | |
| **Comentarios** | [Por definir] valores por defecto y máximos para `page_size`. | |

---

<a id="dom-rf-019"></a>
### DOM-RF-019 — Calcular Costo de Envío

> **Justificación:** El documento (Regla 13) establece que el costo de envío se calcula con base en una tarifa fija configurable o en un cálculo simplificado por distancia. Esta lógica se reutiliza al crear una entrega (DOM-RF-010) y potencialmente al recalcular, por lo que se aísla como requisito independiente.

| | | |
|---|---|---|
| **Código** | DOM-RF-019 | |
| **Nombre** | Calcular Costo de Envío | |
| **Descripción** | Calcula el costo de envío de una entrega aplicando una tarifa fija configurable o una fórmula simplificada basada en la distancia entre la dirección de origen y la de destino. | |
| **Actores** | Proceso interno de ms-domicilios (invocado por DOM-RF-010) | |
| | | |
| **Precondición** | Se dispone de la `direccion_origen` y la `direccion_destino` de la entrega. | |
| | Existe una tarifa o parámetro de cálculo configurado en el sistema. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Leer el modo de cálculo configurado: `tarifa_fija` o `por_distancia`. |
| | 2a | Si `tarifa_fija`: retornar el valor fijo configurado como `costo_envio`. |
| | 2b | Si `por_distancia`: calcular la distancia simplificada entre origen y destino (fórmula a definir) y multiplicar por la tarifa por unidad de distancia configurada. |
| | 3 | Retornar el `costo_envio` calculado al proceso invocante. |
| | | |
| **Secuencia alterna** | 1A | No existe configuración de tarifa → retornar error interno al proceso invocante. |
| | | |
| **Excepciones** | E1 | Error en el cálculo de distancia (coordenadas inválidas o algoritmo falla) → retornar `costo_envio = null` y registrar el incidente. |
| | | |
| **Postcondición** | Se dispone del costo de envío calculado para persistir en la entrega. | |
| | | |
| **Comentarios** | [Por definir] el algoritmo exacto de cálculo por distancia, el formato de las direcciones y dónde se almacena la configuración de tarifas (¿tabla en BD?, ¿variable de entorno?). | |

---

<a id="dom-rf-020"></a>
### DOM-RF-020 — Consultar Calificaciones de un Repartidor

> **Justificación:** El sistema almacena calificaciones individuales por entrega y mantiene un promedio por repartidor. Para transparencia operativa y auditoría de desempeño, es necesario poder consultar el detalle de calificaciones históricas de un repartidor, no solo su promedio agregado.

| | | |
|---|---|---|
| **Código** | DOM-RF-020 | |
| **Nombre** | Consultar Calificaciones de un Repartidor | |
| **Descripción** | Retorna el listado de todas las calificaciones recibidas por un repartidor específico, ordenadas cronológicamente, junto con el promedio actual. | |
| **Actores** | Administrador logístico con permiso de consulta de calificaciones | |
| | | |
| **Precondición** | El repartidor existe en el sistema. | |
| | El usuario tiene sesión activa y permiso de consulta de calificaciones. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID del repartidor del path de la petición. |
| | 5 | Verificar que el repartidor existe. |
| | 6 | Consultar todas las calificaciones cuya `entrega` esté asociada al repartidor, ordenadas por `fecha` descendente. |
| | 7 | Incluir en la respuesta el `calificacion_promedio` actual del repartidor. |
| | 8 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 9 | Retornar HTTP 200 con la lista de calificaciones y el promedio en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | El repartidor no existe → retornar HTTP 404. |
| | 6A | El repartidor no tiene calificaciones → retornar HTTP 200 con lista vacía y promedio `null`. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El solicitante recibe el historial de calificaciones y el desempeño promedio del repartidor. | |
| | | |
| **Comentarios** | [Por definir] si se requiere paginación para repartidores con muchas calificaciones. | |

---

<a id="dom-rf-021"></a>
### DOM-RF-021 — Cambiar Estado de Repartidor

> **Justificación:** La entidad Repartidor define tres estados (`disponible`, `en ruta`, `inactivo`) y las reglas de negocio los referencian continuamente. Sin embargo, el cambio al estado `inactivo` (baja temporal del repartidor) no está cubierto por ningún flujo existente —solo se cubre `disponible` ↔ `en ruta` de forma indirecta mediante la asignación y cierre de entregas. Se necesita un mecanismo explícito para que un administrador active o desactive repartidores.

| | | |
|---|---|---|
| **Código** | DOM-RF-021 | |
| **Nombre** | Cambiar Estado de Repartidor | |
| **Descripción** | Permite a un administrador cambiar manualmente el estado de un repartidor entre `disponible`, `en ruta` e `inactivo`, respetando las restricciones de negocio (Regla 15). | |
| **Actores** | Administrador logístico con permiso de gestión de estado de repartidores | |
| | | |
| **Precondición** | El repartidor existe en el sistema. | |
| | El usuario tiene sesión activa y permiso de cambio de estado. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar **DOM-RF-001** (Validación de Sesión). |
| | 2 | Ejecutar **DOM-RF-002** (Validación de Permisos). |
| | 3 | Ejecutar **DOM-RF-003** (Generación de Request ID). |
| | 4 | Extraer el ID del repartidor y el nuevo estado del payload. |
| | 5 | Verificar que el repartidor existe. |
| | 6 | Validar que el nuevo estado es uno de los valores permitidos: `disponible`, `en ruta`, `inactivo`. |
| | 7 | [Por definir] Evaluar restricciones adicionales: por ejemplo, no se puede poner `inactivo` a un repartidor con entregas activas en estado `en camino`. |
| | 8 | Actualizar el estado y `fecha_actualizacion` = ahora. |
| | 9 | Ejecutar **DOM-RF-004** (Auditoría asíncrona). |
| | 10 | Retornar HTTP 200 con el repartidor actualizado en estructura **DOM-RF-005**. |
| | | |
| **Secuencia alterna** | 5A | El repartidor no existe → retornar HTTP 404. |
| | 6A | Estado inválido → retornar HTTP 400. |
| | 7A | El repartidor tiene entregas activas y se intenta poner `inactivo` → retornar HTTP 422 con mensaje descriptivo. |
| | | |
| **Excepciones** | E1 | Error de base de datos → retornar HTTP 500. |
| | | |
| **Postcondición** | El estado del repartidor está actualizado y refleja su disponibilidad real. | |
| | | |
| **Comentarios** | Las transiciones automáticas de estado (disponible ↔ en ruta) producidas por los flujos de asignación y cierre de entrega siguen siendo responsabilidad de DOM-RF-013 y DOM-RF-014 respectivamente. | |
