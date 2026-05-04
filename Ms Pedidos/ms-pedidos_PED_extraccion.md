# Extracción de Requisitos — ms-pedidos [PED]

**Proyecto:** ERP Universitario — Universidad del Valle, Sede Caicedonia  
**Asignatura:** Desarrollo de Software III (750027C)  
**Documento fuente:** Propuesta de Arquitectura y Requisitos Funcionales v1.0  
**Fecha:** Febrero 2026  

---

## 1. Extracción Textual

A continuación se transcriben, sin modificación, todos los fragmentos del documento original relevantes para `ms-pedidos [PED]`.

---

### 1.1 Sección principal — Módulo 4: Logística y Proveedores › 7.10 ms-pedidos [PED]

> **7.10 ms-pedidos [PED]**
>
> **Propósito:** Gestiona los pedidos internos y las órdenes de compra de la institución. Controla el flujo completo desde la creación del pedido en borrador hasta la recepción de los bienes, incluyendo la posibilidad de recepciones parciales.
>
> **Información que gestiona**
>
> Pedidos: Cada orden de compra o pedido interno. Se requiere almacenar: un número de pedido único, el solicitante, el proveedor asignado, el estado (borrador, enviado, aprobado, en proceso, recibido parcial, recibido o cancelado), la fecha de solicitud, la fecha de aprobación, la fecha de recepción, el monto total y observaciones. Se debe registrar la fecha de creación y de actualización.
>
> Ítems de pedido: Cada línea de detalle dentro de un pedido. Se requiere almacenar: el pedido al que pertenece, el activo solicitado, una descripción, la cantidad solicitada, la cantidad recibida hasta el momento, el valor unitario, el subtotal de la línea y el estado del ítem (pendiente, recibido parcial o recibido).
>
> Historial de estados del pedido: Registro de cada cambio de estado del pedido. Se requiere almacenar: el pedido, el estado anterior, el nuevo estado, quién realizó el cambio, la fecha y hora del cambio y un comentario.
>
> **Requisitos funcionales**
>
> - El sistema debe permitir crear, consultar y actualizar pedidos. Un pedido solo puede ser modificado mientras se encuentre en estado "borrador".
> - El sistema debe implementar un flujo de estados: borrador → enviado → aprobado → en proceso → recibido. Cada cambio de estado debe quedar registrado en el historial con la fecha, el usuario y un comentario.
> - El sistema debe permitir cancelar un pedido en cualquier estado previo a "recibido", registrando el motivo de la cancelación.
> - El sistema debe permitir registrar recepciones parciales: recibir una cantidad menor a la solicitada por cada ítem. El estado del ítem y del pedido debe actualizarse automáticamente según corresponda.
> - El sistema debe permitir agregar, actualizar y remover ítems de un pedido mientras esté en estado borrador.
> - El sistema debe calcular automáticamente el monto total del pedido como la suma de cantidad solicitada por valor unitario de cada ítem.
> - El sistema debe permitir consultar el historial completo de cambios de estado de un pedido.
>
> **Dependencias con otros servicios**
>
> - Debe consultar al servicio de inventario para verificar que los activos solicitados existen y para registrar la entrada de stock al momento de la recepción.
> - Debe consultar al servicio de proveedores para validar que el proveedor existe y tiene un contrato vigente.
> - Debe enviar registros de log al servicio de auditoría de forma asíncrona con cada operación realizada.

---

### 1.2 Mención en la Arquitectura General — Módulo 4

> **Módulo 4 — Logística y Proveedores**  
> Responsable de pedidos internos, gestión de entregas y administración de proveedores.
> - ms-pedidos
> - ms-domicilios
> - ms-proveedores

---

### 1.3 Mención en el Mapa de Dependencias — Sección 8

> | Microservicio | Consume datos de |
> |---|---|
> | ms-pedidos | ms-inventario, ms-proveedores |
> | ms-domicilios | ms-pedidos, ms-notificaciones |
>
> Adicionalmente, todos los microservicios (excepto ms-autenticacion y ms-roles entre sí) consumen:
> - ms-autenticacion para validar sesiones activas.
> - ms-roles para validar permisos por funcionalidad.
> - ms-auditoria para enviar registros de log de forma asíncrona.

---

### 1.4 Mención en ms-domicilios [DOM] — Dependencias con otros servicios

> - Debe consultar al servicio de pedidos para obtener los datos del pedido asociado a la entrega.

---

### 1.5 Reglas Transversales — Sección 6 (aplican a todos los microservicios, incluyendo ms-pedidos)

