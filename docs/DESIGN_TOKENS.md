# Sistema de Diseño y Tokens: AutonomousDevConsole (ARQ-02: Piel ERP / Escritorio Windows)

## 1. Alcance y Normativa

Este documento define el **contrato de tokens de diseño** para la Consola de Gestión Integral de Escritorio (`AutonomousDevConsole`), catalogada bajo el **Arquetipo ARQ-02 (Piel ERP / Escritorio Windows)** según el estándar de gobernanza SOP-SF-001.

Se fundamenta en las directrices de diseño corporativo **Microsoft Fluent Design System** y accesibilidad **WCAG 2.1 AA** para estaciones de trabajo y pantallas de alta resolución.

---

## 2. Ergonomía y Densidad de Escritorio (Microsoft Fluent Guidelines)

- **Densidad de Información:** Alta densidad estructurada en paneles Bento modulares con bordes sutiles y divisores claros.
- **Tipografía Institucional:**
  - UI y Controles: `Segoe UI`, `system-ui`, sans-serif (pesos regular y negrita).
  - Terminal, Logs y Código: `Consolas`, `Cascadia Code`, monospace.
- **Interacción y Navegación:**
  - Pestañas superiores accesibles con feedback de foco visual.
  - Árboles y tablas de datos con ordenación por columnas y paginación.
  - Atajos de teclado para operaciones recurrentes (F5 recarga, Esc cancelar).

---

## 3. Paleta Cromática Institucional (Dark Enterprise Theme)

```css
:root {
  /* Fondos y Superficies Principales */
  --erp-bg-window: #121212;        /* Fondo raíz de la ventana Windows */
  --erp-bg-panel: #1E1E1E;         /* Paneles de contenido y tarjetas Bento */
  --erp-bg-console: #141414;       /* Visor de terminal, logs y texto monospaciado */
  --erp-bg-input: #262626;         /* Campos de entrada, combos y filtros */

  /* Colores de Acento y Categorías Operacionales */
  --erp-accent-brand: #CCFF00;     /* Amarillo lima de alta visibilidad (Títulos técnicos, foco) */
  --erp-btn-primary: #2563EB;      /* Azul corporativo (Nuevas tareas, acciones principales) */
  --erp-btn-approve: #059669;      /* Verde esmeralda (Aprobación humana AI-GRC) */
  --erp-btn-cycle: #7C3AED;        /* Púrpura orquestación (Ciclo multiagente asistido) */
  --erp-btn-promote: #D97706;      /* Ámbar / Oro (Promoción formal a producción) */
  --erp-btn-secondary: #374151;    /* Gris azulado (GitHub, consultas, secundarias) */
  --erp-status-error: #EF4444;     /* Rojo (Incidencias críticas, bloqueos de seguridad) */

  /* Textos y Contrastes */
  --erp-text-main: #FFFFFF;        /* Texto de máximo contraste */
  --erp-text-body: #F1F5F9;        /* Texto de lectura general */
  --erp-text-muted: #94A3B8;       /* Etiquetas, placeholders y metadatos */
  --erp-text-dim: #64748B;         /* Separadores y marcas de agua */

  /* Bordes y Estructura */
  --erp-border-subtle: #2D3748;    /* Bordes de división interior */
  --erp-border-strong: #333333;    /* Bordes de paneles principales */
  --erp-border-focus: #CCFF00;     /* Borde indicador de selección o foco */

  /* Espaciados y Radios */
  --erp-radius-card: 4px;          /* Bordes rectos de precisión enterprise */
  --erp-radius-button: 3px;        /* Botones compactos de escritorio */
  --erp-padding-dense: 4px 8px;    /* Relleno compacto para tablas de datos */
}
```

---

## 4. Convenciones de Componentes

1. **Botones de Barra de Acciones:**
   - Tipografía: `Segoe UI`, 9 pt, negrita (`font=("Segoe UI", 9, "bold")`).
   - Relleno estándar: `padx=10, pady=3`.
   - Borde: `flat` con `relief="flat"`.

2. **Paneles de Inspección y Expediente:**
   - Marco exterior con borde de 1 px color `#333333`.
   - Área de texto con fondo `#141414` y tipografía monospaciada `Consolas` a 9 pt.

3. **Insignias de Servicio (Badges de Salud):**
   - Estado Operativo: fondo `#059669` (Verde), texto blanco.
   - Estado Degradado / Fallo: fondo `#EF4444` (Rojo), texto blanco.
   - Latencia: fondo `#374151`, texto `#94A3B8`.
