# Arquitectura Tecnica de la Consola de Gestion Integral de Escritorio

## 1. Vision General

La **Consola de Gestion Integral de Escritorio** (`Console-AI-Dev-Infrastructure`) es la aplicacion de mando centralizada desarrollada para estaciones de trabajo Windows. Proporciona a los directores tecnicos, operadores de sistemas y auditores de cumplimiento AI-GRC una interfaz grafica nativa, reactiva y desacoplada para supervisar y gobernar la infraestructura de factoria de software con inteligencia artificial (`Autonomous-AI-Dev-Infrastructure`) y sus proyectos satelite como *Livestock Manager*.

```mermaid
graph TD
    subgraph Host_Windows_11["Estacion de Control Windows 11"]
        Launcher["Lanzador run_console.bat / main.py"]
        ConsoleApp["Consola Desktop (Tkinter / TTK Dark Pro)"]
        
        subgraph Modulos_UI["Modulos Operacionales"]
            M1["1. Monitorizacion y Control de Servicios"]
            M2["2. Estados de Proyecto y Kanban"]
            M3["3. Code Sessions e Interaccion con Agentes"]
            M4["4. Gestor de Incidencias AI-GRC"]
            M5["5. Registro de Eventos y Auditoria"]
        end
        
        ConsoleApp --> M1
        ConsoleApp --> M2
        ConsoleApp --> M3
        ConsoleApp --> M4
        ConsoleApp --> M5
    end

    subgraph Capa_Persistencia["Persistencia Transaccional"]
        SQLiteDB[("SQLite WAL (factory.db)")]
    end

    subgraph Capa_Servicios["Servicios Supervisados"]
        FCC["FCC Server (:8082)"]
        Backend["FastAPI Backend (:8000)"]
        Foundry["Microsoft Foundry (sadogfarm.onmicrosoft.com)"]
        Sandbox["Motor de Sandboxes y Worktrees"]
    end

    ConsoleApp -->|Lectura / Escritura Transaccional| SQLiteDB
    M1 -->|Socket Ping / Health Probe| FCC
    M1 -->|Socket Ping / Process Control| Backend
    M1 -->|Token Cache / Status Check| Foundry
    M1 -->|Allowlist Check| Sandbox
    M2 -->|Aprobacion Humana AI-GRC| SQLiteDB
    M3 -->|Registro y Resolucion Auditada| SQLiteDB
    M4 -->|Generacion de Informes Markdown| ReportsDir["reports/"]
```

---

## 2. Modelo de Concurrencia y Eventos de la Interfaz

Para asegurar una experiencia de usuario fluida y evitar el bloqueo del hilo principal de renderizado grafico en Windows, la consola implementa una arquitectura basada en **hilos de trabajo asincronos (background worker threads)** y enrutamiento seguro mediante el bucle de eventos de Tkinter:

1. **Bucle Principal (Main GUI Thread):** Gestiona exclusivamente la interfaz visual, eventos de raton y teclado, y redibujado de paneles y tablas `Treeview`.
2. **Hilos de Telemetria (Healthcheck Workers):** Comprueban periódicamente la disponibilidad de puertos (`8082`, `8000`), latencias de red y estado del archivo SQLite mediante sockets no bloqueantes.
3. **Despacho Seguro (`safe_after`):** Los hilos secundarios nunca interactúan directamente con los widgets de la interfaz; en su lugar, delegan la mutación visual mediante `self.safe_after(delay_ms, callback)`, garantizando la integridad del árbol de widgets ante condiciones de carrera.

```mermaid
sequenceDiagram
    autonumber
    actor Operador as Operador / Auditor
    participant GUI as Hilo de Interfaz (Tkinter)
    participant Worker as Hilo Asincrono (Worker)
    participant Red as Socket / Servicio (:8082, :8000)
    participant DB as SQLite WAL (factory.db)

    Operador->>GUI: Pulsa "Refrescar Todo" o "Verificar Conexiones"
    GUI->>Worker: Lanza threading.Thread(target=_check_services_health_worker)
    Worker->>Red: socket.create_connection((host, port), timeout=0.8)
    Red-->>Worker: Retorna latencia en milisegundos o error
    Worker->>DB: Verifica existencia e integridad de base de datos
    Worker->>GUI: Invoca safe_after(0, _update_badge)
    GUI->>Operador: Actualiza etiquetas de estado y badge verde/rojo
```

---

## 3. Diseno Modular de la Aplicacion

### Modulo 1: Monitorizacion y Control de Servicios
- **FCC Server (Localhost 8082):** Verificacion de conectividad con el proxy local de modelos de inferencia. Proporciona boton para consultar `/v1/models` y comprobar el catalogo de 4.405 modelos.
- **FastAPI Backend (Localhost 8000):** Comprobacion del backend REST de la Software Factory. Permite lanzar el servidor uvicorn en un subproceso de Windows o detenerlo de forma controlada.
- **Persistencia SQLite WAL:** Confirmacion del archivo `factory.db`, verificacion del modo Write-Ahead Logging (WAL) y soporte para transacciones concurrentes.
- **Microsoft Foundry Hub (`sadogfarm.onmicrosoft.com`):** Estado del Hub empresarial *Sdog Farm Software Factory* y despliegues `sdogfarm-gpt4o`, `sdogfarm-phi4` y `sdogfarm-gpt4o-mini`.
- **Motor de Sandboxes y Worktrees:** Verificacion de politicas de aislamiento de comandos y creacion de ramas efimeras de desarrollo.

