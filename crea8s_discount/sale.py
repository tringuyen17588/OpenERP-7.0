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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import csv
import datetime

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def get_discount_amount(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            if sale.discount_type == 'pc':
                res[sale.id] = sale.discount * sale.amount_untaxed / 100
            elif sale.discount_type == 'fixed':
                res[sale.id] = sale.discount
            else:
                res[sale.id] = 0
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        if line.order_id.discount_type == 'fixed':
            for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit \
                - (line.discount and line.discount or 0.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)
        else:
            for c in self.pool.get('account.tax').compute_all(cr, uid, line.tax_id, line.price_unit \
                * (1-(line.discount or 0.0)/100.0), line.product_uom_qty, line.product_id, line.order_id.partner_id)['taxes']:
                val += c.get('amount', 0.0)
        return val
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = super(sale_order, self)._amount_all(cr, uid, ids, field_name, arg, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.discount_type == 'pc':
                res[order.id]['amount_total'] = (res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'])# * ((100 - order.discount) / 100)
            elif order.discount_type == 'fixed':
                res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']# - order.discount
            else:
                pass
        return res
    
    _columns = {
        'discount': fields.float('Discount Amount'),
        'dis_amount': fields.function(get_discount_amount, string='Discount', type='float'), 
        'discount_type': fields.selection([('pc','Percent(%)'), ('fixed', 'Fixed')], 'Discount Type'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'discount'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='amount_total', help="The total amount."),
    }
    
    def button_dummy_discount(self, cr, uid, ids, context={}):
        line_obj = self.pool.get('sale.order.line')
        for record in self.browse(cr, uid, ids):
            disc_rate = sum([l1.price_unit * l1.product_uom_qty for l1 in record.order_line]) 
            line_ids = [l.id for l in record.order_line]
            if record.discount_type == 'pc':
                line_obj.write(cr, uid, line_ids, {'discount': record.discount and record.discount or 0})
            elif record.discount_type == 'fixed':
                for line in record.order_line:
                    temp = record.discount * line.price_unit * line.product_uom_qty / disc_rate
                    line_obj.write(cr, uid, [line.id], {'discount': temp})
            else:
                for line in record.order_line:
                    line_obj.write(cr, uid, [line.id], {'discount': 0})
        return 1
    
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = 0
            if line.order_id.discount_type == 'pc':
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            elif line.order_id.discount_type == 'fixed':
                price = line.price_unit - (line.discount / line.product_uom_qty)
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
    
    _columns = {
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
        'discount': fields.float('Discount', digits=(16,4)),
    }
    
sale_order_line()