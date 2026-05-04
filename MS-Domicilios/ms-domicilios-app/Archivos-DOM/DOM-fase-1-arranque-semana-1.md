# Fase 1 - Arranque de Implementacion (Semana 1)

## 1. Objetivo de la semana

Dejar ms-domicilios ejecutando localmente con arquitectura base, conexion a PostgreSQL, migraciones iniciales, contrato de respuesta estandar, request id, manejo global de errores y primer endpoint de salud.

Resultado esperado al cierre de Semana 1:

- Base tecnica estable para construir todos los RF sin retrabajo.
- Estructura de proyecto lista para desarrollo por modulos.
- Pipeline minimo de calidad con pruebas iniciales.

---

## 2. Alcance congelado para el MVP

### Entra al MVP obligatorio (para entrega funcional)

- RF transversales: DOM-RF-001, DOM-RF-002, DOM-RF-003, DOM-RF-004, DOM-RF-005.
- RF funcionales base: DOM-RF-006 a DOM-RF-017.

### Entra como extension (si hay holgura)

- DOM-RF-018, DOM-RF-020, DOM-RF-021.

### Regla de control de alcance

Ningun RF nuevo fuera de esta lista entra al sprint sin desplazar otro RF con el mismo costo.

---

## 3. Backlog ejecutable - Semana 1

## 3.1 Tareas de arquitectura y base

- Crear estructura del proyecto FastAPI por capas: api, application, domain, infrastructure.
- Configurar entorno y dependencias base (FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic, pytest).
- Definir settings por entorno (dev, test) y variables de entorno.
- Configurar conexion a PostgreSQL y sesion de BD.
- Crear migracion inicial (tablas base de repartidores, entregas, seguimiento, calificaciones).

## 3.2 Tareas transversales

- Implementar middleware de request id (reutiliza o genera formato DOM-timestamp-shortid).
- Implementar estructura de respuesta estandar en toda salida de API.
- Implementar manejo global de excepciones con codigos HTTP uniformes.
- Definir contratos de integracion internos para AUTH, ROL y AUD (clientes desacoplados + stubs iniciales).
- Implementar auditoria asincrona sin bloqueo (si falla, registrar local y continuar).

## 3.3 Calidad minima y operacion

- Agregar endpoint GET /health.
- Agregar pruebas iniciales: health, request id, respuesta estandar.
- Configurar linteo/formato base.
- Documentar comando de arranque local y ejecucion de pruebas.

---

## 4. Definition of Done por historia

Una historia se considera terminada solo si cumple todo:

- Endpoint implementado y funcional.
- Validaciones de entrada y errores de negocio.
- Respuesta en formato estandar.
- Request id propagado.
- Auditoria asincrona invocada.
- Tests minimos pasando.
- Documento API actualizado si hubo cambio.

---

## 5. Plan diario recomendado (Semana 1)

## Dia 1

- Crear repo de codigo dentro del workspace.
- Levantar proyecto FastAPI y estructura por capas.
- Configuracion de entorno y comando de arranque.

## Dia 2

- Conexion a PostgreSQL.
- Alembic y migracion inicial.
- Endpoint /health.

## Dia 3

- Middleware request id.
- Respuesta estandar.
- Manejador global de errores.

## Dia 4

- Cliente AUTH y ROL (stub + contrato).
- Cliente AUD asincrono (stub + fallback local).

## Dia 5

- Pruebas base automatizadas.
- Ajustes finales de arquitectura.
- Cierre tecnico de Semana 1.

---

## 6. Riesgos y decisiones pendientes (bloqueantes)

- Definir codigos de permiso por endpoint con equipo de roles.
- Definir estrategia final de auditoria asincrona (cola simple, task queue o broker).
- Confirmar regla de negocio para DOM-RF-019 como proceso interno (sin endpoint).
- Alinear estado final de RF sugeridos 018, 020 y 021 para evitar cambios tardios.

---

## 7. Criterio de avance para pasar a Semana 2

Se pasa a Semana 2 solo si:

- El servicio inicia sin errores.
- Migraciones aplican correctamente.
- Endpoint health responde bien.
- Request id y respuesta estandar estan activos.
- Pruebas base en verde.
