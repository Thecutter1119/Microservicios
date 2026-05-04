# Requisitos Funcionales — ms-pedidos [PED]

**Proyecto:** ERP Universitario — Universidad del Valle, Sede Caicedonia  
**Asignatura:** Desarrollo de Software III (750027C)  
**Microservicio:** ms-pedidos  
**Código:** PED  
**Módulo:** Módulo 4 — Logística y Proveedores  
**Stack:** FastAPI + Python + PostgreSQL  
**Fecha:** Febrero 2026  

---

## Tabla de Contenido

### Categoría 1: Requisitos Transversales

| ID | Nombre |
|---|---|
| PED-RF-001 | Validación de Sesión Activa |
| PED-RF-002 | Validación de Permisos por Funcionalidad |
| PED-RF-003 | Generación y Propagación de Request ID |
| PED-RF-004 | Registro de Auditoría Asíncrono |
| PED-RF-005 | Estructura de Respuesta Estándar |

### Categoría 2: Requisitos Funcionales por Entidad

#### Entidad: Pedido

| ID | Nombre |
|---|---|
| PED-RF-006 | Crear Pedido |
| PED-RF-007 | Consultar Pedido por ID |
| PED-RF-008 | Listar Pedidos |
| PED-RF-009 | Actualizar Pedido en Borrador |
| PED-RF-010 | Avanzar Estado del Pedido |
| PED-RF-011 | Cancelar Pedido |
| PED-RF-012 | Registrar Recepción de Pedido (Total o Parcial) |

#### Entidad: Ítem de Pedido

| ID | Nombre |
|---|---|
| PED-RF-013 | Agregar Ítem a Pedido |
| PED-RF-014 | Actualizar Ítem de Pedido |
| PED-RF-015 | Remover Ítem de Pedido |

#### Entidad: Historial de Estados

| ID | Nombre |
|---|---|
| PED-RF-016 | Consultar Historial de Estados de un Pedido |

### Categoría 3: Requisitos Sugeridos

| ID | Nombre |
|---|---|
| PED-RF-017 | Consultar Pedido por Número de Pedido |
| PED-RF-018 | Listar Ítems de un Pedido |
| PED-RF-019 | Recalcular Monto Total del Pedido |
| PED-RF-020 | Exponer Datos del Pedido para ms-domicilios |
| PED-RF-021 | Validar Existencia del Activo en ms-inventario |
| PED-RF-022 | Validar Proveedor con Contrato Vigente en ms-proveedores |

---

---

## Categoría 1: Requisitos Transversales

> Estos requisitos aplican a **todas** las operaciones del microservicio. Los demás requisitos los referencian en su secuencia normal en lugar de repetir los pasos.

---

### PED-RF-001 — Validación de Sesión Activa

| | | |
|---|---|---|
| **Código** | PED-RF-001 | |
| **Nombre** | Validación de Sesión Activa | |
| **Descripción** | Verifica que el usuario que realiza la petición tiene una sesión activa y válida, consultando a ms-autenticacion antes de ejecutar cualquier lógica de negocio. | |
| **Actores** | Microservicio ms-autenticacion [AUTH], cualquier usuario o servicio que invoque una operación de ms-pedidos | |
| | | |
| **Precondición** | La petición HTTP ha sido recibida por ms-pedidos. | |
| | La petición incluye un token de sesión en los encabezados (Authorization). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-003] para generar o reutilizar el Request ID de la petición. |
| | 2 | ms-pedidos extrae el token de sesión del encabezado de la petición. |
| | 3 | ms-pedidos invoca a **ms-autenticacion [AUTH]** — operación de validación de sesión — enviando el token y el Request ID. Se espera como respuesta: confirmación de sesión válida e identidad del usuario (ID y rol). |
| | 4 | ms-autenticacion retorna confirmación de sesión válida junto con los datos del usuario autenticado. |
| | 5 | ms-pedidos almacena en el contexto de la petición el identificador y rol del usuario para uso posterior. |
| | 6 | El flujo continúa hacia [PED-RF-002]. |
| | | |
| **Secuencia alterna** | 4A | Si ms-autenticacion retorna sesión inválida o expirada: ms-pedidos rechaza la petición, ejecuta [PED-RF-005] con código HTTP 401 y mensaje "Sesión no válida o expirada", y finaliza sin procesar la operación. |
| | | |
| **Excepciones** | E1 | Si ms-autenticacion no responde o devuelve error técnico: ms-pedidos rechaza la petición con HTTP 503, ejecuta [PED-RF-005], y finaliza. |
| | | |
| **Postcondición** | La sesión del usuario ha sido validada y sus datos están disponibles en el contexto de la petición. | |
| | | |
| **Comentarios** | Regla transversal RT-01. Este requisito debe ejecutarse como primer paso en toda operación del microservicio. | |

---

### PED-RF-002 — Validación de Permisos por Funcionalidad

