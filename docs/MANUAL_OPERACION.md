# Manual de Operacion de la Consola de Gestion Integral de Escritorio

## 1. Introduccion y Requisitos

La **Consola de Gestion Integral de Escritorio** es el panel de control operativo para administrar la factoria de desarrollo con IA y supervisar el cumplimiento de politicas AI-GRC en estaciones de trabajo con Windows.

### Requisitos del Sistema
- **Sistema Operativo:** Windows 10 / Windows 11 (64 bits).
- **Entorno de Ejecucion:** Python 3.10 o superior con modulo `tkinter` habilitado (incluido por defecto en el instalador estandar de Python para Windows).
- **Conectividad Local:** Acceso a los puertos loopback `127.0.0.1:8082` (FCC Server) y `127.0.0.1:8000` (FastAPI Backend).
- **Persistencia:** Acceso de lectura y escritura al archivo `factory.db` en modo Write-Ahead Logging (WAL).

---

## 2. Puesta en Marcha

Existen tres metodos para iniciar la consola en el entorno de desarrollo:

### Metodo 1: Lanzador por Lotes (Recomendado)
Hacer doble clic sobre el archivo `run_console.bat` o ejecutarlo desde la consola de comandos de Windows:
```cmd
C:\Users\yo\repo\AutonomousDevConsole\run_console.bat
```

### Metodo 2: Script de PowerShell
Ejecutar el script interactivo desde PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\yo\repo\AutonomousDevConsole\run_console.ps1
```

### Metodo 3: Ejecucion Directa con Python
Desde cualquier terminal en la raiz del proyecto:
```powershell
cd C:\Users\yo\repo\AutonomousDevConsole
python main.py
```

---

## 3. Guia de Operacion por Pestanas

### Pestana 1: Servicios & Salud
Esta pestana monitoriza los cinco pilares de la infraestructura y provee acciones de control directo.

1. **Lectura de Indicadores:**
   - `[ACTIVO]` (Verde): El servicio responde en el puerto esperado con latencia en milisegundos.
   - `[DETENIDO]` (Rojo): El puerto no responde o el servicio no esta levantado.
2. **Acciones Disponibles:**
   - **Verificar Conexiones:** Ejecuta un sondeo en paralelo sobre todos los servicios y actualiza sus estados en pantalla.
   - **Iniciar Backend (8000):** Lanza el servidor uvicorn en segundo plano si el repositorio de la factoria esta disponible.
   - **Detener Backend:** Finaliza el proceso de backend si fue iniciado desde la sesion actual de la consola.
   - **Testear FCC Server:** Realiza una peticion HTTP contra `http://127.0.0.1:8082/v1/models` y reporta el recuento de modelos disponibles en un cuadro informativo.
3. **Registro de Monitorizacion y Telemetria:** El cuadro de texto inferior muestra un registro cronologico detallado de cada accion y sondeo ejecutado.

---

### Pestana 2: Proyectos & Kanban
Permite supervisar el ciclo de vida de los requerimientos y emitir aprobaciones humanas de gobernanza.

