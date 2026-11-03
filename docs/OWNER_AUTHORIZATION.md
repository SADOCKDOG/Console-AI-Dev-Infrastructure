# Autorización de Propietario (Owner-Only Authorization) — Consola de Gestión

**Fase:** Fase D2-B (documentación) — Consola `Console-AI-Dev-Infrastructure`
**Base:** HEAD de inspección `c67d62ab12103752071f9fbfa2b317ae3d470062` (rama `feat/owner-only-authorization-console`, equivalente a `main` en este punto de inspección).
**Alcance:** documentación. No constituye implementación operativa, activación de DOI, creación de Apps, credenciales, permisos ni autorización del propietario para activar capacidades.

---

## 1. Propósito

Este documento consolida, en el repositorio de la Consola, la documentación de la **separación de identidades y de autorización de propietario** que sustenta el flujo de integración (merge) de Pull Requests dentro de la *Sdog Farm Software Factory*.

Describe, sin ejecutar nada:

- La relación entre la Consola y la factoría (repositorio `Autonomous-AI-Dev-Infrastructure`).
- Los estados de tareas (Kanban) y de agentes (Code Sessions) usados por la barrera de aprobación.
- El flujo de autorización del propietario (Owner-Only Authorization) para la integración de PRs.
- La integración futura prevista con el Dev Operations Intermediary (DOI).
- El estado de capacidades (diseño / local fail-closed / no operativo).

---

## 2. Relación con la Factoría (repositorio `Autonomous-AI-Dev-Infrastructure`)

- La Consola se apoya en el backend FastAPI de la factoría en `127.0.0.1:8000`.
- La Consola accede a la base de datos SQLite en modo Write-Ahead Logging (WAL), normalmente en `C:/Users/yo/repo/AutonomousDev/data/factory.db`.
- La Consola expone y consume el contrato de autorización de propietario implementado por la factoría:

| Concepto | Detalle |
|---|---|
| Cliente | `console/owner_auth_client.py` (`OwnerAuthorizationClient`) |
| Firmante | `console/owner_signer.py` (broker de firma FIDO con `sk-*` keys) |
| Endpoint de revisión de contexto | `GET /api/v1/owner-authorizations/review-context?repository=…&pr_number=…` |
| Preparación de autorización | `POST /api/v1/owner-authorizations/prepare` |
| Registro de autorización firmada | `POST /api/v1/owner-authorizations` |
| Revocación firmada | `POST /api/v1/owner-authorizations/{authorization_id}/revoke` |
| Estado / historial | `GET /api/v1/owner-authorizations/{authorization_id}`, `…/history?…` |
| Contexto de ejecución | `GET /api/v1/owner-authorizations/{authorization_id}/execution-context` |
| Ejecución (merge) firmada | `POST /api/v1/owner-authorizations/{authorization_id}/merge` |

- Toda la comunicación de la Consola hacia la factoría se realiza contra el loopback (`127.0.0.1:8000`) y de forma fail-closed ante indisponibilidad o respuestas inválidas.

---

## 3. Separación de identidades y flujos

1. **Owner humano (FIDO) → App Exec → GitHub (merge):** la firma de autorización se realiza con llave OpenSSH FIDO (`sk-ssh-ed25519@openssh.com` / `sk-ecdsa-sha2-nistp256@openssh.com`) mediante broker interactivo que exige presencia física en el token y confirmación del sufijo del SHA del HEAD. La decisión queda ligada a `head_sha`, `base_ref`, `base_sha`, `diff_sha256` y alcance.
2. **Owner humano (FIDO) → DOI → GitHub (dev ops):** flujo previsto para operaciones de desarrollo/integración delegadas al intermediario.
3. **Agente → DOI:** el agente no firma; la delegación de merge requiere autorización firmada por el propietario.

---

## 4. Procedimiento de autorización de integración (task en `REVIEW`)

