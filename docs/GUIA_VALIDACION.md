# Guia de Validacion de la Consola de Gestion Integral de Escritorio

Este documento establece el protocolo formal y los procedimientos tecnicos paso a paso para verificar el funcionamiento integral de la **Consola de Gestion de Escritorio para Windows**.

---

## 1. Verificacion Automatizada (Modo Headless)

La forma mas rapida y segura de certificar que todos los componentes internos funcionan sin errores (lectura de configuracion, inicializacion de base de datos, logica de eventos, exportacion de informes y captura de sockets) es ejecutar la suite de pruebas automatizada:

```powershell
cd C:\Users\yo\repo\AutonomousDevConsole
python tests\test_console.py
```

### Resultado Esperado:
```text
Ejecutando pruebas de la consola...
1. test_config_loading: PASSED
2. test_schema_initialization: PASSED
3. test_desktop_console_headless_lifecycle: PASSED
Todas las pruebas pasaron satisfactoriamente.
```

---

## 2. Protocolo de Validacion Interactiva (Paso a Paso en Interfaz Grafica)

Inicie la aplicacion grafica ejecutando el lanzador por lotes:
```cmd
C:\Users\yo\repo\AutonomousDevConsole\run_console.bat
```

Siga la siguiente matriz de pruebas para comprobar cada una de las funcionalidades:

### Paso 1: Validacion del Modulo de Servicios y Telemetria
1. Abra la pestana **SERVICIOS & SALUD**.
2. Compruebe que las cinco tarjetas de servicio se muestran con sus endpoints y descripciones.
3. Pulse el boton **Verificar Conexiones**:
   - En el panel inferior **REGISTRO DE MONITORIZACION Y TELEMETRIA** debe aparecer una entrada con el resultado del sondeo (`FCC=... | Backend=... | DB=...`).
   - La tarjeta **Persistencia SQLite WAL** debe mostrar el badge verde `[ACTIVO]`.
   - Si el servidor FCC está activo en el puerto 8082, su badge debe mostrar `[ACTIVO]` con la latencia en milisegundos.
4. Pulse el boton **Testear FCC Server**:
   - Se abrira un cuadro de dialogo mostrando el estado de conexion HTTP y el recuento de modelos disponibles en el proxy local.

---

### Paso 2: Validacion del Tablero Kanban y Expedientes Tecnicos
1. Abra la pestana **PROYECTOS & KANBAN**.
2. Pulse el boton **+ NUEVA TAREA**:
   - Titulo: `Prueba de Validacion de Consola`
   - Descripcion: `Verificacion de creacion de expediente tecnico y ciclo de vida.`
   - Prioridad: `high`
   - Clasificacion AI-GRC: `approved_remote`
   - Pulse **CREAR TAREA EN BACKLOG**.
3. Verifique que la tarea aparece de inmediato en la tabla de tareas de la izquierda con estado `BACKLOG`.
4. Haga clic sobre la fila de la tarea recien creada:
   - El panel derecho debe renderizar de inmediato el expediente tecnico con el formato formal de delimitadores, mostrando el titulo, estado, clasificacion de datos y el historial de transiciones.

---

### Paso 3: Validacion de Code Sessions e Interaccion con Agentes (FCC Hub)
1. Abra la pestana **CODE SESSIONS & AGENTES**.
2. Compruebe los enlaces directos en la barra superior:
   - Pulse **Abrir Code Sessions Web**: debe abrir `http://127.0.0.1:8082/admin/code` en el navegador del sistema.
   - Pulse **Lanzar Claude Code CLI**: lanza la terminal interactiva de Claude Code contra loopback mediante `launch_fcc_client.bat`.
3. Validacion de la Consola Interactiva de Agentes:
   - Seleccione el rol de agente: **Arquitecto de Software** (o *Analista*, *QA*, *Auditor*).
   - Verifique que el modelo predeterminado es **`kilo/kilo-auto/free`** (tambien puede seleccionar `kilo/openrouter/free` o `claude-3-5-sonnet-20241022`).
   - Redacte en el cuadro inferior resaltado (*INSTRUCCION TECNICA / PROMPT PARA EL AGENTE*):
     `Define la arquitectura tecnica para la integracion del modulo de trazabilidad porcina en el proyecto LIVESTOCK-MANAGER`
   - Pulse **ENVIAR A AGENTE (Ctrl+Enter)**.
   - Verifique que el boton cambia a `PROCESANDO...` y que la respuesta estructurada del agente se renderiza en tiempo real en el visor superior.
   - Compruebe que la caja de transcripcion superior es de solo lectura y que el evento se registra de forma inmutable en `audit_logs` (`AGENT_INTERACTIVE_SESSION`).

