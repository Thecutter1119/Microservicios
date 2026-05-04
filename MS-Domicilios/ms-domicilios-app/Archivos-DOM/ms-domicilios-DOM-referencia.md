# Documento de Referencia — ms-domicilios [DOM]

| Campo | Detalle |
|---|---|
| **Microservicio** | ms-domicilios |
| **Código** | DOM |
| **Módulo** | Módulo 4 — Logística y Proveedores |
| **Documento base** | ERP Universitario — Propuesta de Arquitectura y Requisitos Funcionales v1.0 |
| **Fecha del documento base** | Febrero 2026 |

---

## 1. Extracción Textual

### 1.1 Sección propia del microservicio (§7.11 ms-domicilios [DOM])

> **Propósito:** Gestiona las entregas a domicilio, la asignación de repartidores, el seguimiento en tiempo real de las rutas y la calificación del servicio de entrega.

#### Información que gestiona

> **Entregas:** Cada entrega programada. Se requiere almacenar: el pedido que origina la entrega, el repartidor asignado, la dirección de origen, la dirección de destino, el estado (asignada, en camino, entregada, fallida o devuelta), la fecha de asignación, la fecha de recogida, la fecha de entrega, el costo del envío y observaciones. Se debe registrar la fecha de creación y de actualización.

> **Repartidores:** Información de cada repartidor disponible. Se requiere almacenar: el usuario asociado, nombre, teléfono, tipo de vehículo, placa del vehículo, el estado (disponible, en ruta o inactivo), la zona de cobertura y la calificación promedio actual. Se debe registrar la fecha de registro y de actualización.

> **Seguimiento:** Puntos de rastreo de cada entrega. Se requiere almacenar: la entrega, el estado en ese punto, la latitud, la longitud, la fecha y hora y una nota descriptiva.

> **Calificaciones:** Evaluación del servicio de cada entrega. Se requiere almacenar: la entrega calificada, quién calificó, la puntuación (de 1 a 5), un comentario y la fecha.

#### Requisitos funcionales

> - El sistema debe permitir crear, consultar y actualizar entregas.
> - El sistema debe permitir actualizar el estado de una entrega y debe generar automáticamente un punto de seguimiento con cada cambio de estado.
> - El sistema debe permitir asignar un repartidor a una entrega, validando que el repartidor esté disponible y que su zona de cobertura corresponda con la dirección de destino.
> - El sistema debe permitir crear, consultar y actualizar repartidores, así como listar los repartidores disponibles filtrados por zona de cobertura.
> - El sistema debe permitir consultar el historial completo de seguimiento de una entrega.
> - El sistema debe permitir registrar puntos de seguimiento con coordenadas geográficas durante el transcurso de una entrega.
> - El sistema debe permitir calificar una entrega únicamente cuando se encuentre en estado "entregada". No se permite calificar entregas en curso o fallidas.
> - El sistema debe calcular y mantener actualizada la calificación promedio de cada repartidor basándose en todas las calificaciones recibidas.
> - El sistema debe calcular el costo de envío basándose en una tarifa fija configurable o en un cálculo simplificado por distancia.

#### Dependencias con otros servicios

> - Debe consultar al servicio de pedidos para obtener los datos del pedido asociado a la entrega.
> - Debe enviar notificaciones a través del servicio de notificaciones al solicitante cuando el estado de su entrega cambie.
> - Debe enviar registros de log al servicio de auditoría de forma asíncrona con cada operación realizada.

---

### 1.2 Mención en el Mapa de Dependencias (§8)

> | ms-domicilios | ms-pedidos, ms-notificaciones |

---

### 1.3 Reglas Transversales del Sistema (§6) — Aplicables a ms-domicilios

> **6.1 Validación de Sesión Obligatoria**
> Toda operación realizada por un usuario a través de cualquier microservicio debe ser precedida por una validación de sesión activa. El microservicio que recibe la petición del usuario debe consultar al servicio de autenticación para confirmar que la sesión es válida antes de ejecutar cualquier lógica de negocio. Si la sesión no es válida, el sistema debe rechazar la petición inmediatamente sin procesarla.