> **6.1 Validación de Sesión Obligatoria**  
> Toda operación realizada por un usuario a través de cualquier microservicio debe ser precedida por una validación de sesión activa. El microservicio que recibe la petición del usuario debe consultar al servicio de autenticación para confirmar que la sesión es válida antes de ejecutar cualquier lógica de negocio. Si la sesión no es válida, el sistema debe rechazar la petición inmediatamente sin procesarla.
>
> **6.2 Validación de Permisos por Funcionalidad**  
> Cada funcionalidad del sistema tiene asociado un código de permiso único. Después de validar la sesión, el microservicio debe consultar al servicio de roles para verificar que el rol del usuario tiene autorización para ejecutar la funcionalidad solicitada. Si el usuario no tiene el permiso correspondiente, el sistema debe rechazar la petición.
>
> **6.3 Tokens de Aplicación para Comunicación entre Servicios**  
> Cada microservicio posee un token de aplicación único que lo identifica ante los demás servicios. Este token es fijo (no expira ni se renueva automáticamente) y solo puede ser actualizado de forma manual por un administrador. Los tokens se almacenan cifrados con AES-256 y se transmiten cifrados en cada petición entre servicios.
>
> **6.5 Trazabilidad Distribuida (Request ID)**  
> Cada petición que ingresa al sistema recibe un identificador único de rastreo con el formato: código del servicio que la recibe, seguido de un timestamp Unix y un identificador corto aleatorio (ejemplo: **PED-1740000000-a3f8b2**). Este identificador se propaga a todos los microservicios que participan en el procesamiento de la petición. Si un servicio recibe una petición que ya trae un identificador de rastreo (porque proviene de otro servicio), debe reutilizarlo en lugar de generar uno nuevo. Toda respuesta del sistema, independientemente de si la operación fue exitosa o fallida, debe incluir este identificador tanto en las cabeceras como en el cuerpo de la respuesta.
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
| **Nombre** | ms-pedidos |
| **Código** | PED |
| **Módulo** | Módulo 4 — Logística y Proveedores |
| **Stack** | FastAPI + Python + PostgreSQL |

**Propósito:**  
`ms-pedidos` gestiona los pedidos internos y órdenes de compra de la institución, controlando el ciclo de vida completo desde la creación en borrador hasta la recepción de los bienes. Soporta recepciones parciales por ítem y mantiene un historial completo de cambios de estado.

**Rol en el sistema:**  
Es el punto de partida del flujo logístico. Coordina con `ms-inventario` para verificar activos y registrar entradas de stock, y con `ms-proveedores` para validar contratos vigentes. A su vez, `ms-domicilios` lo consume para obtener los datos del pedido al gestionar entregas.

---

## 3. Reglas de Negocio

### 3.1 Reglas Transversales del Sistema

| # | Regla |
|---|---|
| RT-01 | Toda operación debe ir precedida de una validación de sesión activa consultando a `ms-autenticacion`. Si la sesión no es válida, la petición debe rechazarse inmediatamente. |
| RT-02 | Tras validar la sesión, debe consultarse a `ms-roles` para verificar que el rol del usuario tiene el permiso asociado a la funcionalidad solicitada. Si no tiene permiso, la petición se rechaza. |
| RT-03 | El microservicio posee un token de aplicación único (cifrado con AES-256) que lo identifica ante los demás servicios. Este token no expira y solo puede ser actualizado manualmente por un administrador. |
| RT-04 | Cada petición entrante debe generar un Request ID con formato `PED-{timestamp_unix}-{id_corto_aleatorio}`. Si la petición ya trae un Request ID de otro servicio, debe reutilizarse. El Request ID debe incluirse en cabeceras y cuerpo de toda respuesta. |
| RT-05 | Cada operación debe generar un registro de log en formato JSON (fecha/hora, Request ID, microservicio, funcionalidad, método, código de respuesta, duración en ms, usuario, detalle) y enviarlo de forma asíncrona a `ms-auditoria`. Si el envío falla, el microservicio debe continuar operando con normalidad. |
| RT-06 | Todas las respuestas deben seguir la estructura estándar: Request ID, indicador de éxito/error, datos, mensaje descriptivo y fecha/hora de la respuesta. |

### 3.2 Reglas Específicas de ms-pedidos

| # | Regla |
|---|---|
| RN-01 | Un pedido solo puede ser modificado (actualización de datos o de ítems) mientras se encuentre en estado **borrador**. |
| RN-02 | El flujo de estados es estricto y secuencial: **borrador → enviado → aprobado → en proceso → recibido**. No se permite saltar estados. |
| RN-03 | Cada cambio de estado debe quedar registrado en el historial con: el estado anterior, el nuevo estado, el usuario que realizó el cambio, la fecha/hora y un comentario. |
| RN-04 | Un pedido puede cancelarse en cualquier estado previo a **"recibido"**. La cancelación debe registrar el motivo. |
| RN-05 | Se permiten recepciones parciales: es posible recibir una cantidad menor a la solicitada por ítem. El estado del ítem y del pedido deben actualizarse automáticamente según la cantidad recibida. |
| RN-06 | Los ítems de un pedido solo pueden agregarse, actualizarse o removerse mientras el pedido esté en estado **borrador**. |
| RN-07 | El monto total del pedido debe calcularse automáticamente como la sumatoria de (cantidad solicitada × valor unitario) de cada ítem. |
| RN-08 | No se puede aprobar ni procesar un pedido con un proveedor cuyo contrato no esté vigente (validación contra `ms-proveedores`). |
| RN-09 | Al recepcionar un pedido (total o parcialmente), debe registrarse la entrada de stock en `ms-inventario`. |

---

