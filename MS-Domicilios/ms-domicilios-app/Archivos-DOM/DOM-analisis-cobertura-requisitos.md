# Análisis de Cobertura de Requisitos — ms-domicilios [DOM]

| Campo | Detalle |
|---|---|
| **Microservicio** | ms-domicilios |
| **Código** | DOM |
| **Módulo** | Módulo 4 — Logística y Proveedores |
| **Documentos analizados** | Requisitos Funcionales v1.0 · Diseño de Integración v1.0 · Especificación de API REST v1.0 |
| **Fecha del análisis** | Marzo 2026 |

---

## Tabla de Contenido

1. [Tabla de Cobertura](#1-tabla-de-cobertura)
2. [Análisis de Cobertura](#2-análisis-de-cobertura)
   - [Resumen cuantitativo](#21-resumen-cuantitativo)
   - [Hallazgos por documento](#22-hallazgos-por-documento)
   - [Recomendaciones prioritarias](#23-recomendaciones-prioritarias)

---

## 1. Tabla de Cobertura

> **Leyenda:** ✅ Cubierto · ⚠️ Cubierto parcialmente · ❌ No cubierto

### Categoría 1 — Requisitos Transversales

| Req. | Nombre | Arquitecto de Integración | Ingeniero de Software (API) | Estado |
|---|---|---|---|---|
| **DOM-RF-001** | Validación de Sesión Activa | ✅ Sección 3.1 — contrato completo con AUTH (request/response, timeouts, manejo de 401/503) + Sección 2 (mapa de integraciones) + Diagramas 8.1, 8.2, 8.3 | ✅ Cabeceras comunes (Sec. 4) + todos los diagramas de secuencia internos (Sec. 5.x) muestran la llamada a AUTH | **Completo** |
| **DOM-RF-002** | Validación de Permisos por Funcionalidad | ✅ Sección 3.2 — contrato completo con ROL (query params, respuestas 200/403/503) + Sección 2 + Diagramas 8.x | ✅ Todos los diagramas 5.x muestran la llamada a ROL con el permiso específico (ej. `DOM_CREAR_ENTREGA`, `DOM_ASIGNAR_REPARTIDOR`) | **Completo** |
| **DOM-RF-003** | Generación y Propagación de Request ID | ✅ Sección 6 — flujo completo: formato `DOM-{timestamp}-{shortid}`, reutilización si ya existe, propagación en cabeceras salientes | ✅ Sección 4, cabeceras comunes + todos los diagramas 5.x muestran el `X-Request-ID` en requests y responses | **Completo** |
| **DOM-RF-004** | Registro de Auditoría Asíncrono | ✅ Sección 7 — flujo completo fire-and-forget, contrato con AUD en Sec. 3.5 + Diagrama 8.4 con fallback a log local | ✅ Todos los diagramas 5.x incluyen el paso async a AUD (`DOM-)AUD`) | **Completo** |
| **DOM-RF-005** | Estructura de Respuesta Estándar | ⚠️ Implícita en todos los ejemplos de respuesta JSON (Secs. 3.1–3.5, 4.x), pero **no existe una sección dedicada** que declare el esquema uniforme | ✅ Sección 4 declara la estructura uniforme con `request_id`, `success`, `data`, `message`, `timestamp`; todos los endpoints la implementan | **Parcial** |

### Categoría 2 — Requisitos por Entidad: Repartidores

| Req. | Nombre | Arquitecto de Integración | Ingeniero de Software (API) | Estado |
|---|---|---|---|---|
| **DOM-RF-006** | Crear Repartidor | ✅ Sección 4.1 — contrato entrante con request/response, incluyendo manejo de HTTP 409 (placa duplicada) | ✅ Sec. 4.1 + Sec. 5.1 — diagrama de secuencia completo con validación, INSERT y auditoría | **Completo** |
| **DOM-RF-007** | Consultar Repartidor por ID | ✅ Sección 4.1 — contrato entrante con GET y ejemplos de 200/404 | ✅ Sec. 4.1 + Sec. 5.2 — diagrama de secuencia con SELECT y respuesta | **Completo** |
| **DOM-RF-008** | Actualizar Repartidor | ✅ Sección 4.1 — contrato entrante con PUT, ejemplos de 200/404/409 | ✅ Sec. 4.1 + Sec. 5.3 — diagrama con validación de placa y UPDATE | **Completo** |
| **DOM-RF-009** | Listar Repartidores Disponibles por Zona | ✅ Sección 4.1 — contrato GET con query param `zona_cobertura`, ejemplo de respuesta en lista | ✅ Sec. 4.1 + Sec. 5.4 — diagrama con filtro por zona y estado `disponible` | **Completo** |

### Categoría 2 — Requisitos por Entidad: Entregas

| Req. | Nombre | Arquitecto de Integración | Ingeniero de Software (API) | Estado |
|---|---|---|---|---|
| **DOM-RF-010** | Crear Entrega | ✅ Sec. 3.3 (contrato con PED) + Sec. 4.2 (contrato entrante) + Diagrama 8.1 Fase 1 — cálculo de costo, consulta a ms-pedidos, verificación de duplicados | ✅ Sec. 4.2 + Sec. 5.7 — diagrama detallado con llamada a PED, cálculo de costo e INSERT | **Completo** |
| **DOM-RF-011** | Consultar Entrega por ID | ✅ Sección 4.2 — contrato GET con ejemplos de 200/404 | ✅ Sec. 4.2 + Sec. 5.8 — diagrama con SELECT y respuesta | **Completo** |
| **DOM-RF-012** | Actualizar Datos de Entrega | ✅ Sección 4.2 — contrato PUT, respuestas 200/404/422 | ✅ Sec. 4.2 + Sec. 5.9 — diagrama con validación de campos editables y UPDATE | **Completo** |
| **DOM-RF-013** | Asignar Repartidor a Entrega | ✅ Sec. 3.4 (contrato NOT para notificación) + Sec. 4.2 + Diagrama 8.1 Fase 2 — validación de zona, cambio de estado del repartidor, notificación | ✅ Sec. 4.2 + Sec. 5.10 — diagrama completo con validación de disponibilidad, zona y estado `en_ruta` | **Completo** |
| **DOM-RF-014** | Actualizar Estado de Entrega | ✅ Sec. 3.4 (contrato NOT) + Sec. 4.2 + Diagrama 8.3 — manejo de timeout de NOT, fallback a log, liberación de repartidor | ✅ Sec. 4.2 + Sec. 5.11 — diagrama con transiciones, punto de seguimiento automático y liberación de repartidor | **Completo** |

### Categoría 2 — Requisitos por Entidad: Seguimiento

| Req. | Nombre | Arquitecto de Integración | Ingeniero de Software (API) | Estado |
|---|---|---|---|---|
| **DOM-RF-015** | Registrar Punto de Seguimiento Manual | ⚠️ Mencionado en Sec. 4.3 como contrato entrante (request/response), pero **sin diagrama de secuencia propio en Sec. 8** | ✅ Sec. 4.3 + Sec. 5.13 — diagrama completo con validación de estado `en_camino` y coordenadas | **Parcial** |
| **DOM-RF-016** | Consultar Historial de Seguimiento | ✅ Sec. 4.3 (contrato entrante) + Diagrama 8.2 — flujo completo mostrando que no usa ms-pedidos ni ms-notificaciones | ✅ Sec. 4.3 + Sec. 5.14 — diagrama con consulta ordenada y lista vacía | **Completo** |

### Categoría 2 — Requisitos por Entidad: Calificaciones

| Req. | Nombre | Arquitecto de Integración | Ingeniero de Software (API) | Estado |
|---|---|---|---|---|
| **DOM-RF-017** | Registrar Calificación de Entrega | ✅ Sección 4.4 — contrato entrante con request/response; Diagrama 8.4 lo referencia como ejemplo de auditoría asíncrona | ✅ Sec. 4.4 + Sec. 5.15 — diagrama completo con anti-duplicado, recálculo de promedio y UPDATE en repartidor | **Completo** |

### Categoría 3 — Requisitos Sugeridos

| Req. | Nombre | Arquitecto de Integración | Ingeniero de Software (API) | Estado |
|---|---|---|---|---|
| **DOM-RF-018** | Listar Entregas con Filtros | ❌ No aparece en ningún contrato ni diagrama del documento de integración | ✅ Catálogo Sec. 3 (`GET /api/v1/entregas`), Sec. 4.2 + Sec. 5.12 — diagrama con filtros y paginación | **Parcial** |
| **DOM-RF-019** | Calcular Costo de Envío | ⚠️ Mencionado narrativamente en Diagrama 8.1 Fase 1 ("calcula el costo de envío"), pero **sin contrato ni sección dedicada**; se trata como detalle interno | ⚠️ Referenciado dentro del diagrama 5.7 (Crear Entrega) como paso interno, pero **sin endpoint ni diagrama propio**; se documenta solo como sub-proceso | **Parcial** |
| **DOM-RF-020** | Consultar Calificaciones de un Repartidor | ❌ No aparece en ningún contrato ni sección del documento de integración | ✅ Catálogo Sec. 3 (`GET /api/v1/repartidores/{id}/calificaciones`), Sec. 4.1 + Sec. 5.6 — diagrama con historial y promedio | **Parcial** |
| **DOM-RF-021** | Cambiar Estado de Repartidor | ❌ No aparece en ningún contrato ni sección del documento de integración | ✅ Catálogo Sec. 3 (`PATCH /api/v1/repartidores/{id}/estado`), Sec. 4.1 + Sec. 5.5 — diagrama con restricción de entregas activas | **Parcial** |

---

## 2. Análisis de Cobertura

### 2.1 Resumen cuantitativo

| Estado | Cantidad | Porcentaje |
|---|---|---|
| ✅ Completo | 14 | 67 % |
| ⚠️ Parcial | 7 | 33 % |
| ❌ Faltante (en ambos documentos) | 0 | 0 % |

Ningún requisito está completamente ausente en ambos documentos simultáneamente, lo cual es una señal positiva del alcance general del diseño. Sin embargo, el 33 % de cobertura parcial representa un riesgo real de inconsistencia en la implementación y en las pruebas de integración.

---

### 2.2 Hallazgos por documento

#### Documento del Arquitecto de Integración

Es el documento con mayor número de brechas. Se identifican tres tipos de problemas:

**1. Requisitos sugeridos ignorados — DOM-RF-018, DOM-RF-020, DOM-RF-021**

Los tres son invisibles en el documento de arquitectura. Si bien su categoría es "sugerida", el ingeniero de software ya los implementó con endpoint y diagrama de secuencia propio, lo que crea una asimetría concreta: existe una API expuesta sin contrato de integración documentado. Esto puede generar problemas en pruebas de integración, auditorías y onboarding de nuevos desarrolladores.

**2. DOM-RF-005 sin sección propia**

La estructura de respuesta estándar se aplica de forma consistente en todos los ejemplos JSON del documento (secciones 3.x y 4.x), pero nunca se declara de forma explícita como un esquema o contrato. Cualquier microservicio consumidor —o equipo externo— que lea solo el documento de arquitectura deberá inferir el esquema a partir de los ejemplos, lo que introduce riesgo de interpretación.

**3. DOM-RF-015 sin diagrama de secuencia**

Los diagramas 8.x cubren los flujos más relevantes (crear+asignar entrega, consultar seguimiento, estado con error tolerante, auditoría asíncrona), pero el registro manual de seguimiento —que involucra validación de estado de entrega y validación de coordenadas geográficas— no tiene representación visual en la sección de arquitectura. Dado que el ingeniero sí lo documentó en el diagrama 5.13, la brecha es solo del lado del arquitecto.

#### Documento del Ingeniero de Software (API)

Tiene cobertura casi completa sobre los 21 requisitos. Su única brecha compartida con el arquitecto es **DOM-RF-019 (Calcular Costo de Envío)**: ambos documentos lo tratan como un sub-proceso interno de DOM-RF-010, sin especificación formal propia. Esto es razonable dado que se trata de lógica interna sin endpoint expuesto; sin embargo, dado que el requisito funcional lo define como una entidad independiente con su propio flujo y excepciones (`tarifa_fija` vs. `por_distancia`, error por coordenadas inválidas), convendría al menos una nota técnica que documente los parámetros de configuración de la tarifa y su ubicación en el sistema.

---

### 2.3 Recomendaciones prioritarias

#### Para el Arquitecto de Integración

**Prioridad alta:**

- Agregar los contratos entrantes de **DOM-RF-018, DOM-RF-020 y DOM-RF-021** en la Sección 4, dado que son endpoints ya presentes y especificados en la API. La asimetría actual es la brecha más crítica del documento.
- Crear una **sección dedicada a la Estructura de Respuesta Estándar** (DOM-RF-005) —análoga a las Secciones 6 y 7— en lugar de dejarla implícita en los ejemplos JSON.

**Prioridad media:**

- Añadir un **Diagrama 8.5** para el flujo de DOM-RF-015 (Registrar Punto de Seguimiento Manual), especialmente por la validación de estado de entrega y coordenadas geográficas que involucra, lo cual es relevante para comprender el comportamiento en escenarios de error.

#### Para el Ingeniero de Software

**Prioridad media:**

- Agregar una **nota técnica o sección auxiliar para DOM-RF-019** que documente el mecanismo de configuración de la tarifa: si se almacena en variable de entorno, tabla en base de datos u otro mecanismo. El requisito funcional lo marca explícitamente como `[Por definir]`, y esta decisión debe quedar registrada antes de la implementación para evitar deuda técnica.

#### Para el equipo en general

- **Sincronizar el estado de los requisitos sugeridos (RF-018 a RF-021):** dado que el ingeniero ya los implementó a nivel de API, el equipo debe tomar una decisión formal sobre si se promueven a requisitos de la Categoría 2. Si se aceptan, el arquitecto debe formalizar sus contratos de integración; si se rechazan o posponen, deben retirarse de la especificación de API para evitar confusion sobre el alcance del sprint.

---

*Análisis generado a partir de la revisión cruzada de los documentos: Requisitos Funcionales v1.0, Diseño de Integración v1.0 y Especificación de API REST v1.0 — ms-domicilios [DOM], ERP Universitario, Marzo 2026.*
