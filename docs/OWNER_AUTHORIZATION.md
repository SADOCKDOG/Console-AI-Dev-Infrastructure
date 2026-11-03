# Autorización de propietario: diseño previsto y comportamiento de Console

**Entrega:** D2-B, documentación únicamente.
**Base revisada:** `c67d62ab12103752071f9fbfa2b317ae3d470062` (`main`).
**Alcance:** este documento diferencia el diseño de Factory del comportamiento que el código de Console en esa base implementa. No habilita ni certifica capacidades.

## 1. Diseño de referencia de Factory

La documentación de Factory describe como **diseño objetivo** la separación Owner humano (FIDO) → App Exec → GitHub (merge), y al DOI como intermediario previsto para operaciones de desarrollo. Las referencias canónicas son [Owner Authorization](https://github.com/SADOCKDOG/Autonomous-AI-Dev-Infrastructure/blob/main/docs/OWNER_AUTHORIZATION.md), [Dev Operations Intermediary](https://github.com/SADOCKDOG/Autonomous-AI-Dev-Infrastructure/blob/main/docs/security/DEV_OPERATIONS_INTERMEDIARY.md) y [especificaciones DOI](https://github.com/SADOCKDOG/Autonomous-AI-Dev-Infrastructure/tree/main/docs/specifications/doi/).

Estas especificaciones y los nombres de rutas API que describen son documentación de diseño; esta PR no acredita que tales rutas estén desplegadas o disponibles. La documentación Factory indica que F2 es implementación local **no operativa**, con `OWNER_AUTH_ENABLED=false`, sin executor y con validaciones/activación pendientes.

## 2. Comportamiento de Console en la base revisada

La revisión estática de `console/app.py` en la base `c67d62ab12103752071f9fbfa2b317ae3d470062` encontró lo siguiente:

- `approve_selected_task` acepta una confirmación de interfaz para una tarea `REVIEW` y escribe directamente `DONE` junto con eventos de auditoría. Ese camino no exige una firma FIDO ni confirma un merge de GitHub.
- `promote_selected_task_to_production` contempla publicar la rama y crear una PR si no existe; para integrar invoca `gh pr merge --admin`, con alternativas de merge. Tras un merge exitoso intenta sincronizar el repositorio local (`checkout`, `fetch`, `reset --hard`) y limpiar worktrees/ramas.
- El método recibe `skip_confirm`; cuando se pasa `True`, omite sus diálogos de confirmación. La interfaz lo llama sin argumento, pero el parámetro no está deshabilitado en la función.

Por tanto, el comportamiento anterior **no equivale** al diseño Owner-Only Authorization de Factory y no debe presentarse como protegido por FIDO, DOI o un contrato de autorización firmado.

## 3. Archivos locales excluidos y alcance de esta PR

En el checkout de trabajo existen archivos locales `console/owner_auth_client.py` y `console/owner_signer.py`, además de cambios locales en `console/app.py`. No están incluidos en esta PR ni forman parte de la base revisada; su presencia local no acredita una capacidad entregada, publicada o validada. Esta PR modifica únicamente documentación.

## 4. Estados de tareas y agentes

El filtro de Console en la base revisada enumera `BACKLOG`, `READY`, `PLANNING`, `IN_PROGRESS`, `TESTING`, `REVIEW`, `DONE` y `BLOCKED`. En esa misma base, la aprobación desde `REVIEW` puede escribir `DONE` directamente, sin esperar confirmación de merge. Esto se documenta como comportamiento observado del código, no como una garantía recomendada.

## 5. Estado de capacidades

- **Diseño documental:** Owner Authorization y DOI según las referencias Factory.
- **Comportamiento de Console en la base:** aprobación local directa y promoción que puede publicar/crear PR, fusionar y realizar sincronización/limpieza; véase §2.
- **Implementación FIDO/API entregada por esta PR:** ninguna; esta PR es documental y no contiene esos archivos ni código.
- **DOI / validación operativa de Owner Authorization:** no se afirma como operativo ni como probado por esta revisión. No se ejecutaron pruebas operativas.

## 6. Reserva D2-A

D2A-02 y D2A-03 permanecen **parciales**: dos copias P1-A3 difieren de sus originales, según el índice de Factory. Esta PR no cambia esa situación.

## 7. Referencias de Console

- `README.md`
- `docs/MANUAL_OPERACION.md`
- `docs/ARQUITECTURA.md`
- `docs/GUIA_VALIDACION.md`
