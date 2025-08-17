# -*- coding: utf-8 -*-
{
    'name': 'ModuloPersonalizacionPresupuesto',
    'summary': 'Portal: previsualizar/descargar/imprimir el último PDF adjunto del presupuesto',
    'version': '16.0.1.0.0',
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
            'sale_portal_quote_pdf_preview/static/src/js/quote_print.js',
        ],
    },
    'installable': True,
    'application': True,
}
