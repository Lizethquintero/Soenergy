# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('order_line')
    def _onchange_order_line(self):
        if self.fiscal_position_id:
            self.action_comparation()
        # for line in self.order_line:
        #     line.tax_ids = line.product_id.tax_id
        # super(SaleOrder,self)._onchange_order_line()
        
        # if self.order_line.product_id and self.fiscal_position_id and self.order_line.price_unit > 0: 
        #     self.action_comparation()
        #     self._compute_invoice_taxes_by_group()

    def action_comparation(self):
        total_taxes = []
        for record in self:
            total_untaxed = 0
            total_cons, total_alma, total_serv = 0, 0, 0
            for line in record.order_line:
                if line.product_id.type == 'consu':
                    total_cons+= line.price_subtotal
                elif line.product_id.type == 'service':
                    total_serv += line.price_subtotal
                elif line.product_id.type == 'product':
                    total_alma += line.price_subtotal
                total_untaxed += line.price_subtotal
                lists = record._compute_comparation(line)
                final_ids, remove_ids = [], []
                ids = line.product_id.taxes_id.ids
                for comparation in lists:
                    # if comparation not in taxes: taxes.append(comparation)
                    dic = {
                        # 'amount': record.amount_untaxed,
                        'amount': line.price_subtotal,
                        'operator': comparation['comparation'],
                        'value': comparation['value']
                    }
                    
                    # record.order_line.write({'tax_ids': [(4, comparation['src'], 0)]})
 
                    if record._compute_operator(dic) and line.product_id.type == comparation['type']:
                        if comparation['dest'] == False:
                            if comparation['src'] not in remove_ids: remove_ids.append(comparation['src'])
                        else:
                            if comparation['dest'] not in final_ids: final_ids.append(comparation['dest'])
                            # if comparation['src'] not in remove_ids: remove_ids.append(comparation['src']) 
                        # ids.remove(comparation['src'])
                        # record.order_line.write({'tax_ids': [(3, comparation['src'], 0)]})
                        # if comparation['dest']:
                        #     record.order_line.write({'tax_ids': [(4, comparation['dest'], 0)]})
                for id in remove_ids:
                    ids.remove(id)
                for id in ids:
                    if id not in final_ids: final_ids.append(id)
                    # if id not in total_taxes: total_taxes.append(id)
                if final_ids:
                    line.tax_id = final_ids
                else:
                    try:
                        line.write({'tax_id':[(5, 0, 0)]})
                    except:
                        raise Warning("Primero se debe tener la factura en borrador")
                # line.tax_id = final_ids

        if record.fiscal_position_id and total_untaxed!=0:
            for line in record.order_line:
                lists = record._compute_comparation(line)
                total_taxes, remove_ids = [], []
                ids = line.product_id.taxes_id.ids
                for comparation in lists:
                    dic = {
                        'amount': total_untaxed,
                        'operator': comparation['comparation'],
                        'value': comparation['value']
                    }
                    if line.product_id.type == 'consu': dic['amount'] = total_cons
                    elif line.product_id.type == 'service': dic['amount'] = total_serv
                    elif line.product_id.type == 'product': dic['amount'] = total_alma 
                    if record._compute_operator(dic) and line.product_id.type == comparation['type']:
                        if comparation['dest'] == False:
                            if comparation['src'] not in remove_ids: remove_ids.append(comparation['src'])
                        else:
                            if comparation['dest'] not in total_taxes: total_taxes.append(comparation['dest'])
                            # if comparation['src'] not in remove_ids: remove_ids.append(comparation['src']) 
                for id in remove_ids:
                    if id in ids: ids.remove(id)
                for id in ids:
                    if id not in total_taxes: total_taxes.append(id)
                if total_taxes:
                    line.tax_id = total_taxes
                else:
                    try:
                        line.write({'tax_id':[(5, 0, 0)]})
                    except:
                        raise Warning("Primero se debe tener la factura en borrador")


    def _compute_comparation(self, line):
        lists = []
        if self.fiscal_position_id:
            products = line.product_id
            ids = products.taxes_id.ids
            lists = self.fiscal_position_id._compute_comparation(tuple(ids))
        return lists

    def _compute_operator(self, dic):
        amount = dic['amount']
        operator = dic['operator']
        value = dic['value']
        if operator == '==': 
            if amount == value: 
                return True 
            else: 
                return False
        elif operator == '!=':
            if amount != value:
                return True
            else: 
                return False
        elif operator == '>':
            if amount > value:
                return True
            else: 
                return False
        elif operator == '<':
            if amount < value:
                return True
            else: 
                return False    
        elif operator == '>=':
            if amount >= value:
                return True
            else: 
                return False
        elif operator == '<=':
            if amount <= value:
                return True
            else: 
                return False
        else:
            return False