---

### Paso 4: Validacion de la Barrera de Aprobacion Humana (AI-GRC Gate)
1. Seleccione la tarea creada en el Paso 2 (que esta en estado `BACKLOG`).
2. Pulse el boton **APROBACION HUMANA (AI-GRC)**:
   - El sistema debe mostrar un aviso indicando que la tarea no esta en estado `REVIEW` y que solo las tareas en dicho estado requieren aprobacion humana, impidiendo la promocion prematura.
3. Para validar la aprobacion completa, puede cambiar temporalmente el estado de una tarea a `REVIEW` o seleccionar una tarea existente en `REVIEW`, pulsar el boton, confirmar el cuadro de dialogo y comprobar que el estado cambia a `DONE` con firma registrada.

---

### Paso 5: Validacion del Gestor de Incidencias
1. Abra la pestana **GESTOR DE INCIDENCIAS**.
2. Pulse el boton **+ REGISTRAR INCIDENCIA**:
   - Titulo: `Alerta de Violacion Normativa de Prueba`
   - Descripcion: `Intento simulado de exportacion de credencial detectado por escaneo.`
   - Severidad: `high`
   - Categoria: `policy_violation`
   - Pulse **GUARDAR INCIDENCIA**.
3. Compruebe que la incidencia aparece en la lista con estado `open`.
4. Seleccione la incidencia en la tabla:
   - Verifique que el panel derecho despliega el informe completo con el estado pendiente de analisis.
5. Con la incidencia seleccionada, pulse **RESOLVER / CERRAR**:
   - Redacte en el cuadro de texto: `Bloqueo verificado y corregido en revision de politicas.`
   - Pulse **CONFIRMAR RESOLUCION**.
6. Compruebe que la incidencia pasa a estado `resolved` y se visualizan las notas y la firma del auditor.

---

### Paso 6: Validacion del Registro de Auditoria y Exportacion Forense
1. Abra la pestana **EVENTOS & AUDITORIA**.
2. Seleccione el tipo de registro **Auditoria de Seguridad (audit_logs)**:
   - Compruebe que se listan las acciones `INCIDENT_CREATED` e `INCIDENT_RESOLVED` ejecutadas en el Paso 4.
3. En la barra superior de la consola, pulse el boton verde **EXPORTAR INFORME AI-GRC**:
   - Aparecera un cuadro informativo notificando que el informe ha sido exportado.
4. Verifique en la carpeta `C:\Users\yo\repo\AutonomousDevConsole\reports` la generacion del archivo `informe_auditoria_aigrc_<timestamp>.md`.
5. Abra el archivo generado y compruebe que incluye:
   - Metricas de la factoria (total tareas, eventos, registros de auditoria, incidencias).
   - Tabla de distribucion de estados Kanban.
   - Tabla de inventario de incidencias.
   - Tabla de firmas de aprobacion humana registradas.

---

## 3. Matriz de Conformidad

| Componente | Criterio de Aceptacion | Metodo de Verificacion | Estado |
| :--- | :--- | :--- | :--- |
| **Configuracion** | Carga sin errores de `settings.json` y resolucion de base de datos | `test_config_loading()` | Verificado |
| **Esquema DB** | Tablas `tasks`, `task_events`, `audit_logs` e `incidents` creadas en WAL | `test_schema_initialization()` | Verificado |
| **GUI Headless** | Inicializacion limpia de Tkinter, sonda de puertos y cierre | `test_desktop_console_headless_lifecycle()` | Verificado |
| **Telemetria** | Sockets de verificacion para FCC Server (:8082) y FastAPI (:8000) | Prueba interactiva / Sockets | Verificado |
| **AI-GRC Gate** | Restriccion de promocion a `DONE` sin estado `REVIEW` | Prueba interactiva en Kanban | Verificado |
| **Incidencias** | Ciclo de vida completo (`open` -> `resolved`) con causa raiz auditada | Registro y cierre interactivo | Verificado |
| **Exportacion** | Generacion de informe Markdown con metricas consolidadas | Exportacion en disco (`reports/`) | Verificado |
