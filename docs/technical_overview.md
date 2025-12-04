# Technical Overview  
## Reposición & Picking PRO – Arquitectura técnica y flujo de negocio  

**Autor:** Eduardo Hernández  

---

## 1. Flujo operativo real del negocio

El sistema modela un proceso real de reposición en depósitos PyME con entre 300 y 5.000 SKU.  
Participan dos roles operativos: **Supervisor** y **Repositor**.

### 1.1 Supervisor – Planificación de la reposición

El Supervisor:

- Carga los archivos CSV: `stock.csv`, `ubicaciones.csv`, `ventas.csv` (si existe).
- Busca productos por código (parcial o completo).
- Visualiza por cada ítem:
  - Código  
  - Producto  
  - Stock  
  - Ubicación de picking  
  - Cantidad sugerida de reposición  
- Consulta historial de ventas.
- Agrega observaciones.
- Selecciona los productos a reponer.
- Confirma → se genera `reposicion_pendiente.json`.

**Resultado:** lista única, ordenada y sin duplicados de SKU a reponer.

### 1.2 Repositor – Ejecución de la reposición

El Repositor:

- Abre el sistema, que detecta automáticamente `reposicion_pendiente.json`.
- Ve la tabla centrada con:
  - Código  
  - Producto  
  - Stock actual  
  - Picking  
  - Reposición sugerida  
  - Observaciones del Supervisor  
  - Campo **“Cantidad repuesta”**
- Completa cada cantidad (campo obligatorio).
- Puede exportar la tabla a Excel.
- Al finalizar, el sistema:
  - Valida las cantidades
  - Guarda el registro en `historico_reposiciones.csv`
  - Elimina `reposicion_pendiente.json`

**Resultado:** reposición documentada con fecha, rol y cantidades reales.

---

## 2. Flujo técnico del sistema

El sistema utiliza una arquitectura modular y mantenible estilo **WMS ligero**.

### 2.1 Estructura del proyecto

```text
reposicion_wms/
│
├── data/
├── logs/
├── docs/
│   └── technical_overview.md
├── src/
│   ├── main.py
│   ├── ui_role.py
│   ├── ui_supervisor.py
│   ├── ui_repositor.py
│   ├── core.py
│   ├── logger.py
│   └── utils.py
└── README.md
```

### 2.2 Descripción de los módulos

**`main.py`**

- Punto de entrada del sistema.
- Configura la ventana Tkinter (título, tamaño, favicon).
- Redirige al selector de roles.

**`ui_role.py`**

- Muestra pantalla inicial.
- Permite seleccionar Supervisor o Repositor.
- Limpia toda la interfaz entre cambios de rol.

**`ui_supervisor.py`**

- Búsqueda de productos.
- Armado de tabla con stock + picking + reposición.
- Observaciones por SKU.
- Botón de historial (si existe `ventas.csv`).
- Manejo de duplicados.
- Generación de reposicion_pendiente.json.

**`ui_repositor.py`**

- Carga del archivo pendiente.
- Tabla centrada y estética Industrial Light v1.0.
- Filas intercaladas (#FFFFFF / #F2F2F2).
- Validación estricta de cantidades.
- Exportación a Excel.
- Escritura en `historico_reposiciones.csv`.

**`core.py`**

- Carga de `stock.csv`, `ubicaciones.csv`, `ventas.csv`, `TodosLosPedidos.csv`
- Merge de datos
- Limpieza y normalización
- Ordenamiento según ubicación de picking
- Función clave_orden_picking()

**`logger.py`**

- Sistema de logging en /logs/app.log
- Registra errores y acciones clave
- No interrumpe el funcionamiento ante fallos

**`utils.py`**

- Validaciones auxiliares
- Limpieza de strings
- Funciones reutilizables

## 3. Especificaciones de archivos CSV

Todos deben estar en /data/.

**`stock.csv`**

- Finalidad: fuente principal del inventario.
- Columnas requeridas:
  - codigo (str)
  - producto (str)
  - stock (int)
  - picking (str)
  - reposicion (int o vacío)
- Validaciones:
  - No puede faltar codigo.
  - Stock debe ser numérico.
  - Filas corruptas se ignoran con log de advertencia.

**`ubicaciones.csv`**

- Une los SKU con su ubicación física.
- Columnas mínimas:
  - codigo (str)
  - picking (str)
  - reposicion (str)
- Se cruza automáticamente con `stock.csv`.

**`ventas.csv`**

- Historial de movimientos de salida.
- Columnas requeridas:
  - fecha (date)
  - cliente (str)
  - comprobante (str)
  - producto (str)
  - cantidad (int)
  - codigo (str)
- Usado solo para el botón Ver historial.

**`TodosLosPedidos.csv`**

- Aporta información enriquecida del estado de los pedidos.
- Columnas requeridas:
  - nombre del cliente (str)
  - estado de preparacion (str)
  - empresa de envio (str)
  - nombre de transporte (str)
  - numero de seguimiento (str)
  - estado de despacho (str)
  - fecha de despacho (date)
  - numero de pedido dux (str)
  - cantidad de comprobantes (str)
  - importe total (str)
  - Fecha (date)
- Se usa para complementar el historial y análisis de contexto.

**`historico_reposiciones.csv`**

- Se genera automáticamente.
- Columnas:
  - codigo (str)
  - producto (str)
  - stock (int)
  - picking (str)
  - reposicion (str)
  - observaciones (str)
  - cantidad_reponer (int)
  - fecha_registro (date)
  - rol (str)
- Si no existe → se crea automáticamente.

## 4. Reglas de negocio del sistema

**Reglas del Supervisor**

- Se requiere al menos 1 coincidencia en búsqueda. 
- Los resultados se ordenan por picking. 
- No puede haber duplicados en la lista final. 
- Observaciones opcionales. 
- JSON final siempre sobrescribe al anterior. 
- Si el JSON existe → se advierte al usuario.

**Reglas del Repositor**

- “Cantidad repuesta” obligatoria.
- Debe ser entero ≥ 0.
- No se permiten strings ("dos", "5u", etc.).
- Se escribe una fila por producto en histórico.
- El archivo JSON se elimina siempre al finalizar.

**Reglas sobre archivos**

- Todos los CSV deben estar en /data/.
- Si falta `stock.csv` → el sistema no funciona.
- Si falta `ubicaciones.csv` → picking/reposición no se pueden mostrar.
- Si falta `ventas.csv` o `TodosLosPedidos.csv` → igual funciona, pero sin historial extendido.
- Los logs nunca bloquean el funcionamiento.

## 5. Conclusión

**Este documento detalla:**

- El proceso real del negocio
- La arquitectura del sistema
- La interacción de los módulos
- Los CSV y su estructura
- Las reglas de negocio exactas

Documento diseñado para uso en portfolio profesional, auditorías técnicas y presentaciones a clientes PyME.