| | | |
|---|---|---|
| **Código** | PED-RF-002 | |
| **Nombre** | Validación de Permisos por Funcionalidad | |
| **Descripción** | Verifica que el rol del usuario autenticado tiene el permiso requerido para ejecutar la funcionalidad solicitada, consultando a ms-roles. | |
| **Actores** | Microservicio ms-roles [ROL], usuario autenticado | |
| | | |
| **Precondición** | PED-RF-001 fue ejecutado exitosamente. | |
| | El contexto de la petición contiene el identificador y rol del usuario. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos determina el código de permiso asociado a la funcionalidad solicitada. |
| | 2 | ms-pedidos invoca a **ms-roles [ROL]** — operación de verificación de permiso — enviando el rol del usuario, el código de permiso y el Request ID. Se espera como respuesta: autorizado o no autorizado. |
| | 3 | ms-roles retorna confirmación de que el rol tiene el permiso requerido. |
| | 4 | El flujo continúa hacia la lógica de negocio correspondiente. |
| | | |
| **Secuencia alterna** | 3A | Si ms-roles retorna que el rol no tiene el permiso: ms-pedidos rechaza la petición, ejecuta [PED-RF-005] con HTTP 403 y mensaje "Permisos insuficientes", y finaliza. |
| | | |
| **Excepciones** | E1 | Si ms-roles no responde o devuelve error técnico: ms-pedidos rechaza la petición con HTTP 503, ejecuta [PED-RF-005], y finaliza. |
| | | |
| **Postcondición** | El permiso del usuario ha sido verificado y el flujo puede continuar hacia la lógica de negocio. | |
| | | |
| **Comentarios** | Regla transversal RT-02. Cada funcionalidad tiene un código de permiso único; los códigos específicos son [Por definir] por el equipo de arquitectura. | |

---

### PED-RF-003 — Generación y Propagación de Request ID

| | | |
|---|---|---|
| **Código** | PED-RF-003 | |
| **Nombre** | Generación y Propagación de Request ID | |
| **Descripción** | Genera un identificador único de rastreo para cada petición entrante, o reutiliza el que ya viene de otro microservicio, propagándolo en todas las llamadas salientes y respuestas. | |
| **Actores** | ms-pedidos (internamente), cualquier servicio consumidor | |
| | | |
| **Precondición** | ms-pedidos ha recibido una petición HTTP. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos inspecciona los encabezados de la petición en busca de un Request ID existente. |
| | 2 | Si no existe Request ID, se genera uno nuevo con el formato: `PED-{timestamp_unix}-{id_corto_aleatorio}` (ejemplo: `PED-1740000000-a3f8b2`). |
| | 3 | El Request ID se almacena en el contexto de la petición. |
| | 4 | Toda llamada saliente hacia otros microservicios incluye el Request ID en los encabezados. |
| | 5 | Toda respuesta generada incluye el Request ID en cabeceras y cuerpo (ver [PED-RF-005]). |
| | | |
| **Secuencia alterna** | 1A | Si la petición ya trae un Request ID en los encabezados: ms-pedidos lo reutiliza tal como viene, sin generar uno nuevo. |
| | | |
| **Excepciones** | E1 | Si el formato del Request ID recibido no es reconocible: ms-pedidos genera uno nuevo con el prefijo PED y lo usa para la operación. |
| | | |
| **Postcondición** | El Request ID está disponible en el contexto de la petición y será incluido en todas las respuestas y llamadas salientes. | |
| | | |
| **Comentarios** | Regla transversal RT-04. El prefijo del Request ID debe ser siempre "PED" cuando lo genera este microservicio. | |

---

### PED-RF-004 — Registro de Auditoría Asíncrono

| | | |
|---|---|---|
| **Código** | PED-RF-004 | |
| **Nombre** | Registro de Auditoría Asíncrono | |
| **Descripción** | Genera y envía de forma asíncrona un registro de log en formato JSON a ms-auditoria tras cada operación realizada, sin bloquear ni retrasar la respuesta al usuario. | |
| **Actores** | Microservicio ms-auditoria [AUD], ms-pedidos (internamente) | |
| | | |
| **Precondición** | Una operación de ms-pedidos ha sido procesada (exitosa o fallida). | |
| | El contexto de la petición contiene: Request ID, usuario, funcionalidad, código de respuesta y duración. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos construye el registro de log en formato JSON con los campos: fecha/hora, Request ID, nombre del microservicio (`ms-pedidos`), funcionalidad ejecutada, método HTTP, código de respuesta, duración en milisegundos, ID del usuario y detalle descriptivo. |
| | 2 | ms-pedidos envía el registro de forma **asíncrona** a **ms-auditoria [AUD]** — operación de ingesta de log — sin esperar confirmación. |
| | 3 | La respuesta ya fue enviada al usuario antes o en paralelo con este paso. |
| | | |
| **Secuencia alterna** | — | No aplica (el envío es asíncrono y no afecta el flujo principal). |
| | | |
| **Excepciones** | E1 | Si el envío a ms-auditoria falla por cualquier causa (timeout, error de red, servicio caído): ms-pedidos registra el fallo internamente en su log local y continúa operando con normalidad. |
| | | |
| **Postcondición** | El registro de log fue enviado a ms-auditoria o el fallo fue registrado localmente. La operación principal no se ve afectada. | |
| | | |
| **Comentarios** | Regla transversal RT-05. El mecanismo de cola asíncrona (ej. mensaje en cola, tarea en background) es [Por definir] según la implementación técnica del equipo. | |

---

### PED-RF-005 — Estructura de Respuesta Estándar

