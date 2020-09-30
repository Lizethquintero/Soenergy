# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    def _compute_comparation(self, ids):
        lists = []
        for line in self.tax_ids:
            if line.tax_comparation and line.tax_comparation_value>=0 and line.tax_src_id.id in ids:
                dic = {
                    'src': line.tax_src_id.id,
                    'comparation': line.tax_comparation,
                    'value': line.tax_comparation_value,
                    'dest': line.tax_dest_id.id,
                    'type': line.product_type
                }
                lists.append(dic)
        return lists


class AccountFiscalPositionTax(models.Model):
    _inherit = 'account.fiscal.position.tax'

    tax_comparation = fields.Selection([('==', '=='), ('!=', '!='), ('>', '>'), ('<','<'), ('>=','>='), ('<=','<=')], 'Comparation')
    tax_comparation_value = fields.Float('Value', digits='Account')
    product_type = fields.Selection([('consu','Consumible'),('service','Servicio'),('product','Almacenable')],string="Tipo de producto")
