# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import fields, osv
from openerp.report import report_sxw
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import csv
class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'oid': fields.integer('Old ID'),
    }
product_product()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'oid': fields.integer('Old ID'),
    }
res_partner()

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
        'oid': fields.integer('Old ID'),
        'old_name': fields.char('Old Name', size=128),
    }
    
    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True
    
purchase_order()

class purchase_line_invoice(osv.osv_memory):

    """ To create invoice for purchase order line"""

    _inherit = 'purchase.order.line_invoice'

    def makeInvoices(self, cr, uid, ids, context=None):
        print 'context invoice  ', context
        """
             To get Purchase Order line and create Invoice
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            context={}

        record_ids =  context.get('active_ids',[])
        if record_ids:
            res = False
            invoices = {}
            res_user = self.pool.get('res.users')
            invoice_obj = self.pool.get('account.invoice')
            purchase_obj = self.pool.get('purchase.order')
            purchase_line_obj = self.pool.get('purchase.order.line')
            invoice_line_obj = self.pool.get('account.invoice.line')
            account_jrnl_obj = self.pool.get('account.journal')

            def multiple_order_invoice_notes(orders):
                notes = ""
                for order in orders:
                    notes += "%s \n" % order.notes
                return notes



            def make_invoice_by_partner(partner, orders, lines_ids):
                """
                    create a new invoice for one supplier
                    @param partner : The object partner
                    @param orders : The set of orders to add in the invoice
                    @param lines : The list of line's id
                """
                name = orders and orders[0].name or ''
                journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'purchase')], context=None)
                journal_id = journal_id and journal_id[0] or False
                a = partner.property_account_payable.id
                inv = {
                    'name': name,
                    'origin': name,
                    'type': 'in_invoice',
                    'journal_id':journal_id,
                    'reference' : partner.ref,
                    'account_id': a,
                    'partner_id': partner.id,
                    'invoice_line': [(6,0,lines_ids)],
                    'currency_id' : orders[0].pricelist_id.currency_id.id,
                    'comment': multiple_order_invoice_notes(orders),
                    'payment_term': orders[0].payment_term_id.id,
                    'fiscal_position': partner.property_account_position.id
                }
                inv_id = invoice_obj.create(cr, uid, inv)
                
                for order in orders:
                    order.write({'invoice_ids': [(4, inv_id)],
                                 })
                return inv_id

            for line in purchase_line_obj.browse(cr, uid, record_ids, context=context):
                if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                    if not line.partner_id.id in invoices:
                        invoices[line.partner_id.id] = []
                    acc_id = purchase_obj._choose_account_from_po_line(cr, uid, line, context=context)
                    inv_line_data = purchase_obj._prepare_inv_line(cr, uid, acc_id, line, context=context)
                    inv_line_data.update({'origin': line.order_id.name})
                    inv_id = invoice_line_obj.create(cr, uid, inv_line_data, context=context)
                    purchase_line_obj.write(cr, uid, [line.id], {'invoiced': True, 'invoice_lines': [(4, inv_id)]})
                    invoices[line.partner_id.id].append((line,inv_id))

            res = []
            for result in invoices.values():
                il = map(lambda x: x[1], result)
                orders = list(set(map(lambda x : x[0].order_id, result)))

                res.append(make_invoice_by_partner(orders[0].partner_id, orders, il))

        return {
            'domain': "[('id','in', ["+','.join(map(str,res))+"])]",
            'name': _('Supplier Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
            'type': 'ir.actions.act_window'
        }
purchase_line_invoice()

class sale_advance_payment_inv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_obj = self.pool.get('sale.order')
        ir_property_obj = self.pool.get('ir.property')
        fiscal_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])

        result = []
        for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
            val = inv_line_obj.product_id_change(cr, uid, [], wizard.product_id.id,
                    uom_id=False, partner_id=sale.partner_id.id, fposition_id=sale.fiscal_position.id)
            res = val['value']

            # determine and check income account
            if not wizard.product_id.id :
                prop = ir_property_obj.get(cr, uid,
                            'property_account_income_categ', 'product.category', context=context)
                prop_id = prop and prop.id or False
                account_id = fiscal_obj.map_account(cr, uid, sale.fiscal_position or False, prop_id)
                if not account_id:
                    raise osv.except_osv(_('Configuration Error!'),
                            _('There is no income account defined as global property.'))
                res['account_id'] = account_id
            if not res.get('account_id'):
                raise osv.except_osv(_('Configuration Error!'),
                        _('There is no income account defined for this product: "%s" (id:%d).') % \
                            (wizard.product_id.name, wizard.product_id.id,))

            # determine invoice amount
            if wizard.amount <= 0.00:
                raise osv.except_osv(_('Incorrect Data'),
                    _('The value of Advance Amount must be positive.'))
            if wizard.advance_payment_method == 'percentage':
                inv_amount = sale.amount_total * wizard.amount / 100
                if not res.get('name'):
                    res['name'] = _("Advance of %s %%") % (wizard.amount)
            else:
                inv_amount = wizard.amount
                if not res.get('name'):
                    #TODO: should find a way to call formatLang() from rml_parse
                    symbol = sale.pricelist_id.currency_id.symbol
                    if sale.pricelist_id.currency_id.position == 'after':
                        res['name'] = _("Advance of %s %s") % (inv_amount, symbol)
                    else:
                        res['name'] = _("Advance of %s %s") % (symbol, inv_amount)

            # determine taxes
            if res.get('invoice_line_tax_id'):
                res['invoice_line_tax_id'] = [(6, 0, res.get('invoice_line_tax_id'))]
            else:
                res['invoice_line_tax_id'] = False

            # create the invoice
            inv_line_values = {
                'name': res.get('name'),
                'origin': sale.name,
                'account_id': res['account_id'],
                'price_unit': inv_amount,
                'quantity': wizard.qtty or 1.0,
                'discount': False,
                'uos_id': res.get('uos_id', False),
                'product_id': wizard.product_id.id,
                'invoice_line_tax_id': res.get('invoice_line_tax_id'),
                'account_analytic_id': sale.project_id.id or False,
            }
            inv_values = {
                'name': sale.client_order_ref or sale.name,
                'origin': sale.name,
                'type': 'out_invoice',
                'reference': False,
                'account_id': sale.partner_id.property_account_receivable.id,
                'partner_id': sale.partner_id and sale.partner_id.id or 0,
                'invoice_line': [(0, 0, inv_line_values)],
                'currency_id': sale.pricelist_id.currency_id.id,
                'partner_invoice_id': sale.partner_invoice_id and sale.partner_invoice_id.id or 0,
                'partner_shipping_id': sale.partner_shipping_id and sale.partner_shipping_id.id or sale.partner_invoice_id.id,
                'comment': '',
                'payment_term': sale.payment_term.id,
                'fiscal_position': sale.fiscal_position.id or sale.partner_id.property_account_position.id
            }
            result.append((sale.id, inv_values))
        return result

sale_advance_payment_inv()

class change_invoice_line1(osv.osv_memory):
    _name = "change.invoice.line1"
    _description = "Change Invoice Line1"
    _columns = {
        'name': fields.many2one('account.invoice.line', 'Invoice Line'),
        'qty': fields.float('Qty'),
        'uprice': fields.float('Unit Price'),
        'discount': fields.float('Discount(%)'),
        'parent_id': fields.many2one('change.invoice.line', 'Invoice Line'),
        'tax_id': fields.many2many('account.tax', 'line_tax_change_rel', 'line_id', 'tax_id', 'Tax'),
    }
change_invoice_line1()

class change_invoice_line(osv.osv_memory):
    _name = "change.invoice.line"
    _description = "Change Invoice Line"
    
    def get_default_invoice(self, cr, uid, context={}):
        result = 0
        if context.get('active_id', False):
            result = context['active_id']            
        return result
    
    def get_inv_line(self, cr, uid, context={}):
        result = []
        inv_obj = self.pool.get('account.invoice')
        if context.get('active_id', False):
            result = [{'name': x.id, 'uprice': x.price_unit, 'qty':x.quantity, 'discount':x.discount} for x in inv_obj.browse(cr, uid, context['active_id']).invoice_line]
        return result    
    _columns = {
        'name': fields.many2one('account.invoice'),
        'invoice_line':fields.one2many('change.invoice.line1', 'parent_id', 'Invoice Line'),
    }
    _defaults = {
        'name': get_default_invoice,
        'invoice_line': get_inv_line,
    }

    def change_price(self, cr, uid, ids, context=None):
        inv_ob = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        non_tax_account = []
        for record in self.browse(cr, uid, ids):
            non_tax_account.append(record.name.account_id.id)            
            for line in record.invoice_line:
                non_tax_account.append(line.name.account_id.id)
                sql2 = ''' update account_invoice_line set price_unit = %s, quantity = %s, discount = %s where id = %s  '''%(line.uprice, line.qty, line.discount, line.name.id)
                cr.execute(sql2)
                sql7 = ''' Delete from account_invoice_line_tax where invoice_line_id = %s  '''%line.name.id
                cr.execute(sql7)
                for tax in line.tax_id:
                    sql6 = ''' Insert into account_invoice_line_tax values(%s,%s)  '''%(line.name.id, tax.id)
                    cr.execute(sql6)
                sub_total = inv_line_obj._amount_line(cr, uid, [line.name.id], 1, 1, 1).values()[0]
                sql3 = ''' Update account_invoice_line Set price_subtotal= %s where id = %s '''%(sub_total, line.name.id)
                cr.execute(sql3)
                for jn_line in record.name.move_id.line_id:
                    if jn_line.name == line.name.name:
                        sql1 = '''update account_move_line set credit = %s, tax_amount = %s where id = %s  '''%(sub_total, sub_total, jn_line.id)
                        print sql1
                        cr.execute(sql1)
                inv_ob.button_reset_taxes(cr, uid, [record.name.id])
        for rc in self.browse(cr, uid, ids):
            for jn_line1 in rc.name.move_id.line_id:
                if jn_line1.account_id.id not in non_tax_account:
                    sql5 = sql1 = '''update account_move_line set credit = %s, tax_amount = %s where id = %s  '''%(rc.name.amount_tax, rc.name.amount_tax, jn_line1.id)
                    cr.execute(sql5)
            for jn_line2 in rc.name.move_id.line_id:
                if jn_line2.account_id.id == rc.name.account_id.id:
                    sql4 = '''update account_move_line set debit = %s where id = %s  '''%(rc.name.amount_total, jn_line2.id)
                    cr.execute(sql4)                        
        return 1

change_invoice_line()

def rounding(number):
    print ' cogoi hanm tinh nay ne  == ', number
    if number:
        temp = round(number,3) - round(number,2)
        if temp < 0:
            return round(number,2) - 0.01
        return round(number,2)
    return number

class account_tax(osv.osv):
    _inherit = "account.tax"
    
    def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        if not precision:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
        total = 0.0
        for r in res:
            if r.get('balance',False):
                r['amount'] = rounding(r.get('balance', 0.0) * quantity) - total
            else:
                r['amount'] = rounding(r.get('amount', 0.0) * quantity)
                total += r['amount']
        return res

class account_invoice(osv.osv):
    _inherit = "account.invoice"
#     def _amount_all(self, cr, uid, ids, name, args, context=None):
#         res = {}
#         for invoice in self.browse(cr, uid, ids, context=context):
#             res[invoice.id] = {
#                 'amount_untaxed': 0.0,
#                 'amount_tax': 0.0,
#                 'amount_total': 0.0
#             }
#             tax_ids = []
#             for line in invoice.invoice_line:
#                 res[invoice.id]['amount_untaxed'] += rounding(line.price_subtotal)
#                 if line.invoice_line_tax_id:
#                     for tax in line.invoice_line_tax_id:
#                         if tax.id not in tax_ids: 
#                             tax_ids.append(tax.id)
#             temp = 0
#             for line in invoice.tax_line:
#                 res[invoice.id]['amount_tax'] += rounding(line.amount)
#             if len(tax_ids) == 1:
#                 temp = rounding(res[invoice.id]['amount_untaxed'] * self.pool.get('account.tax').browse(cr, uid, tax_ids[0]).amount)
#                 if res[invoice.id]['amount_tax'] != temp:
#                     res[invoice.id]['amount_tax'] = temp
#                     self.pool.get('account.invoice.tax').write(cr, uid, [invoice.tax_line[len(invoice.tax_line) - 1].id], {'amount':temp})
#             res[invoice.id]['amount_total'] = rounding(res[invoice.id]['amount_tax']) + rounding(res[invoice.id]['amount_untaxed'])
#         return res
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    def _get_invoice_tax(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()

    _columns = {
        'po_num': fields.char('P/o Number', size=128),
        'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Invoice address for current sales order."),
        'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order."),
        'oid': fields.integer('Old ID'),
        'old_name': fields.char('Old Name', size=128),
#         'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Subtotal', track_visibility='always',
#             store={
#                 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                 'account.invoice.tax': (_get_invoice_tax, None, 20),
#                 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#             },
#             multi='all'),
#         'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Tax',
#             store={
#                 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                 'account.invoice.tax': (_get_invoice_tax, None, 20),
#                 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#             },
#             multi='all'),
#         'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
#             store={
#                 'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
#                 'account.invoice.tax': (_get_invoice_tax, None, 20),
#                 'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
#             },
#             multi='all'),
    }

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if args is None:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('oid', '=', name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
        return self.name_get(cr, user, ids, context=context)

    def check_income_acc(self, cr, uid, ids, context={}):
        prod_obj = self.pool.get('product.product')
        prod_ids = prod_obj.search(cr, uid, [])
        print 'income = ', [x.property_account_income and x.property_account_income.code + ' ' + x.property_account_income.name or 0 for x in prod_obj.browse(cr, uid, prod_ids)]
        print '\n expense = ', [x.property_account_expense and x.property_account_expense.code + ' ' + x.property_account_expense.name or 0 for x in prod_obj.browse(cr, uid, prod_ids)]
        return 1
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        if not partner_id:
            result['value'].update({'partner_invoice_id': False, 'partner_shipping_id': False})
            return result
        part = self.pool.get('res.partner').browse(cr, uid, partner_id)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        result['value'].update({'partner_invoice_id': addr['invoice'], 'partner_shipping_id': addr['delivery']})
        return result
    def update_address(self, cr, uid, ids, context={}):
        inv_ids = self.search(cr, uid, [])
        for record in self.browse(cr, uid, inv_ids):
            partner_id = record.partner_id and record.partner_id.id or 0
            if partner_id:
                addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['delivery', 'invoice', 'contact'])
                self.write(cr, uid, [record.id], {'partner_invoice_id': addr['invoice'], 'partner_shipping_id': addr['delivery']})
        return 1

    def change_inv_line(self, cr, uid, ids, context={}):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'change.invoice.line',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'active_id': ids and ids[0] or 0, 'type': self.browse(cr, uid, ids)[0].type},
            'nodestroy': True,
        }
        
account_invoice()



class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = rounding(cur_obj.round(cr, uid, cur, res[line.id]))
        return res
account_invoice_line()
class sale_order(osv.osv):
    _inherit = "sale.order"

    def get_user_id(self, cr, uid, context={}):
        return uid

    def check_readonly(self, cr, uid, ids, field_name, arg, context=None):
        user_obj = self.pool.get('res.users')
        res = {}
        rs = 0
        for record in self.browse(cr, uid, ids):
            for x in user_obj.browse(cr, uid, uid).groups_id:
                if x.name == 'Detail Own Quotation':
                    if record.user_id:
                        if record.user_id.id == uid:
                            res[record.id] = 0
                            return res
                        else:
                            res[record.id] = 1
                    else:
                        res[record.id] = 1
                else:
                    res[record.id] = 0
        return res
        
    _columns = {
        'is_readonly': fields.function(check_readonly, type='boolean', string='Readonly'),
        'oid': fields.integer('Old ID'),
        'old_name': fields.char('Old Name', size=128),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if not ids:
            return True
        if type(ids) != type([]):
            ids = [ids] 
        user_obj = self.pool.get('res.users')
        for record in self.browse(cr, uid, ids):
            for x in user_obj.browse(cr, uid, uid).groups_id:
                if x.name == 'Detail Own Quotation':
                    if record.user_id:
                        if record.user_id.id == uid:
                            pass
                        else:
                            raise osv.except_osv('Warnning!', 'You can not change anything, please contact with Administrator!')
                    else:
                        raise osv.except_osv('Warnning!', 'You can not change anything, please contact with Administrator!')
                else:
                    pass
        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        result = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context)
        sale_obj = self.pool.get('sale.order')
        invoice_obj = self.pool.get('account.invoice')
        dict_rs = {}
        for sale in sale_obj.browse(cr, uid, ids):
            if  sale.partner_invoice_id:
                dict_rs.update({'partner_invoice_id': sale.partner_invoice_id and sale.partner_invoice_id.id or 0})
            if sale.partner_shipping_id:
                dict_rs.update({'partner_shipping_id': sale.partner_shipping_id and sale.partner_shipping_id.id or 0})
            dict_rs.update({'partner_id': sale.partner_id.id})

        invoice_obj.write(cr, uid, [result], dict_rs) 
        return result

    _defaults = {
        'user_id': get_user_id,
    }
    
sale_order()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    _columns = {
        'oid': fields.integer('Old ID'),
        'old_name': fields.char('Old Name', size=128),
    }
    
account_voucher()


class account_invoice_jmd_pacific(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_jmd_pacific, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line': self.get_line,
            'get_description': self.get_description,
        })

    def process_line_wrap(self, character, char_com):
        result = []
        num_char = 0
        line = ''
        arr1 = []
        arr = character.split('\n')
        for tep1 in arr:
            for tep in tep1.split(' '):
                arr1.append(tep)
            for temp in arr1:
                num_char += len(temp)
                if num_char <= char_com:
                    line += ' ' + temp
                else:
                    result.append(line)
                    num_char = len(temp)
                    line  = temp
            result.append(line)
        return result


    def get_line(self,line):
        result = []
        result1 = []
        result2 = []
        temp = 0
        for x in line:
            temp += self.process_line_wrap(self.get_description(x), 25)
#            raise osv.except_osv('Warning', temp)
            if temp < 27:
                result1.append(x)
            else:
                result2.append(x)
        result.append(result1)
        result.append(result2)
        return result

    def get_description(self, line):
        result = ''
        product_name    = line.product_id and line.product_id.name or ''
        product_barcode = line.product_id and (line.product_id.ean13 and line.product_id.ean13 or '') or '' 
        description = line.name
        if product_barcode:
            if product_name in description:
                kq = description.split(product_name)
                kq = kq[len(kq) - 1]
                if '-' in kq:
                    kq = kq.split('-')
                    kq = '- ' + kq[len(kq) - 1]
                else:
                    kq = ''
                result = '[%s] %s %s'%(product_barcode, product_name, kq)
        else:
            result = description
        return result

report_sxw.report_sxw(
    'report.account.invoice.jmd_pacific',
    'account.invoice',
    'addons/crea8s_jmd_pacific_fix/account_print_invoice.rml',
    parser=account_invoice_jmd_pacific
)

class account_invoice_jmd_pacific_without(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_jmd_pacific_without, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line': self.get_line,
            'get_description': self.get_description,
        })

    def get_line(self,line):
        result = []
        result1 = []
        result2 = []
        temp = 0
        for x in line:
            temp += self.process_line_wrap(self.get_description(x), 25)
            if temp < 27:
                result1.append(x)
            else:
                result2.append(x)
        result.append(result1)
        result.append(result2)
        return result

    def process_line_wrap(self, character, char_com):
        result = []
        num_char = 0
        line = ''
        arr1 = []
        arr = character.split('\n')
        for tep1 in arr:
            for tep in tep1.split(' '):
                arr1.append(tep)
        for temp in arr1:
            num_char += len(temp)
            if num_char <= char_com:
                line += ' ' + temp
            else:
                result.append(line)
                num_char = len(temp)
                line  = temp
        result.append(line)
        return len(result)


    def get_description(self, line):
        result = ''
        product_name    = line.product_id and line.product_id.name or ''
        product_barcode = line.product_id and (line.product_id.ean13 and line.product_id.ean13 or '') or '' 
        description = line.name
        if product_barcode:
            if product_name in description:
                kq = description.split(product_name)
                kq = kq[len(kq) - 1]
                if '-' in kq:
                    kq = kq.split('-')
                    kq = '- ' + kq[len(kq) - 1]
                else:
                    kq = ''
                result = '[%s] %s %s'%(product_barcode, product_name, kq)
        else:
            result = description
        return result

report_sxw.report_sxw(
    'report.account.invoice.jmd_pacific_without',
    'account.invoice',
    'addons/crea8s_jmd_pacific_fix/account_print_invoice_without.rml',
    parser=account_invoice_jmd_pacific_without
)

class sale_order_jmd_pacific_without(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_order_jmd_pacific_without, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw(
    'report.sale.order.jmd_pacific_without',
    'sale.order',
    'addons/crea8s_jmd_pacific_fix/sale_order_without.rml',
    parser=sale_order_jmd_pacific_without
)

# class crea8s_purchase_order(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context):
#         super(crea8s_purchase_order, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({'time': time})
# 
# report_sxw.report_sxw('report.crea8s.purchase.order','purchase.order','addons/crea8s_jmd_pacific_fix/order.rml',parser=crea8s_purchase_order,header=False)

# class crea8s_request_quotation(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context):
#         super(crea8s_request_quotation, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({
#             'time': time,
#             'user': self.pool.get('res.users').browse(cr, uid, uid, context)
#         })
# report_sxw.report_sxw('report.crea8s.purchase.quotation','purchase.order','addons/crea8s_jmd_pacific_fix/request_quotation.rml',parser=crea8s_request_quotation,header=False)

class crea8s_picking_jmd(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_picking_jmd, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc,
            'get_total': self.get_total,
            'get_description': self.get_description,
        })

    def get_description(self, line):
        result = ''
        product_name    = line.product_id and line.product_id.name or ''
        product_barcode = line.product_id and (line.product_id.ean13 and line.product_id.ean13 or '') or '' 
        description = line.name 
        if product_barcode:
            if product_name in description:
                kq = description.split(product_name)
                kq = kq[len(kq) - 1]
                if '-' in kq:
                    kq = kq.split('-')
                    kq = '- ' + kq[len(kq) - 1]
                result = '[%s] %s %s'%(product_barcode, product_name, kq)
        else:
            result = line.name
        if not result:
            result = line.name
        return result

    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

    def get_total(self, move_line):
        total = 0
        if move_line:
            total = sum([x.product_uos_qty and x.product_uos_qty or x.product_qty for x in move_line])
        return total

for suffix in ['', '.in', '.out']:
    report_sxw.report_sxw('report.crea8s.stock.picking.list.jmd' + suffix,
                          'stock.picking' + suffix,
                          'addons/crea8s_jmd_pacific_fix/picking.rml',
                          parser=crea8s_picking_jmd,header=False)