| | | |
|---|---|---|
| **Código** | PED-RF-005 | |
| **Nombre** | Estructura de Respuesta Estándar | |
| **Descripción** | Define el formato uniforme que deben seguir todas las respuestas emitidas por ms-pedidos, tanto en operaciones exitosas como en errores. | |
| **Actores** | ms-pedidos (internamente), cualquier consumidor de la API | |
| | | |
| **Precondición** | Una operación ha concluido (con éxito o con error) y ms-pedidos va a emitir una respuesta. | |
| | El Request ID está disponible en el contexto (ver [PED-RF-003]). | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos construye el objeto de respuesta con los siguientes campos: `request_id` (Request ID de la petición), `success` (booleano: true/false), `data` (datos resultantes o null), `message` (mensaje descriptivo de la operación), `timestamp` (fecha y hora de la respuesta en ISO 8601). |
| | 2 | ms-pedidos incluye el Request ID también en los encabezados HTTP de la respuesta (ej. header `X-Request-ID`). |
| | 3 | ms-pedidos retorna la respuesta con el código HTTP correspondiente a la operación. |
| | | |
| **Secuencia alterna** | — | No aplica. |
| | | |
| **Excepciones** | E1 | Si ocurre un error inesperado antes de poder construir la respuesta estándar: ms-pedidos retorna al menos el campo `request_id` y un mensaje de error genérico con HTTP 500. |
| | | |
| **Postcondición** | La respuesta entregada al consumidor cumple con la estructura estándar del sistema. | |
| | | |
| **Comentarios** | Regla transversal RT-06. La estructura de `data` varía según la operación; cada requisito funcional define qué retorna en ese campo. | |

---

---

## Categoría 2: Requisitos Funcionales por Entidad

---

### Entidad: Pedido

---

### PED-RF-006 — Crear Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-006 | |
| **Nombre** | Crear Pedido | |
| **Descripción** | Permite a un usuario autorizado crear un nuevo pedido en estado "borrador", registrando el solicitante, el proveedor asignado y las observaciones iniciales. | |
| **Actores** | Usuario autenticado con permiso de creación de pedidos, ms-proveedores [PRV], ms-inventario [INV] | |
| | | |
| **Precondición** | El usuario tiene una sesión activa y permisos para crear pedidos. | |
| | Se proporciona al menos el proveedor asignado y el solicitante. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | Ejecutar [PED-RF-022] — Validar Proveedor con Contrato Vigente: invocar a **ms-proveedores [PRV]** para verificar que el proveedor existe y tiene contrato vigente. Se espera: confirmación de vigencia. |
| | 4 | ms-pedidos genera un número de pedido único. |
| | 5 | ms-pedidos crea el registro del pedido con estado **"borrador"**, registrando: número de pedido, solicitante (usuario autenticado), proveedor asignado, fecha de solicitud (timestamp actual), monto total = 0, observaciones y fechas de creación/actualización. |
| | 6 | ms-pedidos registra en el historial de estados la entrada inicial: estado anterior = null, nuevo estado = "borrador", usuario y fecha/hora. |
| | 7 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 201 y los datos del pedido creado. |
| | 8 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el proveedor no existe o no tiene contrato vigente: ejecutar [PED-RF-005] con HTTP 422 y mensaje descriptivo. Finalizar. |
| | | |
| **Excepciones** | E1 | Si ms-proveedores no responde: ejecutar [PED-RF-005] con HTTP 503. Finalizar. |
| | E2 | Si ocurre un error de base de datos al guardar el pedido: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El pedido queda registrado en la base de datos con estado "borrador". | |
| | El historial de estados tiene una entrada inicial. | |
| | El monto total es 0 (no hay ítems aún). | |
| | | |
| **Comentarios** | Reglas de negocio aplicadas: RN-02, RN-03, RN-07, RN-08. El número de pedido único puede generarse como secuencia de BD o UUID; formato [Por definir]. | |

---

### PED-RF-007 — Consultar Pedido por ID

| | | |
|---|---|---|
| **Código** | PED-RF-007 | |
| **Nombre** | Consultar Pedido por ID | |
| **Descripción** | Permite a un usuario autorizado obtener el detalle completo de un pedido específico a partir de su identificador interno. | |
| **Actores** | Usuario autenticado con permiso de consulta de pedidos, ms-domicilios [DOM] (como consumidor externo) | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para consultar pedidos. | |
| | Se proporciona un ID de pedido válido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por el ID proporcionado en la base de datos. |
| | 4 | ms-pedidos retorna el detalle completo del pedido, incluyendo todos sus atributos y la lista de ítems asociados. |
| | 5 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 6 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si no existe un pedido con el ID proporcionado: ejecutar [PED-RF-005] con HTTP 404 y mensaje "Pedido no encontrado". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El usuario recibe el detalle completo del pedido solicitado. | |
| | | |
| **Comentarios** | Este endpoint es también consumido por ms-domicilios [DOM] para obtener datos del pedido al gestionar entregas (ver sección 7, consumidores). | |

---

### PED-RF-008 — Listar Pedidos

| | | |
|---|---|---|
| **Código** | PED-RF-008 | |
| **Nombre** | Listar Pedidos | |
| **Descripción** | Permite a un usuario autorizado obtener un listado de pedidos, con soporte de filtros por estado, proveedor, solicitante o rango de fechas. | |
| **Actores** | Usuario autenticado con permiso de consulta de pedidos | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para consultar pedidos. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos recibe y aplica los filtros opcionales: estado, proveedor, solicitante, rango de fechas de solicitud. |
| | 4 | ms-pedidos consulta la base de datos y retorna la lista de pedidos que cumplen los criterios, con paginación. |
| | 5 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 6 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 4A | Si no existen pedidos que cumplan los filtros: retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El usuario recibe la lista paginada de pedidos según los filtros aplicados. | |
| | | |
| **Comentarios** | Los parámetros de paginación (tamaño de página, número de página) son [Por definir]. | |

