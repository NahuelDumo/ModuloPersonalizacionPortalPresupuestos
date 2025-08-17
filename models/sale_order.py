# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # DEFINIR LOS CAMPOS - ESTO ES LO QUE FALTABA
    portal_last_pdf_attachment = fields.Many2one(
        'ir.attachment', 
        string='Portal Last PDF Attachment',
        compute='_compute_portal_last_pdf_attachment',
        store=False,
        help="Último adjunto PDF para mostrar en el portal"
    )
    
    portal_has_pdf_attachment = fields.Boolean(
        string='Portal Has PDF Attachment',
        compute='_compute_portal_last_pdf_attachment',
        store=False,
        help="Indica si hay un PDF adjunto disponible para el portal"
    )
    
    portal_pdf_attachment_url = fields.Char(
        string='Portal PDF Attachment URL',
        compute='_compute_portal_last_pdf_attachment',
        store=False,
        help="URL para ver el PDF en el portal"
    )
    
    portal_pdf_download_url = fields.Char(
        string='Portal PDF Download URL',
        compute='_compute_portal_last_pdf_attachment',
        store=False,
        help="URL para descargar el PDF desde el portal"
    )
    
    portal_pdf_attachment_name = fields.Char(
        string='Portal PDF Attachment Name',
        compute='_compute_portal_last_pdf_attachment',
        store=False,
        help="Nombre del archivo PDF adjunto"
    )
    
    @api.depends('message_attachment_ids')  # Se recomputa cuando cambien los adjuntos
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
                    order.portal_pdf_attachment_name = attachment.name or 'documento.pdf'
                    # Usar URLs personalizadas para el portal que manejan permisos correctamente
                    order.portal_pdf_attachment_url = f'/my/orders/{order.id}/view_pdf'
                    order.portal_pdf_download_url = f'/my/orders/{order.id}/download_pdf'
                else:
                    order.portal_last_pdf_attachment = False
                    order.portal_has_pdf_attachment = False
                    order.portal_pdf_attachment_name = ''
                    order.portal_pdf_attachment_url = False
                    order.portal_pdf_download_url = False
                    
            except Exception as e:
                _logger.error(f"Error computing PDF attachment for order {order.name}: {e}")
                order.portal_last_pdf_attachment = False
                order.portal_has_pdf_attachment = False
                order.portal_pdf_attachment_name = ''
                order.portal_pdf_attachment_url = False
                order.portal_pdf_download_url = False

    def _get_portal_pdf_info(self):
        """
        Retorna información del PDF para el portal
        """
        try:
            # Asegurar que los campos están computados
            self._compute_portal_last_pdf_attachment()
            
            info = {
                'has_pdf': self.portal_has_pdf_attachment,
                'pdf_url': self.portal_pdf_attachment_url or '',
                'download_url': self.portal_pdf_download_url or '',
                'filename': self.portal_pdf_attachment_name or '',
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

    @api.model
    def debug_portal_pdf_attachments(self, order_id):
        """
        Método de debug para inspeccionar adjuntos PDF de una orden
        """
        _logger.info(f"=== DEBUG PORTAL PDF ATTACHMENTS ===")
        
        try:
            order = self.browse(order_id)
            _logger.info(f"Debugging order: {order.name} (ID: {order.id})")
            
            # Buscar TODOS los adjuntos de esta orden
            all_attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id)
            ])
            
            _logger.info(f"Total attachments for this order: {len(all_attachments)}")
            
            for att in all_attachments:
                _logger.info(f"  - {att.name} | Type: {att.mimetype} | Size: {att.file_size} | Store: {att.store_fname}")
            
            # Buscar específicamente PDFs
            pdf_attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'sale.order'),
                ('res_id', '=', order.id),
                ('mimetype', '=', 'application/pdf')
            ])
            
            _logger.info(f"PDF attachments: {len(pdf_attachments)}")
            
            for pdf in pdf_attachments:
                _logger.info(f"  PDF: {pdf.name} | ID: {pdf.id} | Created: {pdf.create_date}")
                _logger.info(f"       URL: /web/content/{pdf.id}")
                _logger.info(f"       Local URL: {pdf.local_url}")
                
                # Verificar acceso al archivo
                try:
                    data = pdf.datas
                    _logger.info(f"       Can access data: {bool(data)}")
                except Exception as e:
                    _logger.error(f"       Cannot access data: {e}")
            
            # Probar el método de cómputo
            order._compute_portal_last_pdf_attachment()
            _logger.info(f"After compute - Has PDF: {order.portal_has_pdf_attachment}")
            _logger.info(f"After compute - PDF Name: {order.portal_pdf_attachment_name}")
            
            return True
            
        except Exception as e:
            _logger.error(f"Error in debug method: {e}")
            _logger.exception("Full traceback:")
            return False
        finally:
            _logger.info("=== END DEBUG PORTAL PDF ATTACHMENTS ===")