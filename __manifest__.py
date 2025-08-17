# -*- coding: utf-8 -*-
{
    'name': 'Portal Sale Order PDF Preview',
    'version': '16.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Vista previa de PDF en portal del cliente para presupuestos',
    'description': """
Portal Sale Order PDF Preview
=============================

Este módulo modifica ÚNICAMENTE la vista del portal del cliente
para mostrar el último PDF adjunto en lugar del PDF generado automáticamente.

Características
---------------

* Solo afecta al portal del cliente (frontend)
* No modifica ninguna vista del backend de Odoo
* Mantiene toda la funcionalidad existente intacta
* Reemplaza los botones "Descargar" e "Imprimir" para usar el último PDF adjunto
* Vista previa del PDF adjunto en lugar del PDF generado

IMPORTANTE: Este módulo solo modifica la experiencia del portal del cliente.
Todas las vistas internas de Odoo permanecen sin cambios.
    """,
    'author': 'Tu Empresa',
    'website': 'https://tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'portal',
        'website',
    ],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ModuloPersonalizacionPortalPresupuestos/static/src/css/portal_pdf.css',
            'ModuloPersonalizacionPortalPresupuestos/static/src/js/portal_pdf.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}