## 4. Entidades y Datos

### 4.1 Pedidos

**Propósito:** Representa cada orden de compra o pedido interno generado por la institución.

**Atributos requeridos:**

| Atributo | Descripción |
|---|---|
| Número de pedido | Único, identifica al pedido en el sistema |
| Solicitante | Usuario que generó el pedido |
| Proveedor asignado | Proveedor al que se dirige el pedido |
| Estado | borrador, enviado, aprobado, en proceso, recibido parcial, recibido o cancelado |
| Fecha de solicitud | Fecha en que se creó el pedido |
| Fecha de aprobación | Fecha en que el pedido fue aprobado |
| Fecha de recepción | Fecha en que los bienes fueron recibidos |
| Monto total | Calculado automáticamente a partir de los ítems |
| Observaciones | Notas adicionales sobre el pedido |
| Fecha de creación | Registro automático al crear el pedido |
| Fecha de actualización | Registro automático en cada modificación |

---

### 4.2 Ítems de Pedido

**Propósito:** Representa cada línea de detalle dentro de un pedido, indicando el activo solicitado y las cantidades.

**Atributos requeridos:**

| Atributo | Descripción |
|---|---|
| Pedido | Referencia al pedido al que pertenece |
| Activo solicitado | Referencia al activo del inventario |
| Descripción | Descripción del ítem |
| Cantidad solicitada | Unidades pedidas al proveedor |
| Cantidad recibida | Unidades efectivamente recibidas hasta el momento |
| Valor unitario | Precio por unidad del activo |
| Subtotal de la línea | Calculado como cantidad solicitada × valor unitario |
| Estado del ítem | pendiente, recibido parcial o recibido |

---

### 4.3 Historial de Estados del Pedido

**Propósito:** Registra cada cambio de estado ocurrido en un pedido para garantizar trazabilidad y auditoría del flujo logístico.

**Atributos requeridos:**

| Atributo | Descripción |
|---|---|
| Pedido | Referencia al pedido afectado |
| Estado anterior | Estado previo al cambio |
| Nuevo estado | Estado resultante del cambio |
| Usuario | Quién realizó el cambio |
| Fecha y hora del cambio | Timestamp del momento del cambio |
| Comentario | Observación o motivo del cambio de estado |

---

## 5. Funcionalidades Requeridas

> *(Transcripción exacta del documento original)*

- El sistema debe permitir crear, consultar y actualizar pedidos. Un pedido solo puede ser modificado mientras se encuentre en estado "borrador".
- El sistema debe implementar un flujo de estados: borrador → enviado → aprobado → en proceso → recibido. Cada cambio de estado debe quedar registrado en el historial con la fecha, el usuario y un comentario.
- El sistema debe permitir cancelar un pedido en cualquier estado previo a "recibido", registrando el motivo de la cancelación.
- El sistema debe permitir registrar recepciones parciales: recibir una cantidad menor a la solicitada por cada ítem. El estado del ítem y del pedido debe actualizarse automáticamente según corresponda.
- El sistema debe permitir agregar, actualizar y remover ítems de un pedido mientras esté en estado borrador.
- El sistema debe calcular automáticamente el monto total del pedido como la suma de cantidad solicitada por valor unitario de cada ítem.
- El sistema debe permitir consultar el historial completo de cambios de estado de un pedido.

---

## 6. Dependencias (de quién dependo)

Servicios que `ms-pedidos` consume directamente:

| Microservicio | Qué consume | Cuándo se consulta |
|---|---|---|
| **ms-inventario [INV]** | Verificación de existencia del activo solicitado / Registro de entrada de stock | Al crear un ítem de pedido (para validar que el activo existe) y al recepcionar el pedido (para registrar la entrada de stock) |
| **ms-proveedores [PRV]** | Validación de existencia del proveedor y vigencia de su contrato | Al crear o enviar un pedido, para asegurar que el proveedor tiene contrato vigente |
| **ms-autenticacion [AUTH]** | Validación de sesión activa del usuario | Antes de ejecutar cualquier operación (regla transversal RT-01) |
| **ms-roles [ROL]** | Validación de permisos del usuario por funcionalidad | Después de validar sesión, antes de ejecutar la lógica de negocio (regla transversal RT-02) |
| **ms-auditoria [AUD]** | Envío de registros de log en formato JSON | De forma asíncrona tras cada operación realizada (regla transversal RT-05) |

---

## 7. Consumidores (quién depende de mí)

Servicios que consumen datos o funcionalidades de `ms-pedidos`:

| Microservicio | Qué consume | Cuándo lo consulta |
|---|---|---|
| **ms-domicilios [DOM]** | Datos del pedido asociado a una entrega | Al crear o gestionar una entrega, para obtener la información del pedido de origen |

> **Nota:** Adicionalmente, según las reglas transversales, `ms-pedidos` expone sus funcionalidades a cualquier usuario autenticado con los permisos correspondientes, a través de los flujos de operación estándar del sistema.

---

*Documento generado a partir de: ERP Universitario — Propuesta de Arquitectura y Requisitos Funcionales v1.0, Febrero 2026.*