1. La tarea debe estar en estado `REVIEW` (la barrera AI-GRC exige este estado previo a la aprobación humana).
2. La tarea debe tener una Pull Request registrada (no se publican ramas ni se crean PRs automáticamente desde la Consola).
3. El operador selecciona la tarea y pulsa **APROBAR / AUTORIZAR / REVOCAR / PROMOVER** según el flujo vigente:
   - `APROBACION HUMANA (AI-GRC)`: evalúa el estado y la firma humana.
   - `ESTADO OWNER AUTH`: consulta historial de autorizaciones activas para la PR.
   - `REVOCAR OWNER AUTH`: revoca autorizaciones no consumidas (requiere nueva firma FIDO).
   - `PROMOVER A PRODUCCION (MERGE PR)`: ejecuta el merge de la PR ya autorizada; el alcance permitido es únicamente el merge de esa PR (sin despliegue, sync, cleanup).
   - `VER PR EN GITHUB`: abre la PR en el navegador para revisión externa.
4. El propietario revisa el snapshot de la PR (metadatos, diff manifest SHA-256, checks, branch protection) y decide:
   - **AUTORIZAR SOLO PROPIETARIO** (merge bajo su responsabilidad directa con firma FIDO), o
   - **DELEGAR MERGE AL AGENTE** (solo dentro del allowlist del DOI; la firma FIDO del propietario sigue siendo obligatoria).
5. Ante cualquier inconsistencia de payload, cambio de SHA/diff o fallo de firma: **fail-closed** (denegar, sin fallback ni aprobación sin firmar).

---

## 5. Revocación y caducidad

- Las autorizaciones se emiten con expiración y estado; la revocación consume un namespace de firma (`owner-merge-revocation-v1`) con firma FIDO del propietario.
- La revocación solo aplica a autorizaciones no consumidas; el consumido (merge) requiere un nuevo ciclo.

---

## 6. Estados de tareas y de agentes (consola)

- **Estados de tarea (Kanban):** `BACKLOG`, `READY`, `PLANNING`, `IN_PROGRESS`, `TESTING`, `REVIEW`, `DONE`, `BLOCKED`.
- **Ciclo:** el progreso se modela hasta `REVIEW`; la transición a `DONE` requiere aprobación humana firmada (AI-GRC Gate).
- **Roles de agente (Code Sessions):** Arquitecto de Software, Analista de Requerimientos, Desarrollador Full-Stack, Ingeniero QA / Tester, Auditor AI-GRC & Seguridad, Project Manager.
- El agente interactúa con el propietario mediante instrucciones; la autorización de integración de PRs es exclusivamente del propietario (FIDO).

---

## 7. Integración futura con el Dev Operations Intermediary (DOI)

- El DOI se prevé como el canal único de intermediación entre agente y GitHub para operaciones de desarrollo.
- La Consola ya incorpora el punto de delegación de merge (`DELEGAR MERGE AL AGENTE`) que se materializará sobre el contrato del DOI.
- Hasta que el DOI esté operativo, la Consola opera con el contrato local fail-closed descrito en este documento.

---

## 8. Estado de capacidades y evidencia de diseño

- **Diseño / documentación:** esta documentación.
- **Implementación local (código de la Consola):** cliente y firmante FIDO; contrato contra la factoría.
- **Validación operativa / DOI operativo:** **no ejecutada ni activada** en esta fase.
- **Aprobación del propietario:** no registra capacidad operativa.
- **Estado efectivo observado en la factoría:** `OWNER_AUTH_ENABLED=false`, sin FIDO handle operativo activo, sin executor, sin reglas/rulsets, `factory.db` sin cambios.

> Este documento no afirma que la Consola ejecute operaciones de producción; solo describe el flujo diseñado y documentado.

---

## 9. Referencias cruzadas

- Factoría (repositorio `Autonomous-AI-Dev-Infrastructure`): `docs/OWNER_AUTHORIZATION.md`, `docs/security/DEV_OPERATIONS_INTERMEDIARY.md`, `docs/specifications/doi/`.
- Consola: `README.md`, `docs/MANUAL_OPERACION.md`, `docs/ARQUITECTURA.md`, `docs/GUIA_VALIDACION.md`.
