# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii
from datetime import date

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.account.controllers.portal import CustomerPortal
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    @http.route(['/my/account_payment/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_payment_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access('account.payment', invoice_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='account_payment_mail.account_payment_invoices', download=download)

        values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)
        acquirers = values.get('acquirers')

        if invoice_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % invoice_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % invoice_sudo.id] = now
                body = _('Invoice viewed by customer %s') % invoice_sudo.partner_id.name
                _message_post_helper(
                    "account.payment",
                    invoice_sudo.id,
                    body,
                    token=invoice_sudo.access_token,
                    message_type="notification",
                    subtype="mail.mt_note",
                    partner_ids=invoice_sudo.sudo().partner_id.ids,
                )


        if acquirers:
            country_id = values.get('partner_id') and values.get('partner_id')[0].country_id.id
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(invoice_sudo.amount_residual, invoice_sudo.currency_id, country_id)

        return request.render("account_payment_mail.portal_invoice_page_account_payment", values)
        # return request.render("account_payment.portal_my_invoices_payment", values)

    @http.route(['/my/account_payment/<int:invoice_id>/accept'], type='json', auth="public", website=True)
    def portal_my_invoice_payment_detail_accept(self, invoice_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            invoice = self._document_check_access('account.payment', invoice_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Invalid order.')}

        # if not invoice.has_to_be_signed():
        #     return {'error': _('The order is not in a state requiring customer signature.')}
        if not signature:
            return {'error': _('Signature is missing.')}

        if invoice.state != 'invoice send' and invoice.state != 'pre confirm' :
            return {'error': _('The invoice is not in a state requiring customer signature.')}

        if invoice.state == 'pre confirm' :
            return {'error': _('The invoice has already been signed by the customer.')}

        try:
            invoice.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature, 
                'state':'pre confirm',
            })
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        # if not invoice.has_to_be_paid():
        #     # order_sudo.action_confirm()
        #     invoice._send_order_confirmation_mail()

        pdf = request.env.ref('account_payment_mail.account_payment_invoices').sudo().render_qweb_pdf([invoice.id])[0]
        _message_post_helper(
            'account.payment', invoice.id, _('Invoice signed by %s') % (name,),
            attachments=[('%s.pdf' % invoice.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        # if invoice.has_to_be_paid(True):
        #     query_string += '#allow_payment=yes'
        # invoice.state = 'pre-conform'
        return {
            'force_refresh': True,
            'redirect_url': invoice.get_portal_url(query_string=query_string),
        }