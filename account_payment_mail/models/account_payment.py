from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo import models,http,_

from werkzeug.urls import url_encode



class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'portal.mixin']

    # state = fields.Selection(selection_add=[('invoice send', 'Invoice send')])
    state = fields.Selection([('draft', 'Draft'), ('invoice send', 'Invoice send'), ('pre confirm', 'Pre confirm'), ('posted', 'Validated'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')], readonly=True, default='draft', copy=False, string="Status")

    signature = fields.Image('Signature: ', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By: ', help='Name of the person that signed the SO.', copy=False)
    signed_on = fields.Datetime('Signed On: ', help='Date of the signature.', copy=False)

    def action_draft(self):
        self.signed_by = False
        self.signed_on = False
        self.signature = False
        return super(AccountPayment, self).action_draft()

    def action_send_payment(self):
        # print(dir(self))
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('account_payment_mail.account_payment_mail_template', raise_if_not_found=False)
        # lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'account.payment', self.ids[0])
        ctx = {
            'default_model': 'account.payment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            # 'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'draft').with_context(tracking_disable=True).write({'state': 'invoice send'})
            # self.env.company.sudo().set_onboarding_step_done('sale_onboarding_sample_quotation_state')
        return super(AccountPayment, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def preview_account_payment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        """Override for sales order.

        If the SO is in a state where an action is required from the partner,
        return the URL with a login token. Otherwise, return the URL with a
        generic access token (no login).
        """
        self.ensure_one()
        if self.state not in ['sale', 'done']:
            auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
            return self.get_portal_url(query_string='&%s' % auth_param)
        return super(AccountPayment, self)._get_share_url(redirect, signup_partner, pid)


    def _compute_access_url(self):
        super(AccountPayment, self)._compute_access_url()
        for account in self:
            account.access_url = '/my/account_payment/%s' % (account.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Invoice ', self.name)

