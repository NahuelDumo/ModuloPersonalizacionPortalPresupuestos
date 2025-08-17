# Portal Sale Order PDF Preview

## ⚠️ IMPORTANTE

Este módulo modifica **ÚNICAMENTE** la vista del portal del cliente. **NO modifica ninguna vista del backend de Odoo**.

## 🎯 Objetivo

Mostrar el último PDF adjunto en lugar del PDF generado automáticamente en la vista del portal del cliente para presupuestos/órdenes de venta.

## 🔧 Qué hace exactamente

### ✅ Lo que SÍ modifica:
- **Solo la vista del portal del cliente** (frontend web donde los clientes ven sus presupuestos)
- Reemplaza los botones "Descargar" e "Imprimir" para usar el último PDF adjunto
- Muestra vista previa del PDF adjunto en lugar del PDF generado
- Añade información visual sobre el PDF disponible

### ❌ Lo que NO modifica:
- **Ninguna vista del backend de Odoo** (interfaz administrativa interna)
- **Ningún formulario interno** de presupuestos/órdenes de venta
- **Ninguna funcionalidad del CRM** o módulos internos
- **Ningún reporte o vista de lista** del backend

## 📁 Estructura del módulo

```
portal_sale_pdf/
├── __manifest__.py                 # Configuración del módulo
├── __init__.py                     # Importaciones principales
├── README.md                       # Esta documentación
├── models/
│   ├── __init__.py
│   └── sale_order.py              # SOLO campos para portal
├── views/
│   └── portal_templates.xml       # SOLO templates del portal
├── controllers/
│   ├── __init__.py
│   └── portal.py                  # SOLO controladores del portal
└── static/src/
    ├── css/
    │   └── portal_pdf.css         # SOLO estilos del portal
    └── js/
        └── portal_pdf.js          # SOLO JavaScript del portal
```

## 🚀 Instalación

### 1. Estructura de carpetas

```bash
# Crear la estructura
mkdir -p /path/to/odoo/addons/portal_sale_pdf/{models,views,controllers,static/src/{css,js}}

# Crear archivos __init__.py
touch /path/to/odoo/addons/portal_sale_pdf/__init__.py
touch /path/to/odoo/addons/portal_sale_pdf/models/__init__.py
touch /path/to/odoo/addons/portal_sale_pdf/controllers/__init__.py
```

### 2. Copiar archivos

Copiar cada archivo en su ubicación correspondiente:

- `__manifest__.py` → raíz del módulo
- `models/sale_order.py` → carpeta models/
- `views/portal_templates.xml` → carpeta views/
- `controllers/portal.py` → carpeta controllers/
- `static/src/css/portal_pdf.css` → carpeta static/src/css/
- `static/src/js/portal_pdf.js` → carpeta static/src/js/

### 3. Instalar

1. Reiniciar Odoo
2. Actualizar lista de aplicaciones
3. Buscar "Portal Sale Order PDF Preview"
4. Instalar

## 📱 Cómo funciona

### Para el cliente en el portal:

1. **Accede al portal** con su usuario
2. **Ve sus presupuestos** en "Mis Pedidos"
3. **Abre un presupuesto** que tenga PDFs adjuntos
4. **Ve automáticamente**:
   - Información del PDF adjunto disponible
   - Vista previa del PDF en lugar de la cotización estándar
   - Botones para descargar/imprimir el PDF adjunto

### Comportamiento inteligente:

- ✅ **Si HAY PDF adjunto**: Muestra y usa el PDF adjunto
- ⚠️ **Si NO hay PDF adjunto**: Usa el comportamiento original (PDF generado)

## 🎨 Personalización

### Modificar estilos

Edita `static/src/css/portal_pdf.css`:

```css
/* Cambiar colores */
.portal-pdf-info {
    border-left-color: #tu-color;
}

/* Cambiar altura del PDF */
.portal-pdf-iframe {
    height: 700px; /* tu altura preferida */
}
```

### Modificar textos

Edita `views/portal_templates.xml`:

```xml
<!-- Cambiar el mensaje informativo -->
<h6 class="mb-1">📄 Tu mensaje personalizado</h6>
```

### Añadir funcionalidad JavaScript

Edita `static/src/js/portal_pdf.js` para agregar nuevas características.

## 🔒 Seguridad

- Respeta todos los permisos existentes de Odoo
- Solo muestra PDFs que el usuario tiene derecho a ver
- No expone información adicional del backend
- Mantiene los mismos controles de acceso del portal

## 🧪 Testing

### Probar el módulo:

1. **Crear un presupuesto** con PDF adjunto en el backend
2. **Compartir el presupuesto** con un cliente (portal)
3. **Acceder como cliente** al portal
4. **Verificar** que se muestra el PDF adjunto en lugar del generado

### Casos de prueba:

- ✅ Presupuesto CON PDF adjunto → Muestra PDF adjunto
- ✅ Presupuesto SIN PDF adjunto → Muestra cotización normal
- ✅ Múltiples PDFs adjuntos → Muestra el más reciente
- ✅ Botones de descarga/impresión → Usan el PDF correcto

## 🚫 Limitaciones

- Solo afecta al portal del cliente (frontend)
- Requiere que los PDFs estén adjuntos al presupuesto
- Solo muestra el último PDF adjunto (por fecha de creación)
- No modifica la funcionalidad del backend

## 🔧 Troubleshooting

### PDF no se muestra
1. Verificar que el archivo adjunto sea realmente un PDF
2. Comprobar permisos de acceso al archivo
3. Revisar que el mimetype sea 'application/pdf'

### Botones no funcionan
1. Limpiar caché del navegador
2. Verificar que los assets se carguen correctamente
3. Revisar consola del navegador para errores JavaScript

### Módulo no aparece
1. Verificar estructura de archivos
2. Comprobar que todos los `__init__.py` existen
3. Revisar logs de Odoo para errores de sintaxis

## 📞 Soporte

Este módulo está diseñado para ser:
- **Seguro**: No modifica funcionalidad crítica
- **Independiente**: No interfiere con otros módulos
- **Reversible**: Se puede desinstalar sin afectar datos

---

**¡Perfecto para mostrar PDFs personalizados a tus clientes sin tocar el backend!** 🎉