---

### PED-RF-009 — Actualizar Pedido en Borrador

| | | |
|---|---|---|
| **Código** | PED-RF-009 | |
| **Nombre** | Actualizar Pedido en Borrador | |
| **Descripción** | Permite modificar los datos generales de un pedido (proveedor, observaciones, etc.) únicamente mientras el pedido se encuentre en estado "borrador". | |
| **Actores** | Usuario autenticado con permiso de actualización de pedidos | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para actualizar pedidos. | |
| | El pedido identificado por su ID existe en la base de datos. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica que su estado es **"borrador"**. |
| | 4 | Si se cambia el proveedor asignado, ejecutar [PED-RF-022] — Validar Proveedor con Contrato Vigente en ms-proveedores [PRV]. |
| | 5 | ms-pedidos aplica los cambios a los campos permitidos: proveedor asignado y/u observaciones. |
| | 6 | ms-pedidos actualiza el campo `fecha_actualizacion` con el timestamp actual. |
| | 7 | Ejecutar [PED-RF-019] — Recalcular Monto Total del Pedido (si aplica). |
| | 8 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 9 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido no está en estado "borrador": ejecutar [PED-RF-005] con HTTP 422 y mensaje "Solo se pueden modificar pedidos en estado borrador". Finalizar. |
| | 4A | Si el nuevo proveedor no existe o no tiene contrato vigente: ejecutar [PED-RF-005] con HTTP 422. Finalizar. |
| | | |
| **Excepciones** | E1 | Si ms-proveedores no responde: ejecutar [PED-RF-005] con HTTP 503. Finalizar. |
| | E2 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | Los datos generales del pedido han sido actualizados. La `fecha_actualizacion` refleja el momento del cambio. | |
| | | |
| **Comentarios** | Regla de negocio RN-01. Los campos que no se permiten modificar por esta vía (estado, número de pedido, solicitante) son inmutables una vez creados. | |

---

### PED-RF-010 — Avanzar Estado del Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-010 | |
| **Nombre** | Avanzar Estado del Pedido | |
| **Descripción** | Permite avanzar el estado de un pedido al siguiente en el flujo secuencial (borrador → enviado → aprobado → en proceso → recibido), registrando el cambio en el historial. | |
| **Actores** | Usuario autenticado con permiso de cambio de estado de pedidos, ms-proveedores [PRV] | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para cambiar el estado del pedido. | |
| | El pedido existe y no está en estado "recibido" ni "cancelado". | |
| | El usuario proporciona un comentario para el registro del cambio de estado. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y determina su estado actual. |
| | 4 | ms-pedidos determina el estado siguiente según el flujo: borrador → enviado → aprobado → en proceso → recibido. |
| | 5 | Si el nuevo estado es "aprobado" o "en proceso", ejecutar [PED-RF-022] — Validar Proveedor con Contrato Vigente en **ms-proveedores [PRV]**. Se espera confirmación de vigencia del contrato. |
| | 6 | ms-pedidos actualiza el estado del pedido al estado siguiente. |
| | 7 | Si el nuevo estado es "aprobado", registrar la `fecha_aprobacion` con el timestamp actual. |
| | 8 | ms-pedidos registra el cambio en el historial de estados con: estado anterior, nuevo estado, usuario, fecha/hora y comentario proporcionado. |
| | 9 | ms-pedidos actualiza `fecha_actualizacion`. |
| | 10 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 11 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido está en estado "recibido" o "cancelado": ejecutar [PED-RF-005] con HTTP 422 y mensaje "No se puede avanzar el estado de un pedido recibido o cancelado". Finalizar. |
| | 5A | Si el proveedor no tiene contrato vigente: ejecutar [PED-RF-005] con HTTP 422 y mensaje "El proveedor asignado no tiene contrato vigente". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ms-proveedores no responde: ejecutar [PED-RF-005] con HTTP 503. Finalizar. |
| | E2 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El pedido avanza al siguiente estado en el flujo. | |
| | El historial de estados tiene una nueva entrada con los datos del cambio. | |
| | | |
| **Comentarios** | Reglas de negocio RN-02, RN-03, RN-08. No se permiten saltos de estado. El campo comentario es obligatorio para garantizar trazabilidad. | |

---

### PED-RF-011 — Cancelar Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-011 | |
| **Nombre** | Cancelar Pedido | |
| **Descripción** | Permite cancelar un pedido en cualquier estado previo a "recibido", registrando el motivo de la cancelación en el historial de estados. | |
| **Actores** | Usuario autenticado con permiso de cancelación de pedidos | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para cancelar pedidos. | |
| | El pedido existe y su estado no es "recibido". | |
| | El usuario proporciona un motivo de cancelación. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica que su estado no es "recibido". |
| | 4 | ms-pedidos actualiza el estado del pedido a **"cancelado"**. |
| | 5 | ms-pedidos registra el cambio en el historial de estados con: estado anterior, nuevo estado = "cancelado", usuario, fecha/hora y el motivo de cancelación como comentario. |
| | 6 | ms-pedidos actualiza `fecha_actualizacion`. |
| | 7 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 8 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido ya está en estado "recibido": ejecutar [PED-RF-005] con HTTP 422 y mensaje "No se puede cancelar un pedido ya recibido". Finalizar. |
| | 3C | Si el pedido ya está en estado "cancelado": ejecutar [PED-RF-005] con HTTP 422 y mensaje "El pedido ya se encuentra cancelado". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El pedido queda en estado "cancelado". | |
| | El historial de estados refleja la cancelación con su motivo. | |
| | | |
| **Comentarios** | Reglas de negocio RN-03, RN-04. El motivo de cancelación es obligatorio. | |