1. **Filtrado:**
   - Selector **Proyecto Activo:** Filtra entre *Todos los Proyectos*, *Livestock Manager*, *Infrastructure Core* o *Sdog Farm Software Factory*.
   - Selector **Filtro Estado:** Filtra por estados Kanban (`BACKLOG`, `READY`, `PLANNING`, `IN_PROGRESS`, `TESTING`, `REVIEW`, `DONE`, `BLOCKED`). El detalle del ciclo y la barrera de aprobacion humana se define en la [seccion 7](#7-estados-de-tareas-y-de-agentes).
2. **Creacion de Nuevas Tareas:**
   - Pulsar el boton `+ NUEVA TAREA`.
   - Completar el titulo y la descripcion tecnica de los requerimientos.
   - Seleccionar la prioridad (`low`, `medium`, `high`, `critical`).
   - Seleccionar la clasificacion de datos AI-GRC (`approved_remote`, `restricted`, `local_only`).
   - Pulsar `CREAR TAREA EN BACKLOG`. La tarea quedara registrada con identificador unico y trazabilidad auditada.
3. **Inspeccion de Expedientes Tecnicos:**
   - Al seleccionar cualquier tarea en la tabla izquierda, el panel derecho desplegara el expediente completo: metadatos, rama Git, worktree aislado, criterios normativos de aceptacion y el historial de transiciones de agentes.
4. **Barrera de Aprobacion Humana (AI-GRC Gate):**
   - Para promover una tarea a produccion, el estado debe ser `REVIEW`.
   - Seleccionar la tarea y pulsar `APROBACION HUMANA (AI-GRC)`.
   - Confirmar el cuadro de dialogo. El sistema actualizara el estado a `DONE` y firmara una entrada inmutable en `audit_logs` con rol `director_tecnico_consola_windows`.

---

### Pestana 3: Code Sessions & Agentes
Permite interactuar directamente con los agentes especializados de la factoría y probar modelos de inferencia a través del servidor local FCC.

1. **Accesos y Herramientas Externas:**
   - **Abrir Code Sessions Web:** Abre de inmediato `http://127.0.0.1:8082/admin/code` en el navegador web para ver el estado general de sesiones.
   - **Lanzar Claude Code CLI:** Abre una ventana de comando ejecutando `launch_fcc_client.bat` configurada con el proxy loopback local.
   - **Lanzar Sesión Aider / Codex:** Inicia la sesión para edición directa de repositorios.
2. **Consola Interactiva de Agentes:**
   - **Selector de Rol:** Selecciona el rol correspondiente (*Arquitecto de Software*, *Analista de Requerimientos*, *Desarrollador Full-Stack*, *Ingeniero QA / Tester*, *Auditor AI-GRC & Seguridad*, *Project Manager*).
   - **Selector de Modelo:** Prioriza modelos gratuitos de alta disponibilidad (`kilo/kilo-auto/free`, `kilo/openrouter/free`, `open_router/openrouter/free`, `openrouter/auto`) o modelos avanzados (`deepseek/deepseek-chat`, `claude-3-5-sonnet-20241022`, `gpt-4o`).
   - **Cuadro de Entrada de Prompt:** Escriba su instrucción técnica en el recuadro inferior y pulse `ENVIAR A AGENTE (Ctrl+Enter)`.
   - **Visor de Historial:** Muestra la respuesta formateada con diagramas o tablas y bloquea la edición manual para proteger la integridad de la conversación.
   - **Limpiar Historial:** Restablece la vista de conversación sin alterar los registros forenses en base de datos.

---

### Pestana 4: Gestor de Incidencias
Permite auditar y resolver bloqueos operativos o violaciones normativas detectadas por los agentes.

1. **Registro Manual de Incidencias:**
   - Pulsar `+ REGISTRAR INCIDENCIA`.
   - Ingresar titulo, descripcion tecnica o causa raiz.
   - Asignar la severidad (`critical`, `high`, `medium`, `low`) y la categoria (`policy_violation`, `secret_detected`, `sandbox_failure`, `timeout`, `manual`).
   - Guardar la incidencia. Esta quedara en estado `open`.
2. **Inspeccion de Incidencias:**
   - Al hacer clic sobre cualquier fila, el panel derecho mostrara el informe de investigacion con la causa tecnica.
3. **Resolucion Auditada:**
   - Seleccionar la incidencia y pulsar `RESOLVER / CERRAR`.
   - Redactar las notas de resolucion y las medidas correctoras implementadas.
   - Confirmar. La incidencia pasara a estado `resolved` y se emitira un registro inmutable en `audit_logs`.

---

### Pestana 5: Eventos & Auditoria
Permite consultar la pista forense completa y exportar informes ejecutivos.

1. **Visualizacion de Registros:**
   - Selector **Tipo de Registro:** Permite alternar entre `Eventos de Tareas (task_events)` y `Auditoria de Seguridad (audit_logs)`.
   - Selector **Limite:** Configura el numero maximo de entradas a consultar (`50`, `100`, `200`, `500`).
   - Pulsar `Refrescar Registros` para recargar.
2. **Exportacion de Informes de Cumplimiento:**
   - En la cabecera superior derecha de la aplicacion, pulsar el boton verde `EXPORTAR INFORME AI-GRC`.
   - La aplicacion consolidara las metricas de la factoria, el inventario de tareas por estado, el registro de incidencias y las firmas de aprobacion humana en un informe estructurado Markdown guardado en la carpeta `reports/`.

---

## 6. Autorizacion de Propietario y Proceso de Merge con Pull Request (Owner-Only Authorization)

La consola no integra codigo ni ejecuta operaciones de integracion sin la autorizacion firmada del propietario. El flujo documentado es el siguiente:

1. **Prerequisito de estado:** la tarea seleccionada debe estar en estado `REVIEW`. Solo en `REVIEW` se permite iniciar la revision de PR y la aprobacion humana.
2. **Prerequisito de PR:** la tarea debe tener una Pull Request registrada en la base de datos (`PULL_REQUEST_PUBLISHED`); la consola no publica ramas ni crea PRs automaticamente.
3. **Revision del propietario:** mediante el flujo de owner authorization, el propietario revisa el snapshot de la PR (HEAD SHA, Base, diff manifest SHA-256, checks, branch protection) antes de firmar.
4. **Firma FIDO (broker):** el propietario confirma el payload exacto (incluyendo el sufijo del SHA del HEAD) y firma con llave OpenSSH FIDO mediante broker interactivo. Ante cualquier error o cancelacion: **fail-closed** (denegar, sin fallback).
5. **Opciones de integracion:**
   - **AUTORIZAR SOLO PROPIETARIO:** el propietario autoriza el merge con alcance limitado a `MERGE this PR only` (sin despliegue, sincronizacion ni limpieza).
   - **DELEGAR MERGE AL AGENTE:** delegacion habilitada unicamente dentro del allowlist del Dev Operations Intermediary (DOI); la firma FIDO del propietario sigue siendo obligatoria.
6. **Ejecucion de merge:** mediante `PROMOVER A PRODUCCION (MERGE PR)` con autorizacion `ACTIVE` vigente; la tarea permanece en `REVIEW` hasta que GitHub confirme el merge.
7. **Revocacion:** mediante `REVOCAR OWNER AUTH` (requiere nueva firma FIDO del propietario).
8. **Restricciones:** no se ejecutan operaciones automaticas de integracion (`skip_confirm` esta deshabilitado); no se ejecuta sync, deploy ni cleanup.

Detalle completo: [OWNER_AUTHORIZATION.md](OWNER_AUTHORIZATION.md).

---

## 7. Estados de Tareas y de Agentes

- **Estados de tarea (Kanban):** `BACKLOG`, `READY`, `PLANNING`, `IN_PROGRESS`, `TESTING`, `REVIEW`, `DONE`, `BLOCKED`.
- **Ciclo de vida:** las fases previas a `REVIEW` representan trabajo de diseno/planificacion/testing; `REVIEW` es el estado de control de calidad previo a la aprobacion humana.
- **Transicion a `DONE`:** unicamente mediante aprobacion humana firmada (AI-GRC Gate). Las transiciones fuera de `REVIEW` quedan bloqueadas.
- **Roles de agente:** Arquitecto de Software, Analista de Requerimientos, Desarrollador Full-Stack, Ingeniero QA / Tester, Auditor AI-GRC & Seguridad, Project Manager.

---

## 8. Integracion Futura con el Dev Operations Intermediary (DOI)

- El DOI se prevé como canal unico de intermediacion entre agente y GitHub para operaciones de desarrollo.
- La consola incorpora el punto de delegacion de merge (`DELEGAR MERGE AL AGENTE`) que se materializara sobre el contrato del DOI.
- Hasta que el DOI este operativo, la consola opera con el contrato local fail-closed descrito en [OWNER_AUTHORIZATION.md](OWNER_AUTHORIZATION.md).

---

## 9. Estado de Capacidades (Consola)

- **Documentacion:** esta manual y documentos derivados (`ARQUITECTURA.md`, `GUIA_VALIDACION.md`, `OWNER_AUTHORIZATION.md`).
- **Implementacion local:** cliente y firmante FIDO, contrato contra la factoria.
- **Validacion operativa / DOI operativo / activacion:** no ejecutada ni activada en esta fase.
- **Aprobacion del propietario:** no registrada como autorizacion operativa.