### Modulo 2: Estados de Proyecto y Tablero Kanban
- **Ciclo de Estados:** Mapea el flujo de trabajo formal: `BACKLOG` -> `TODO` -> `IN_PROGRESS` -> `IN_REVIEW` -> `APPROVAL_PENDING` -> `DONE`.
- **Inspeccion de Tareas:** Muestra titulo, descripcion, prioridad (`low`, `medium`, `high`, `critical`), clasificacion de datos AI-GRC (`approved_remote`, `restricted`, `local_only`), rama git, criterios de aceptacion y log historico de transiciones.
- **Puerta de Enlace Humana (Human-in-the-Loop Barrier):** Implementa la barrera de aprobacion obligatoria antes de autorizar la promocion de cualquier tarea a `DONE`.

### Modulo 3: Code Sessions e Interaccion con Agentes
- **Hub Web de FCC (:8082/admin/code):** Apertura en navegador del centro de sesiones de código de FCC.
- **Lanzadores de Terminal:** Ejecución desacoplada de sesiones CLI de Claude Code (`launch_fcc_client.bat`) y Aider/Codex con variables de entorno de proxy loopback preconfiguradas.
- **Consola Interactiva de Agentes:** Inyección de System Prompts especializados por rol (Arquitecto, Analista, Full-Stack, QA Tester, Auditor AI-GRC, Project Manager), selección dinámica de modelos con prioridad gratuita (`kilo/kilo-auto/free`, `kilo/openrouter/free`, `open_router/openrouter/free`, `openrouter/auto`) y comerciales (`claude-3-5-sonnet-20241022`, `gpt-4o`). Ejecuta llamadas asíncronas HTTP a `/v1/messages` y almacena eventos forenses en SQLite WAL (`AGENT_INTERACTIVE_SESSION`).

### Modulo 4: Gestor de Incidencias Operacionales y AI-GRC
- **Deteccion y Registro:** Captura violaciones de politicas de seguridad, deteccion de credenciales o secretos (`SecretScanner`), excepciones en el sandbox de comandos y fallos de orquestacion.
- **Triaje por Severidad:** Categorizacion en `critical`, `high`, `medium` y `low`.
- **Resolucion Auditada:** Formulario para documentar la causa raiz y las acciones correctoras, guardando la firma del operador y la fecha de resolucion.

### Modulo 5: Registro de Eventos, Auditoria y Exportacion Forense
- **Stream de Eventos:** Visualizacion de transiciones en `task_events` y de acciones de seguridad en `audit_logs`.
- **Exportador Forense Markdown:** Genera informes ejecutivos estructurados en `reports/informe_auditoria_aigrc_<timestamp>.md` con tablas de metricas, distribucion de estados Kanban, inventario de incidencias y firmas humanas registradas.

---

## 4. Esquema de Datos y Persistencia

La consola opera sobre cuatro tablas relacionales normalizadas en SQLite:

```mermaid
erDiagram
    TASKS ||--o{ TASK_EVENTS : genera
    TASKS ||--o{ AUDIT_LOGS : audita
    TASKS ||--o{ INCIDENTS : bloquea

    TASKS {
        string id PK
        string title
        string description
        string status
        string priority
        string data_classification
        string acceptance_criteria
        string assigned_agent
        string branch_name
        string worktree_path
        timestamp created_at
        timestamp updated_at
    }

    TASK_EVENTS {
        integer id PK
        string task_id FK
        string event_type
        string from_status
        string to_status
        string agent_role
        string payload
        timestamp created_at
    }

    AUDIT_LOGS {
        integer id PK
        string task_id FK
        string action
        string actor
        string details
        timestamp created_at
    }

    INCIDENTS {
        string id PK
        string task_id FK
        string title
        string description
        string severity
        string category
        string status
        string reported_by
        string resolution_notes
        string resolved_by
        timestamp created_at
        timestamp updated_at
    }
```

---

## 5. Integracion Empresarial con Microsoft Azure AI Foundry

La consola esta configurada para integrarse con el Hub empresarial de *Sdog Farm*:
- **Tenant:** `sadogfarm.onmicrosoft.com`
- **Hub:** `Sdog Farm Software Factory`
- **Region y Custodia:** `spaincentral` / `westeurope` bajo la garantia **EU Data Boundary** (Reglamento General de Proteccion de Datos e ISO/IEC 42001).
- **Control de Rutas:** Las tareas con clasificacion `local_only` se restringen al entorno local (FCC Server / CPU local), mientras que las tareas marcadas como `approved_remote` son habilitadas para inferencia en Microsoft Foundry.