---

### PED-RF-012 — Registrar Recepción de Pedido (Total o Parcial)

| | | |
|---|---|---|
| **Código** | PED-RF-012 | |
| **Nombre** | Registrar Recepción de Pedido (Total o Parcial) | |
| **Descripción** | Permite registrar la recepción de uno o más ítems del pedido, actualizando las cantidades recibidas, el estado de cada ítem y el estado global del pedido según corresponda, y notificando la entrada de stock a ms-inventario. | |
| **Actores** | Usuario autenticado con permiso de recepción de pedidos, ms-inventario [INV] | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para recepcionar pedidos. | |
| | El pedido existe y está en estado "en proceso" o "recibido parcial". | |
| | Se proporcionan las cantidades recibidas por cada ítem a recepcionar. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica que está en estado "en proceso" o "recibido parcial". |
| | 4 | Para cada ítem incluido en la recepción: validar que la cantidad recibida en este acto no supera la cantidad pendiente (cantidad solicitada − cantidad ya recibida). |
| | 5 | ms-pedidos actualiza la `cantidad_recibida` de cada ítem sumando la nueva cantidad. |
| | 6 | ms-pedidos actualiza el estado de cada ítem: si `cantidad_recibida` = `cantidad_solicitada` → "recibido"; si `cantidad_recibida` < `cantidad_solicitada` → "recibido parcial". |
| | 7 | Ejecutar [PED-RF-021] — invocar a **ms-inventario [INV]** — operación de registro de entrada de stock — enviando el activo y la cantidad recibida por cada ítem. Se espera: confirmación de registro. |
| | 8 | ms-pedidos evalúa el estado global del pedido: si todos los ítems están en "recibido" → estado del pedido = "recibido" y registrar `fecha_recepcion`; si al menos un ítem está en "recibido parcial" o "pendiente" → estado del pedido = "recibido parcial". |
| | 9 | ms-pedidos registra el cambio de estado en el historial con usuario, fecha/hora y comentario. |
| | 10 | ms-pedidos actualiza `fecha_actualizacion`. |
| | 11 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 12 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido no está en estado "en proceso" ni "recibido parcial": ejecutar [PED-RF-005] con HTTP 422 y mensaje descriptivo. Finalizar. |
| | 4A | Si la cantidad recibida de algún ítem supera la cantidad pendiente: ejecutar [PED-RF-005] con HTTP 422 y mensaje "La cantidad recibida supera la cantidad pendiente del ítem". Finalizar. |
| | 7A | Si ms-inventario retorna error al registrar la entrada: ejecutar [PED-RF-005] con HTTP 502 y mensaje descriptivo. Revertir cambios. Finalizar. |
| | | |
| **Excepciones** | E1 | Si ms-inventario no responde: ejecutar [PED-RF-005] con HTTP 503. Revertir cambios. Finalizar. |
| | E2 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | Las cantidades recibidas de los ítems han sido actualizadas. | |
| | El estado de cada ítem refleja si fue recibido total o parcialmente. | |
| | El estado del pedido es "recibido" o "recibido parcial" según corresponda. | |
| | La entrada de stock ha sido registrada en ms-inventario. | |
| | El historial de estados tiene una nueva entrada. | |
| | | |
| **Comentarios** | Reglas de negocio RN-03, RN-05, RN-09. La reversión de cambios ante fallo de ms-inventario implica transaccionalidad; el mecanismo de rollback es [Por definir]. | |

---

### Entidad: Ítem de Pedido

---

### PED-RF-013 — Agregar Ítem a Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-013 | |
| **Nombre** | Agregar Ítem a Pedido | |
| **Descripción** | Permite agregar una nueva línea de ítem a un pedido que se encuentra en estado "borrador", validando que el activo solicitado existe en el inventario y recalculando el monto total. | |
| **Actores** | Usuario autenticado con permiso de gestión de ítems, ms-inventario [INV] | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para gestionar ítems de pedido. | |
| | El pedido existe y está en estado "borrador". | |
| | Se proporciona el activo solicitado, cantidad solicitada y valor unitario. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica que está en estado "borrador". |
| | 4 | Ejecutar [PED-RF-021] — invocar a **ms-inventario [INV]** — operación de verificación de existencia del activo — enviando el ID del activo. Se espera: confirmación de que el activo existe. |
| | 5 | ms-pedidos crea el ítem con: referencia al pedido, activo solicitado, descripción, cantidad solicitada, cantidad recibida = 0, valor unitario, subtotal = cantidad solicitada × valor unitario, estado = "pendiente". |
| | 6 | Ejecutar [PED-RF-019] — Recalcular Monto Total del Pedido. |
| | 7 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 201. |
| | 8 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido no está en estado "borrador": ejecutar [PED-RF-005] con HTTP 422 y mensaje "Solo se pueden agregar ítems a pedidos en estado borrador". Finalizar. |
| | 4A | Si ms-inventario indica que el activo no existe: ejecutar [PED-RF-005] con HTTP 422 y mensaje "El activo solicitado no existe en el inventario". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ms-inventario no responde: ejecutar [PED-RF-005] con HTTP 503. Finalizar. |
| | E2 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El ítem queda registrado en el pedido con estado "pendiente". | |
| | El monto total del pedido ha sido recalculado. | |
| | | |
| **Comentarios** | Reglas de negocio RN-06, RN-07. El valor unitario lo ingresa el usuario; no se obtiene automáticamente del inventario (definición [Por confirmar] con el equipo). | |

