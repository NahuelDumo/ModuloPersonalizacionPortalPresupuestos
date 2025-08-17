from odoo import models, fields, api
from odoo.http import request

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    @api.depends('message_attachment_ids')
    def _compute_portal_last_pdf_attachment(self):
        """Compute the last PDF attachment ONLY for portal views"""
        for record in self:
            pdf_attachments = record.message_attachment_ids.filtered(
                lambda att: att.mimetype == 'application/pdf'
            ).sorted('create_date', reverse=True)
            
            if pdf_attachments:
                record.portal_last_pdf_attachment_id = pdf_attachments[0].id
                record.portal_has_pdf_attachment = True
                record.portal_pdf_attachment_name = pdf_attachments[0].name
                record.portal_pdf_attachment_url = f'/web/content/{pdf_attachments[0].id}'
                record.portal_pdf_download_url = f'/web/content/{pdf_attachments[0].id}?download=true'
            else:
                record.portal_last_pdf_attachment_id = False
                record.portal_has_pdf_attachment = False
                record.portal_pdf_attachment_name = False
                record.portal_pdf_attachment_url = False
                record.portal_pdf_download_url = False
    
    # Campos específicos para el portal (no interfieren con el backend)
    portal_last_pdf_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Portal - Último PDF Adjunto',
        compute='_compute_portal_last_pdf_attachment',
        store=False
    )
    
    portal_has_pdf_attachment = fields.Boolean(
        string='Portal - Tiene PDF Adjunto',
        compute='_compute_portal_last_pdf_attachment',
        store=False
    )
    
    portal_pdf_attachment_name = fields.Char(
        string='Portal - Nombre del PDF',
        compute='_compute_portal_last_pdf_attachment',
        store=False
    )
    
    portal_pdf_attachment_url = fields.Char(
        string='Portal - URL del PDF',
        compute='_compute_portal_last_pdf_attachment',
        store=False
    )
    
    portal_pdf_download_url = fields.Char(
        string='Portal - URL de descarga del PDF',
        compute='_compute_portal_last_pdf_attachment',
        store=False
    )
    
    def _get_portal_pdf_info(self):
        """Método helper para obtener info del PDF en el portal"""
        self.ensure_one()
        self._compute_portal_last_pdf_attachment()
        
        return {
            'has_pdf': self.portal_has_pdf_attachment,
            'name': self.portal_pdf_attachment_name or 'Sin PDF adjunto',
            'url': self.portal_pdf_attachment_url or '',
            'download_url': self.portal_pdf_download_url or '',
            'attachment_id': self.portal_last_pdf_attachment_id.id if self.portal_last_pdf_attachment_id else False,
        }