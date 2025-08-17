# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def _compute_portal_last_pdf_attachment(self):
        """
        Computa el último adjunto PDF para mostrar en el portal
        """
        for order in self:
            try:
                # Buscar adjuntos PDF relacionados con esta orden
                domain = [
                    ('res_model', '=', 'sale.order'),
                    ('res_id', '=', order.id),
                    ('mimetype', '=', 'application/pdf'),
                    ('name', 'ilike', '%.pdf')
                ]
                
                attachments = self.env['ir.attachment'].search(domain, order='create_date desc', limit=1)
                
                if attachments:
                    attachment = attachments[0]
                    order.portal_last_pdf_attachment = attachment
                    order.portal_has_pdf_attachment = True
                    # Usar URLs personalizadas para el portal que manejan permisos correctamente
                    order.portal_pdf_attachment_url = f'/my/orders/{order.id}/view_pdf'
                    order.portal_pdf_download_url = f'/my/orders/{order.id}/download_pdf'
                else:
                    order.portal_last_pdf_attachment = False
                    order.portal_has_pdf_attachment = False
                    order.portal_pdf_attachment_url = False
                    order.portal_pdf_download_url = False
                    
            except Exception as e:
                _logger.error(f"Error computing PDF attachment for order {order.name}: {e}")
                order.portal_last_pdf_attachment = False
                order.portal_has_pdf_attachment = False
                order.portal_pdf_attachment_url = False
                order.portal_pdf_download_url = False

    def _get_portal_pdf_info(self):
        """
        Retorna información del PDF para el portal
        """
        try:
            self._compute_portal_last_pdf_attachment()
            
            info = {
                'has_pdf': self.portal_has_pdf_attachment,
                'pdf_url': self.portal_pdf_attachment_url or '',
                'download_url': self.portal_pdf_download_url or '',
                'filename': '',
                'filesize': 0,
                'create_date': ''
            }
            
            if self.portal_last_pdf_attachment:
                attachment = self.portal_last_pdf_attachment
                info.update({
                    'filename': attachment.name or 'document.pdf',
                    'filesize': attachment.file_size or 0,
                    'create_date': attachment.create_date.strftime('%Y-%m-%d %H:%M:%S') if attachment.create_date else ''
                })
            
            return info
            
        except Exception as e:
            _logger.error(f"Error getting PDF info for order {self.name}: {e}")
            return {
                'has_pdf': False,
                'pdf_url': '',
                'download_url': '',
                'filename': '',
                'filesize': 0,
                'create_date': '',
                'error': str(e)
            }

    def get_portal_access_token(self):
        """
        Método auxiliar para obtener el token de acceso del portal
        """
        return getattr(self, 'access_token', None) or self.access_token

    def _get_portal_pdf_urls_with_token(self):
        """
        Obtiene las URLs del PDF incluyendo el token de acceso si es necesario
        """
        base_view_url = f'/my/orders/{self.id}/view_pdf'
        base_download_url = f'/my/orders/{self.id}/download_pdf'
        
        # Si estamos en contexto de portal y hay token, añadirlo
        access_token = self.get_portal_access_token()
        if access_token:
            view_url = f'{base_view_url}?access_token={access_token}'
            download_url = f'{base_download_url}?access_token={access_token}'
        else:
            view_url = base_view_url
            download_url = base_download_url
        
        return view_url, download_url