---

### PED-RF-014 — Actualizar Ítem de Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-014 | |
| **Nombre** | Actualizar Ítem de Pedido | |
| **Descripción** | Permite modificar los datos de un ítem existente (descripción, cantidad solicitada, valor unitario) dentro de un pedido en estado "borrador". | |
| **Actores** | Usuario autenticado con permiso de gestión de ítems | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para gestionar ítems de pedido. | |
| | El pedido existe y está en estado "borrador". | |
| | El ítem identificado existe dentro del pedido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica que está en estado "borrador". |
| | 4 | ms-pedidos ubica el ítem por su ID dentro del pedido. |
| | 5 | ms-pedidos aplica los cambios a los campos permitidos: descripción, cantidad solicitada y/o valor unitario. |
| | 6 | ms-pedidos recalcula el subtotal del ítem = cantidad solicitada × valor unitario. |
| | 7 | Ejecutar [PED-RF-019] — Recalcular Monto Total del Pedido. |
| | 8 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 9 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido no está en estado "borrador": ejecutar [PED-RF-005] con HTTP 422 y mensaje "Solo se pueden modificar ítems de pedidos en estado borrador". Finalizar. |
| | 4A | Si el ítem no existe en el pedido: ejecutar [PED-RF-005] con HTTP 404 y mensaje "Ítem no encontrado". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | Los datos del ítem han sido actualizados. El subtotal del ítem y el monto total del pedido han sido recalculados. | |
| | | |
| **Comentarios** | Reglas de negocio RN-06, RN-07. No se permite cambiar el activo solicitado de un ítem ya creado; se debe remover y agregar uno nuevo. | |

---

### PED-RF-015 — Remover Ítem de Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-015 | |
| **Nombre** | Remover Ítem de Pedido | |
| **Descripción** | Permite eliminar un ítem de un pedido que se encuentra en estado "borrador", recalculando el monto total del pedido. | |
| **Actores** | Usuario autenticado con permiso de gestión de ítems | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para gestionar ítems de pedido. | |
| | El pedido existe y está en estado "borrador". | |
| | El ítem a remover existe dentro del pedido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica que está en estado "borrador". |
| | 4 | ms-pedidos ubica el ítem por su ID dentro del pedido. |
| | 5 | ms-pedidos elimina el registro del ítem. |
| | 6 | Ejecutar [PED-RF-019] — Recalcular Monto Total del Pedido. |
| | 7 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 8 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 3B | Si el pedido no está en estado "borrador": ejecutar [PED-RF-005] con HTTP 422 y mensaje "Solo se pueden remover ítems de pedidos en estado borrador". Finalizar. |
| | 4A | Si el ítem no existe: ejecutar [PED-RF-005] con HTTP 404 y mensaje "Ítem no encontrado". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El ítem ha sido eliminado del pedido. El monto total del pedido ha sido recalculado. | |
| | | |
| **Comentarios** | Reglas de negocio RN-06, RN-07. La eliminación es física (hard delete) o lógica (soft delete) según decisión del equipo [Por definir]. | |

---

### Entidad: Historial de Estados

---

### PED-RF-016 — Consultar Historial de Estados de un Pedido

| | | |
|---|---|---|
| **Código** | PED-RF-016 | |
| **Nombre** | Consultar Historial de Estados de un Pedido | |
| **Descripción** | Permite a un usuario autorizado obtener el registro completo de todos los cambios de estado ocurridos en un pedido, ordenados cronológicamente. | |
| **Actores** | Usuario autenticado con permiso de consulta de pedidos | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para consultar pedidos. | |
| | El pedido identificado por su ID existe en la base de datos. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica su existencia. |
| | 4 | ms-pedidos consulta todos los registros del historial de estados asociados al pedido, ordenados por `fecha_hora_cambio` ascendente. |
| | 5 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200 y la lista de entradas del historial. |
| | 6 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404 y mensaje "Pedido no encontrado". Finalizar. |
| | 4A | Si el pedido existe pero no tiene entradas de historial: retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El usuario recibe el historial completo de cambios de estado del pedido. | |
| | | |
| **Comentarios** | Cada entrada del historial incluye: estado anterior, nuevo estado, usuario, fecha/hora y comentario. Cumple con la regla RN-03. | |

---

---

## Categoría 3: Requisitos Sugeridos

> Estos requisitos no están escritos explícitamente en el documento de referencia, pero se deducen del contexto, las entidades, las dependencias o las buenas prácticas del sistema.

---

### PED-RF-017 — Consultar Pedido por Número de Pedido

> **Justificación:** El documento define el "número de pedido" como un atributo único y visible del negocio (diferente al ID interno de base de datos). Los usuarios operativos identifican pedidos por este número en contextos reales (facturas, entregas, comunicaciones con proveedores), por lo que es necesario un endpoint de búsqueda por este campo adicional al de búsqueda por ID interno.