> **6.2 Validación de Permisos por Funcionalidad**
> Cada funcionalidad del sistema tiene asociado un código de permiso único. Después de validar la sesión, el microservicio debe consultar al servicio de roles para verificar que el rol del usuario tiene autorización para ejecutar la funcionalidad solicitada. Si el usuario no tiene el permiso correspondiente, el sistema debe rechazar la petición.

> **6.3 Tokens de Aplicación para Comunicación entre Servicios**
> Cada microservicio posee un token de aplicación único que lo identifica ante los demás servicios. Este token es fijo (no expira ni se renueva automáticamente) y solo puede ser actualizado de forma manual por un administrador. Los tokens se almacenan cifrados con AES-256 y se transmiten cifrados en cada petición entre servicios. Cualquier microservicio puede comunicarse con cualquier otro siempre que posea un token activo y válido.

> **6.5 Trazabilidad Distribuida (Request ID)**
> Cada petición que ingresa al sistema recibe un identificador único de rastreo con el formato: código del servicio que la recibe, seguido de un timestamp Unix y un identificador corto aleatorio (ejemplo: `PED-1740000000-a3f8b2`). Este identificador se propaga a todos los microservicios que participan en el procesamiento de la petición. Si un servicio recibe una petición que ya trae un identificador de rastreo (porque proviene de otro servicio), debe reutilizarlo en lugar de generar uno nuevo. Toda respuesta del sistema, independientemente de si la operación fue exitosa o fallida, debe incluir este identificador tanto en las cabeceras como en el cuerpo de la respuesta.

> **6.6 Auditoría y Logs en Formato JSON**
> Cada operación realizada en cualquier microservicio debe generar un registro de log en formato JSON que contenga: la fecha y hora de la operación, el identificador de rastreo de la petición, el nombre del microservicio, la funcionalidad ejecutada, el método utilizado, el código de respuesta, la duración en milisegundos, el identificador del usuario que realizó la operación y un detalle descriptivo. Estos registros se envían de forma asíncrona al servicio de auditoría, de manera que el envío no bloquee ni retrase la respuesta al usuario. Si el envío al servicio de auditoría falla, el microservicio debe continuar operando normalmente.

> **6.7 Estructura de Respuesta Estándar**
> Todas las respuestas del sistema deben seguir una estructura uniforme que incluya: el identificador de rastreo de la petición, un indicador de éxito o error, los datos resultantes de la operación, un mensaje descriptivo y la fecha y hora de la respuesta.

---

### 1.4 Menciones desde otros microservicios

No se encontraron menciones directas de ms-domicilios [DOM] en las secciones de otros microservicios del documento. ms-domicilios no es listado como dependencia por ningún otro servicio en el mapa de dependencias (§8).

---

## 2. Información General

| Campo | Detalle |
|---|---|
| **Nombre** | ms-domicilios |
| **Código** | DOM |
| **Módulo** | Módulo 4 — Logística y Proveedores |
| **Tecnología** | FastAPI + Python + PostgreSQL |

**Propósito:** ms-domicilios es el servicio encargado de gestionar el ciclo completo de entregas a domicilio de la institución, desde la asignación de un repartidor hasta la calificación final del servicio. Administra la información de los repartidores, registra los puntos de seguimiento geográfico en tiempo real y controla los estados de cada entrega.

**Rol dentro del sistema:** Actúa como el componente de ejecución logística del módulo de Logística y Proveedores. Recibe como insumo los pedidos gestionados por ms-pedidos y se encarga de la fase de distribución física, notificando a los solicitantes sobre el avance de sus entregas mediante ms-notificaciones.

---

## 3. Reglas de Negocio

### 3.1 Reglas Transversales (aplican a todos los microservicios)

