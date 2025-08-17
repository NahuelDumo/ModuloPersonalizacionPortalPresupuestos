# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request

# We inherit the Sale portal controller to reuse access checks and keep behavior consistent
try:
    from odoo.addons.sale.controllers.portal import CustomerPortal as SaleCustomerPortal
except Exception:  # pragma: no cover - in case of version differences
    from odoo.addons.portal.controllers.portal import CustomerPortal as SaleCustomerPortal  # type: ignore


class SalePortalQuotePDFPreview(SaleCustomerPortal):
    """Extend the sale portal to provide routes to preview/download the last PDF attachment
    and (optionally) enrich the order page context in a version-specific override later.
    """

    def _get_last_quote_pdf_attachment(self, order_id):
        """Return the last PDF ir.attachment for the given sale.order id or None.
        We sudo to ensure access to the binary content but will still enforce portal access to the order itself.
        """
        # Accept both strict mimetype and looser matches, as some uploads have
        # different or missing mimetypes but correct filename.
        domain = [
            ('res_model', '=', 'sale.order'),
            ('res_id', '=', order_id),
            '|',
                ('mimetype', 'ilike', 'pdf'),
                ('name', 'ilike', '%.pdf'),
        ]
        # Prefer most recent attachment
        return request.env['ir.attachment'].sudo().search(domain, order='create_date desc, id desc', limit=1)

    def _check_portal_order_access(self, order_id, access_token=None):
        """Leverage the portal access check from the parent controller to ensure the visitor can access the order."""
        # _document_check_access is provided by CustomerPortal
        return self._document_check_access('sale.order', order_id, access_token=access_token)

    # Odoo 16: enrich the values used to render the portal order page
    def _order_get_page_view_values(self, order, access_token=None, **kwargs):  # pylint: disable=arguments-differ
        values = super()._order_get_page_view_values(order, access_token, **kwargs)
        # Compose URLs to serve the last attached PDF (if any)
        token_qs = f"?access_token={access_token}" if access_token else ''
        values.update({
            'quote_pdf_inline_url': f"/my/orders/{order.id}/quote/last-pdf{token_qs}",
            'quote_pdf_download_url': f"/my/orders/{order.id}/quote/last-pdf/download{token_qs}",
        })
        # Determine if there is a PDF available
        has_pdf = bool(self._get_last_quote_pdf_attachment(order.id))
        values['has_quote_pdf'] = has_pdf
        return values

    @http.route(['/my/orders/<int:order_id>/quote/last-pdf'], type='http', auth='public', website=True)
    def portal_order_last_pdf_inline(self, order_id, access_token=None, **kw):
        # Ensure the portal user is allowed to access the order
        try:
            self._check_portal_order_access(order_id, access_token)
        except Exception:
            return request.redirect('/my')

        attachment = self._get_last_quote_pdf_attachment(order_id)
        if not attachment:
            # If no PDF, redirect back to the order page
            base_url = f"/my/orders/{order_id}"
            if access_token:
                base_url += f"?access_token={access_token}"
            return request.redirect(base_url)

        filename = attachment.name or f"order_{order_id}.pdf"
        content = base64.b64decode(attachment.datas or b'')
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', str(len(content))),
            ('Content-Disposition', f'inline; filename="{filename}"'),
            ('X-Content-Type-Options', 'nosniff'),
        ]
        return request.make_response(content, headers=headers)

    @http.route(['/my/orders/<int:order_id>/quote/last-pdf/download'], type='http', auth='public', website=True)
    def portal_order_last_pdf_download(self, order_id, access_token=None, **kw):
        # Ensure the portal user is allowed to access the order
        try:
            self._check_portal_order_access(order_id, access_token)
        except Exception:
            return request.redirect('/my')

        attachment = self._get_last_quote_pdf_attachment(order_id)
        if not attachment:
            base_url = f"/my/orders/{order_id}"
            if access_token:
                base_url += f"?access_token={access_token}"
            return request.redirect(base_url)

        filename = attachment.name or f"order_{order_id}.pdf"
        content = base64.b64decode(attachment.datas or b'')
        headers = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', str(len(content))),
            ('Content-Disposition', f'attachment; filename="{filename}"'),
            ('X-Content-Type-Options', 'nosniff'),
        ]
        return request.make_response(content, headers=headers)