| | | |
|---|---|---|
| **Código** | PED-RF-017 | |
| **Nombre** | Consultar Pedido por Número de Pedido | |
| **Descripción** | Permite buscar y obtener el detalle de un pedido utilizando su número de pedido único (clave de negocio), en lugar del identificador interno de base de datos. | |
| **Actores** | Usuario autenticado con permiso de consulta de pedidos, ms-domicilios [DOM] | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para consultar pedidos. | |
| | Se proporciona un número de pedido válido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido cuyo `numero_pedido` coincide con el valor proporcionado. |
| | 4 | ms-pedidos retorna el detalle completo del pedido encontrado. |
| | 5 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 6 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si no existe un pedido con ese número: ejecutar [PED-RF-005] con HTTP 404 y mensaje "Número de pedido no encontrado". Finalizar. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El usuario recibe el detalle del pedido identificado por el número de pedido. | |
| | | |
| **Comentarios** | Puede implementarse como parámetro de query en el mismo endpoint de listado ([PED-RF-008]) o como endpoint independiente. Decisión [Por definir]. | |

---

### PED-RF-018 — Listar Ítems de un Pedido

> **Justificación:** Aunque los ítems se pueden incluir en la respuesta de consulta de pedido ([PED-RF-007]), un endpoint dedicado a listar los ítems de un pedido facilita la paginación y filtrado cuando un pedido tiene muchas líneas, y es una práctica estándar en APIs REST para recursos anidados.

| | | |
|---|---|---|
| **Código** | PED-RF-018 | |
| **Nombre** | Listar Ítems de un Pedido | |
| **Descripción** | Permite obtener la lista completa de ítems asociados a un pedido específico, con sus cantidades solicitadas, recibidas, subtotales y estados. | |
| **Actores** | Usuario autenticado con permiso de consulta de pedidos | |
| | | |
| **Precondición** | El usuario tiene sesión activa y permisos para consultar pedidos. | |
| | El pedido identificado existe en la base de datos. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-001] — Validación de Sesión Activa. |
| | 2 | Ejecutar [PED-RF-002] — Validación de Permisos por Funcionalidad. |
| | 3 | ms-pedidos busca el pedido por ID y verifica su existencia. |
| | 4 | ms-pedidos consulta todos los ítems asociados al pedido. |
| | 5 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200 y la lista de ítems. |
| | 6 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 3A | Si el pedido no existe: ejecutar [PED-RF-005] con HTTP 404. Finalizar. |
| | 4A | Si el pedido no tiene ítems: retornar lista vacía con HTTP 200. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | El usuario recibe la lista de todos los ítems del pedido con sus datos actuales. | |
| | | |
| **Comentarios** | [Por definir] si se implementa como endpoint independiente (`GET /pedidos/{id}/items`) o incluido en la respuesta de [PED-RF-007]. | |

---

### PED-RF-019 — Recalcular Monto Total del Pedido

> **Justificación:** La regla RN-07 establece que el monto total debe calcularse automáticamente. Este cálculo se invoca desde múltiples operaciones (agregar, actualizar y remover ítems), por lo que se define como un requisito reutilizable independiente para evitar duplicación y asegurar consistencia.

| | | |
|---|---|---|
| **Código** | PED-RF-019 | |
| **Nombre** | Recalcular Monto Total del Pedido | |
| **Descripción** | Recalcula y actualiza el campo `monto_total` del pedido sumando los subtotales de todos sus ítems activos. Es invocado internamente por otras operaciones. | |
| **Actores** | ms-pedidos (proceso interno) | |
| | | |
| **Precondición** | El pedido existe y su ID está disponible en el contexto de la operación que lo invoca. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos consulta todos los ítems activos del pedido. |
| | 2 | ms-pedidos calcula: `monto_total` = Σ (cantidad_solicitada × valor_unitario) de cada ítem. |
| | 3 | ms-pedidos actualiza el campo `monto_total` del pedido en la base de datos. |
| | | |
| **Secuencia alterna** | 1A | Si el pedido no tiene ítems: `monto_total` = 0. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos al actualizar: propagar la excepción al requisito invocador. |
| | | |
| **Postcondición** | El campo `monto_total` del pedido refleja la suma actualizada de todos los subtotales de ítems. | |
| | | |
| **Comentarios** | Regla de negocio RN-07. Este es un proceso interno; no expone un endpoint HTTP propio. | |

---

### PED-RF-020 — Exponer Datos del Pedido para ms-domicilios

> **Justificación:** El documento indica que ms-domicilios [DOM] consume datos del pedido al gestionar entregas. Si bien [PED-RF-007] puede cubrir este caso, es recomendable definir explícitamente las consideraciones de autenticación entre servicios (token de aplicación) y los campos mínimos requeridos por DOM, para garantizar que la integración esté contemplada en el diseño.

