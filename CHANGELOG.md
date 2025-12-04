# 📘 CHANGELOG — Reposición & Picking PRO

Este documento detalla los cambios introducidos en cada versión del sistema.

---

## 🔖 Versión 3.4B PRO — (Actual)
**Estado:** Estable

### 🔧 Mejoras principales
- Reescritura completa del sistema con arquitectura modular (`core`, `ui_supervisor`, `ui_repositor`, `logger`, `ui_role`).
- Implementación de estética **Industrial Light v1.0**.
- Filas intercaladas para mejor legibilidad (#FFFFFF / #F2F2F2).
- Scroll horizontal y vertical en Supervisor y Repositor.
- Historial de ventas en ventana separada, con formateo limpio.
- Manejo robusto de errores y validaciones en todos los módulos.
- Sistema de logging profesional (`logs/app.log`).
- Prevención automática de duplicados al guardar reposición.
- Generación del archivo `reposicion_pendiente.json`.
- Exportación del Repositor a Excel para trabajo offline.
- Registro automático en `historico_reposiciones.csv` con metadatos.

### 🧱 Estructura profesional del proyecto
- `/src` con módulos independientes y mantenibles.
- `/data` para todos los archivos CSV y datos operativos.
- `/logs` autocreado si no existe.
- `main.py` como punto de entrada único del sistema.

---

## 🕘 Versiones anteriores (resumen técnico)

### 3.3G
- Primera versión estable con búsqueda y carga de CSV funcional.
- Exportación básica a Excel.
- Sin estética ni manejo de errores centralizado.

### 3.2
- Unificación de `stock.csv` + `ubicaciones.csv`.
- Ordenamiento por picking básico.

### 3.0
- MVP funcional inicial: selección de reposición y finalización.
- Flujo Supervisor → Repositor mínimo viable.

---

## 🧭 Próximos pasos sugeridos (no implementados)

> *Estas funciones no forman parte de la versión actual. Son propuestas para roadmap profesional.*

- Dashboard con métricas clave del depósito.
- Registro de tiempos (operador, armado, ejecución del picking).
- Captura de usuarios y roles reales.
- Integración opcional vía API REST Dummy para pruebas.