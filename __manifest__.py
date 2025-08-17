# -*- coding: utf-8 -*-
{
    'name': 'Presupuestos - Vista Previa PDF en Portal',
    'summary': 'Muestra una vista previa del PDF del presupuesto en el portal con opciones de descarga e impresión',
    'version': '16.0.1.0.0',
    'description': """
        Módulo personalizado para mostrar una vista previa del PDF del presupuesto en el portal del cliente,
        con opciones para descargar e imprimir directamente desde la vista de detalle del pedido.
    """,
    'category': 'Sales/Portal',
    'author': 'Nahuel Dumo',
    'license': 'LGPL-3',
    'depends': ['sale', 'portal', 'website'],
    'data': [
        # QWeb templates to be added after confirming Odoo version
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ModuloPersonalizacionPortalPresupuestos/static/src/js/quote_print.js',
        ],
    },
    'installable': True,
    'application': True,
}