| | | |
|---|---|---|
| **Código** | PED-RF-020 | |
| **Nombre** | Exponer Datos del Pedido para ms-domicilios | |
| **Descripción** | Garantiza que el endpoint de consulta de pedido esté accesible para llamadas de servicio a servicio provenientes de ms-domicilios [DOM], autenticadas mediante token de aplicación, retornando al menos los datos necesarios para gestionar una entrega. | |
| **Actores** | ms-domicilios [DOM] (consumidor de servicio) | |
| | | |
| **Precondición** | ms-domicilios envía su token de aplicación cifrado en la petición. | |
| | La petición incluye el ID o número del pedido requerido. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | Ejecutar [PED-RF-003] — Generación y Propagación de Request ID (reutilizando el Request ID de ms-domicilios si viene en la petición). |
| | 2 | ms-pedidos valida el token de aplicación de ms-domicilios (regla transversal RT-03). |
| | 3 | ms-pedidos busca el pedido por el ID o número de pedido proporcionado. |
| | 4 | ms-pedidos retorna los datos del pedido requeridos por ms-domicilios: número de pedido, proveedor, estado, solicitante, ítems y monto total. |
| | 5 | Ejecutar [PED-RF-005] — retornar respuesta estándar con HTTP 200. |
| | 6 | Ejecutar [PED-RF-004] — Registro de Auditoría Asíncrono. |
| | | |
| **Secuencia alterna** | 2A | Si el token de aplicación es inválido: retornar HTTP 401 y finalizar. |
| | 3A | Si el pedido no existe: retornar HTTP 404 y finalizar. |
| | | |
| **Excepciones** | E1 | Si ocurre un error de base de datos: ejecutar [PED-RF-005] con HTTP 500. Finalizar. |
| | | |
| **Postcondición** | ms-domicilios recibe los datos del pedido necesarios para gestionar la entrega asociada. | |
| | | |
| **Comentarios** | Puede compartir implementación con [PED-RF-007]; la distinción clave es el mecanismo de autenticación (token de aplicación vs. token de sesión de usuario). Detalle del contrato de integración [Por definir] con el equipo de ms-domicilios. | |

---

### PED-RF-021 — Validar Existencia del Activo en ms-inventario

> **Justificación:** La validación de existencia del activo en ms-inventario se realiza en múltiples operaciones (crear ítem, recepcionar). Definirla como requisito independiente y reutilizable evita duplicación y centraliza el manejo de errores de integración con ms-inventario.

| | | |
|---|---|---|
| **Código** | PED-RF-021 | |
| **Nombre** | Validar Existencia del Activo en ms-inventario | |
| **Descripción** | Consulta a ms-inventario para verificar que un activo específico existe en el sistema antes de incluirlo en un pedido. Es un proceso interno reutilizable. | |
| **Actores** | ms-inventario [INV], ms-pedidos (proceso interno) | |
| | | |
| **Precondición** | El ID del activo a validar está disponible. | |
| | El Request ID de la operación en curso está disponible. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos invoca a **ms-inventario [INV]** — operación de consulta/verificación de activo — enviando el ID del activo y el Request ID. Se espera como respuesta: confirmación de existencia del activo y sus datos básicos. |
| | 2 | ms-inventario retorna confirmación de que el activo existe. |
| | 3 | El flujo retorna al requisito invocador con el resultado de la validación. |
| | | |
| **Secuencia alterna** | 2A | Si ms-inventario indica que el activo no existe: retornar resultado negativo al requisito invocador. |
| | | |
| **Excepciones** | E1 | Si ms-inventario no responde o devuelve error técnico: propagar el error al requisito invocador para que retorne HTTP 503. |
| | | |
| **Postcondición** | El requisito invocador conoce si el activo existe o no. | |
| | | |
| **Comentarios** | Es un proceso interno reutilizado por [PED-RF-013] y [PED-RF-012]. No expone endpoint propio. | |

---

### PED-RF-022 — Validar Proveedor con Contrato Vigente en ms-proveedores

> **Justificación:** La validación del proveedor y su contrato vigente se invoca en múltiples operaciones (crear pedido, actualizar pedido, avanzar estado). Definirla como requisito reutilizable centraliza la lógica de integración con ms-proveedores y facilita el mantenimiento.

| | | |
|---|---|---|
| **Código** | PED-RF-022 | |
| **Nombre** | Validar Proveedor con Contrato Vigente en ms-proveedores | |
| **Descripción** | Consulta a ms-proveedores para verificar que un proveedor existe en el sistema y tiene un contrato vigente en la fecha actual. Es un proceso interno reutilizable. | |
| **Actores** | ms-proveedores [PRV], ms-pedidos (proceso interno) | |
| | | |
| **Precondición** | El ID o identificador del proveedor a validar está disponible. | |
| | El Request ID de la operación en curso está disponible. | |
| | | |
| | **Paso** | **Descripción** |
| **Secuencia normal** | 1 | ms-pedidos invoca a **ms-proveedores [PRV]** — operación de validación de proveedor y contrato — enviando el ID del proveedor y el Request ID. Se espera como respuesta: confirmación de existencia del proveedor y vigencia de su contrato. |
| | 2 | ms-proveedores retorna confirmación de que el proveedor existe y tiene contrato vigente. |
| | 3 | El flujo retorna al requisito invocador con el resultado de la validación. |
| | | |
| **Secuencia alterna** | 2A | Si el proveedor no existe o su contrato no está vigente: retornar resultado negativo al requisito invocador. |
| | | |
| **Excepciones** | E1 | Si ms-proveedores no responde o devuelve error técnico: propagar el error al requisito invocador para que retorne HTTP 503. |
| | | |
| **Postcondición** | El requisito invocador conoce si el proveedor existe y tiene contrato vigente. | |
| | | |
| **Comentarios** | Es un proceso interno reutilizado por [PED-RF-006], [PED-RF-009] y [PED-RF-010]. No expone endpoint propio. Regla de negocio RN-08. | |

---

*Documento generado a partir de: ms-pedidos_PED_extraccion.md — ERP Universitario, Propuesta de Arquitectura y Requisitos Funcionales v1.0, Febrero 2026.*