1. Toda operación debe estar precedida por una **validación de sesión activa** consultando a ms-autenticacion. Si la sesión es inválida, la petición se rechaza sin procesar ninguna lógica de negocio.
2. Después de validar la sesión, se debe **validar el permiso** correspondiente a la funcionalidad solicitada consultando a ms-roles. Si el usuario no tiene el permiso, la petición se rechaza.
3. Toda comunicación entre servicios debe incluir el **token de aplicación** del microservicio emisor, transmitido cifrado con AES-256. El token es fijo y solo puede actualizarse manualmente por un administrador.
4. Cada petición entrante debe generar o reutilizar un **Request ID** con formato `DOM-{timestamp Unix}-{id corto aleatorio}`. Si la petición ya trae un identificador de rastreo de otro servicio, debe reutilizarse. El Request ID debe incluirse en cabeceras y cuerpo de toda respuesta.
5. Cada operación debe generar un **registro de log en formato JSON** con: fecha/hora, Request ID, nombre del microservicio, funcionalidad ejecutada, método, código de respuesta, duración en ms, ID de usuario y detalle descriptivo. El envío al servicio de auditoría es asíncrono (fire-and-forget); si falla, el servicio continúa operando normalmente.
6. Todas las respuestas deben cumplir la **estructura estándar**: Request ID, indicador éxito/error, datos, mensaje descriptivo y fecha/hora de la respuesta.

### 3.2 Reglas Específicas del Microservicio

7. Un repartidor solo puede ser asignado a una entrega si su **estado es "disponible"**.
8. Al asignar un repartidor, se debe validar que su **zona de cobertura** corresponde con la dirección de destino de la entrega.
9. Cada vez que el estado de una entrega cambia, el sistema debe **generar automáticamente un punto de seguimiento** asociado a ese cambio de estado.
10. Solo se permite **calificar una entrega** cuando su estado sea "entregada". No se permite calificar entregas en curso o en estado fallida/devuelta.
11. La **calificación promedio del repartidor** debe mantenerse actualizada automáticamente tras cada nueva calificación recibida, calculándose sobre la totalidad de sus calificaciones históricas.
12. La **puntuación de calificación** debe estar en el rango de 1 a 5.
13. El **costo de envío** se calcula con base en una tarifa fija configurable o mediante un cálculo simplificado por distancia.
14. Los estados válidos de una entrega son: **asignada → en camino → entregada**. También puede transicionar a **fallida** o **devuelta** en caso de incidencia.
15. Los estados válidos de un repartidor son: **disponible**, **en ruta** e **inactivo**.

### 3.3 Reglas derivadas de dependencias con otros servicios

16. Antes de crear o procesar una entrega, se deben obtener los datos del pedido consultando a **ms-pedidos**. El pedido debe existir para poder crear la entrega asociada.
17. Cuando el estado de una entrega cambia, se debe enviar una **notificación automática** al solicitante del pedido a través de **ms-notificaciones**.

---

## 4. Entidades y Datos

### 4.1 Entregas

> Cada entrega programada. Se requiere almacenar: el pedido que origina la entrega, el repartidor asignado, la dirección de origen, la dirección de destino, el estado (asignada, en camino, entregada, fallida o devuelta), la fecha de asignación, la fecha de recogida, la fecha de entrega, el costo del envío y observaciones. Se debe registrar la fecha de creación y de actualización.

| Atributo | Descripción |
|---|---|
| pedido | Referencia al pedido que origina la entrega |
| repartidor_asignado | Repartidor responsable de la entrega |
| direccion_origen | Dirección desde la que se recoge el paquete |
| direccion_destino | Dirección a la que se realiza la entrega |
| estado | Estado actual: asignada, en camino, entregada, fallida o devuelta |
| fecha_asignacion | Fecha en que se asignó el repartidor |
| fecha_recogida | Fecha en que se realizó la recogida |
| fecha_entrega | Fecha en que se completó la entrega |
| costo_envio | Costo calculado del envío |
| observaciones | Notas adicionales sobre la entrega |
| fecha_creacion | Fecha de creación del registro |
| fecha_actualizacion | Fecha de la última actualización del registro |

---

### 4.2 Repartidores

> Información de cada repartidor disponible. Se requiere almacenar: el usuario asociado, nombre, teléfono, tipo de vehículo, placa del vehículo, el estado (disponible, en ruta o inactivo), la zona de cobertura y la calificación promedio actual. Se debe registrar la fecha de registro y de actualización.

