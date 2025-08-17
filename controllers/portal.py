# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
import logging
import base64

_logger = logging.getLogger(__name__)

class PortalSaleOrder(CustomerPortal):
    
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        """
        Override del método portal_order_page para inyectar información del PDF adjunto
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # Computar información del PDF adjunto para el portal (forzar cálculo)
        order_sudo._compute_portal_last_pdf_attachment()
        # Invalidar cache para asegurar cálculo fresco
        order_sudo.invalidate_cache()
        
        # Si se solicita descarga y hay PDF adjunto, usar nuestra ruta personalizada
        if download and order_sudo.portal_has_pdf_attachment:
            download_url = f'/my/orders/{order_id}/download_pdf'
            if access_token:
                download_url += f'?access_token={access_token}'
            return request.redirect(download_url)
        
        # Llamar al método padre
        response = super(PortalSaleOrder, self).portal_order_page(
            order_id, report_type, access_token, message, download, **kw
        )
        
        # Inyectar información adicional del PDF en el contexto
        if hasattr(response, 'qcontext'):
            pdf_info = order_sudo._get_portal_pdf_info()
            # IMPORTANTE: Cambiar las URLs para que usen nuestras rutas personalizadas
            if pdf_info.get('has_pdf'):
                pdf_info['pdf_url'] = f'/my/orders/{order_id}/view_pdf'
                pdf_info['download_url'] = f'/my/orders/{order_id}/download_pdf'
                if access_token:
                    pdf_info['pdf_url'] += f'?access_token={access_token}'
                    pdf_info['download_url'] += f'?access_token={access_token}'
            
            response.qcontext.update({
                'portal_pdf_info': pdf_info,
                'has_portal_pdf': pdf_info.get('has_pdf', False),
            })
        
        return response
    
    @http.route(['/my/orders/<int:order_id>/pdf'], type='http', auth="public", website=True)
    def portal_order_pdf(self, order_id, access_token=None, **kw):
        """
        Override para redirigir a nuestra ruta personalizada
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        
        # Si hay PDF adjunto, usar nuestra ruta personalizada
        if order_sudo.portal_has_pdf_attachment:
            view_url = f'/my/orders/{order_id}/view_pdf'
            if access_token:
                view_url += f'?access_token={access_token}'
            return request.redirect(view_url)
        
        # Si no hay PDF adjunto, usar el comportamiento original
        return super(PortalSaleOrder, self).portal_order_pdf(order_id, access_token, **kw)
    
    @http.route(['/my/orders/<int:order_id>/view_pdf'], type='http', auth="public", website=True)
    def portal_view_pdf(self, order_id, access_token=None, **kw):
        """
        Ruta personalizada para ver el PDF en el portal con permisos correctos
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.not_found()
        
        # Verificar que hay PDF adjunto (forzar cálculo)
        order_sudo._compute_portal_last_pdf_attachment()
        order_sudo.invalidate_cache()
        if not order_sudo.portal_has_pdf_attachment:
            return request.not_found()
        
        attachment = order_sudo.portal_last_pdf_attachment
        
        try:
            # Verificar que el adjunto pertenece a esta orden (seguridad extra)
            if attachment.res_model != 'sale.order' or attachment.res_id != order_sudo.id:
                return request.not_found()
            
            # Obtener el contenido del archivo
            if attachment.datas:
                pdf_content = base64.b64decode(attachment.datas)
                
                # Preparar la respuesta HTTP
                pdfhttpheaders = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(pdf_content)),
                    ('Content-Disposition', f'inline; filename="{attachment.name}"'),
                    ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                    ('Pragma', 'no-cache'),
                    ('Expires', '0'),
                ]
                
                return request.make_response(pdf_content, headers=pdfhttpheaders)
            else:
                _logger.error(f"PDF attachment {attachment.id} has no data")
                return request.not_found()
                
        except Exception as e:
            _logger.error(f"Error serving PDF for order {order_id}: {e}")
            return request.not_found()
    
    @http.route(['/my/orders/<int:order_id>/download_pdf'], type='http', auth="public", website=True)
    def portal_download_pdf(self, order_id, access_token=None, **kw):
        """
        Ruta personalizada para descargar el PDF en el portal con permisos correctos
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except (AccessError, MissingError):
            return request.not_found()
        
        # Verificar que hay PDF adjunto (forzar cálculo)
        order_sudo._compute_portal_last_pdf_attachment()
        order_sudo.invalidate_cache()
        if not order_sudo.portal_has_pdf_attachment:
            return request.not_found()
        
        attachment = order_sudo.portal_last_pdf_attachment
        
        try:
            # Verificar que el adjunto pertenece a esta orden (seguridad extra)
            if attachment.res_model != 'sale.order' or attachment.res_id != order_sudo.id:
                return request.not_found()
            
            # Obtener el contenido del archivo
            if attachment.datas:
                pdf_content = base64.b64decode(attachment.datas)
                
                # Preparar la respuesta HTTP para descarga
                filename = attachment.name or f'presupuesto_{order_sudo.name}.pdf'
                pdfhttpheaders = [
                    ('Content-Type', 'application/pdf'),
                    ('Content-Length', len(pdf_content)),
                    ('Content-Disposition', f'attachment; filename="{filename}"'),
                    ('Cache-Control', 'no-cache, no-store, must-revalidate'),
                    ('Pragma', 'no-cache'),
                    ('Expires', '0'),
                ]
                
                return request.make_response(pdf_content, headers=pdfhttpheaders)
            else:
                _logger.error(f"PDF attachment {attachment.id} has no data")
                return request.not_found()
                
        except Exception as e:
            _logger.error(f"Error downloading PDF for order {order_id}: {e}")
            return request.not_found()
    
    @http.route(['/portal/order/<int:order_id>/pdf_info'], type='json', auth="public")
    def get_portal_pdf_info(self, order_id, access_token=None, **kw):
        """
        Endpoint JSON para obtener información del PDF adjunto desde el portal
        """
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
            pdf_info = order_sudo._get_portal_pdf_info()
            
            # Actualizar URLs para usar nuestras rutas personalizadas
            if pdf_info.get('has_pdf'):
                pdf_info['pdf_url'] = f'/my/orders/{order_id}/view_pdf'
                pdf_info['download_url'] = f'/my/orders/{order_id}/download_pdf'
                if access_token:
                    pdf_info['pdf_url'] += f'?access_token={access_token}'
                    pdf_info['download_url'] += f'?access_token={access_token}'
            
            return pdf_info
        except (AccessError, MissingError):
            return {'error': 'Acceso denegado'}
        except Exception as e:
            _logger.error(f"Error getting PDF info: {e}")
            return {'error': str(e)}