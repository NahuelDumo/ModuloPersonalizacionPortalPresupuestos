# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError

class PortalSaleOrder(CustomerPortal):
    
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        """
        Override del método portal_order_page para inyectar información del PDF adjunto
        SOLO modifica la vista del portal, no afecta el backend
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # Computar información del PDF adjunto para el portal
        order_sudo._compute_portal_last_pdf_attachment()
        
        # Si se solicita descarga y hay PDF adjunto, redirigir al PDF adjunto
        if download and order_sudo.portal_has_pdf_attachment:
            return request.redirect(order_sudo.portal_pdf_download_url)
        
        # Llamar al método padre pero con información adicional del PDF
        response = super(PortalSaleOrder, self).portal_order_page(
            order_id, report_type, access_token, message, download, **kw
        )
        
        # Inyectar información adicional del PDF en el contexto
        if hasattr(response, 'qcontext'):
            pdf_info = order_sudo._get_portal_pdf_info()
            response.qcontext.update({
                'portal_pdf_info': pdf_info,
                'has_portal_pdf': pdf_info.get('has_pdf', False),
            })
        
        return response
    
    @http.route(['/my/orders/<int:order_id>/pdf'], type='http', auth="public", website=True)
    def portal_order_pdf(self, order_id, access_token=None, **kw):
        """
        Override para redirigir al PDF adjunto si existe
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        # Si hay PDF adjunto, redirigir a ese PDF
        if order_sudo.portal_has_pdf_attachment:
            return request.redirect(order_sudo.portal_pdf_attachment_url)
        
        # Si no hay PDF adjunto, usar el comportamiento original
        return super(PortalSaleOrder, self).portal_order_pdf(order_id, access_token, **kw)
    
    @http.route(['/portal/order/<int:order_id>/pdf_info'], type='json', auth="public")
    def get_portal_pdf_info(self, order_id, access_token=None, **kw):
        """
        Endpoint JSON para obtener información del PDF adjunto desde el portal
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
            return order_sudo._get_portal_pdf_info()
        except (AccessError, MissingError):
            return {'error': 'Acceso denegado'}
        except Exception as e:
            return {'error': str(e)}