| Atributo | Descripción |
|---|---|
| usuario | Referencia al usuario del sistema asociado al repartidor |
| nombre | Nombre del repartidor |
| telefono | Teléfono de contacto |
| tipo_vehiculo | Tipo de vehículo utilizado para las entregas |
| placa_vehiculo | Placa del vehículo |
| estado | Estado actual: disponible, en ruta o inactivo |
| zona_cobertura | Zona geográfica en la que opera el repartidor |
| calificacion_promedio | Promedio actual de todas las calificaciones recibidas |
| fecha_registro | Fecha de registro del repartidor |
| fecha_actualizacion | Fecha de la última actualización del registro |

---

### 4.3 Seguimiento

> Puntos de rastreo de cada entrega. Se requiere almacenar: la entrega, el estado en ese punto, la latitud, la longitud, la fecha y hora y una nota descriptiva.

| Atributo | Descripción |
|---|---|
| entrega | Referencia a la entrega que se está rastreando |
| estado | Estado de la entrega en este punto de rastreo |
| latitud | Coordenada de latitud geográfica |
| longitud | Coordenada de longitud geográfica |
| fecha_hora | Fecha y hora del punto de seguimiento |
| nota | Nota descriptiva del evento de seguimiento |

---

### 4.4 Calificaciones

> Evaluación del servicio de cada entrega. Se requiere almacenar: la entrega calificada, quién calificó, la puntuación (de 1 a 5), un comentario y la fecha.

| Atributo | Descripción |
|---|---|
| entrega | Referencia a la entrega calificada |
| calificador | Usuario que realizó la calificación |
| puntuacion | Puntuación del servicio (rango: 1 a 5) |
| comentario | Comentario descriptivo de la calificación |
| fecha | Fecha en que se registró la calificación |

---

## 5. Funcionalidades Requeridas

> - El sistema debe permitir crear, consultar y actualizar entregas.
> - El sistema debe permitir actualizar el estado de una entrega y debe generar automáticamente un punto de seguimiento con cada cambio de estado.
> - El sistema debe permitir asignar un repartidor a una entrega, validando que el repartidor esté disponible y que su zona de cobertura corresponda con la dirección de destino.
> - El sistema debe permitir crear, consultar y actualizar repartidores, así como listar los repartidores disponibles filtrados por zona de cobertura.
> - El sistema debe permitir consultar el historial completo de seguimiento de una entrega.
> - El sistema debe permitir registrar puntos de seguimiento con coordenadas geográficas durante el transcurso de una entrega.
> - El sistema debe permitir calificar una entrega únicamente cuando se encuentre en estado "entregada". No se permite calificar entregas en curso o fallidas.
> - El sistema debe calcular y mantener actualizada la calificación promedio de cada repartidor basándose en todas las calificaciones recibidas.
> - El sistema debe calcular el costo de envío basándose en una tarifa fija configurable o en un cálculo simplificado por distancia.

---

## 6. Dependencias (de quién dependo)

| Microservicio | Información / Funcionalidad consumida | Momento / Contexto |
|---|---|---|
| **ms-pedidos [PED]** | Datos del pedido asociado a la entrega (solicitante, ítems, proveedor, estado) | Al crear una entrega o al necesitar información del pedido de origen |
| **ms-notificaciones [NOT]** | Envío de notificaciones al solicitante del pedido | Cada vez que el estado de una entrega cambia |
| **ms-autenticacion [AUTH]** | Validación de sesión activa del usuario | Antes de ejecutar cualquier operación (transversal) |
| **ms-roles [ROL]** | Validación de permisos por funcionalidad | Después de validar la sesión, antes de ejecutar la lógica (transversal) |
| **ms-auditoria [AUD]** | Registro de logs de operaciones en formato JSON | De forma asíncrona tras cada operación ejecutada (transversal) |

---

## 7. Consumidores (quién depende de mí)

Según el documento de requisitos y el mapa de dependencias (§8), **ningún otro microservicio del sistema declara depender de ms-domicilios [DOM]**. Este servicio es un consumidor final dentro del flujo logístico: recibe datos de ms-pedidos y entrega resultados al usuario final a través de notificaciones, pero no expone datos que otros servicios del sistema necesiten consumir.

No se encontró información relevante en el documento que indique consumidores de este microservicio.
