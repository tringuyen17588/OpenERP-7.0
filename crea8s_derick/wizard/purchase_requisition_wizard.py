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
from openerp.osv.orm import browse_record, browse_null
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import math

class purchase_requisition_wizard(osv.osv_memory):
    _name = "purchase.requisition.wizard"
    _description = "Purchase Requisition Partner"
    _columns = {
        'from_warehouse': fields.many2one('stock.location', 'From', required=True),
        'to_warehouse': fields.many2one('stock.location', 'To', required=True),
        'purchase_requisition': fields.many2one('purchase.requisition', 'Request', required=True),
    }
    
#    def default_from(self, cr, uid, context):
#        result = 0
#        if context.get('active_id'):
#            result = self.pool.get('purchase.requisition').
#        return 1
    
    def default_to(self, cr, uid, context):
        if context.get('active_id'):
            result = self.pool.get('purchase.requisition').browse(cr, uid, context.get('active_id')).warehouse_id \
            and self.pool.get('purchase.requisition').browse(cr, uid, context.get('active_id')).warehouse_id.id or 0 

        return result
    def default_pr(self, cr, uid, context):
        if context.get('active_id'):
            return context.get('active_id')
        return 0

    _defaults = {
#        'from_warehouse': default_from,
        'to_warehouse': default_to,
        'purchase_requisition': default_pr, 
    }

    def create_shipment(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', [])
        data =  self.browse(cr, uid, ids, context=context)[0]
        pick_obj = self.pool.get('stock.picking')
        stkm_obj = self.pool.get('stock.move')
        picking_id = pick_obj.create(cr, uid, {
                'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                'origin': data.purchase_requisition.name,
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'partner_id': 0,
                'invoice_state': 'none',
                'type': 'in',
                'partner_id': 0,
                'purchase_id': 0,
                'company_id': data.purchase_requisition.company_id.id,
                'move_lines' : [],}) 
        print picking_id
        for order_line in data.purchase_requisition.line_ids:
            print stkm_obj.create(cr, uid, {'name': order_line.product_id.name or '',
                'product_id': order_line.product_id.id,
                'qty_others': order_line.box_qty and order_line.box_qty or 0,
                'uom_others': order_line.uom_other and order_line.uom_other.uom_id_ex.id or 0,
                'product_qty': order_line.product_qty and order_line.product_qty or 0,
                'product_uos_qty': order_line.product_qty and order_line.product_qty or order_line.product_qty,
                'product_uom': order_line.product_uom_id.id,
                'product_uos': order_line.product_uom_id.id,
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'date_expected': time.strftime('%Y-%m-%d %H:%M:%S'),
                'location_id': data.from_warehouse.id,
                'location_dest_id': data.to_warehouse.id,
                'picking_id': picking_id,
                'partner_id': 0,
                'move_dest_id': 0,
                'state': 'draft',
                'type':'in',
                'purchase_line_id': 0,
                'company_id': data.purchase_requisition.company_id.id,
                'price_unit': order_line.up})
        
        
        
        return {'type': 'ir.actions.act_window_close'}

purchase_requisition_wizard()

class stock_change_product_qty(osv.osv_memory):
    _inherit = "stock.change.product.qty"
    
    _columns = {
        'uom_others_id': fields.many2one('product.uom', 'UOM Others'),
        'other_qty': fields.float('New Quantity On Hand'),
    }
    
    def onchange_qty_other(self, cr, uid, ids, product_id, qty, uom_other):
        product_obj   = self.pool.get('product.product')
        uom_other_obj = self.pool.get('product.uom.other')
        result = {}
        lst_uom = []
        if product_id:
            product_br = product_obj.browse(cr, uid, product_id)
            lst_uom = [(x.uom_id_ex and x.uom_id_ex.id or -1) for x in product_br.uom_ids] + [product_br.uom_id and product_br.uom_id.id or -1]
        if qty and uom_other:
            uom_oid = uom_other_obj.search(cr, uid, [('uom_id_ex', '=', uom_other),
                                                     ('product_id', '=', product_id)])
            uom_oid = uom_oid and uom_oid[0] or 0
            qty_exchange = 1
            if uom_oid:
                qty_exchange = uom_other_obj.browse(cr, uid, uom_oid).exchange
            if uom_other not in lst_uom:
                result.update({'warning': {'title': 'Warning !', 
                    'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                result.update({'value':{'uom_others_id': product_br.uom_id and product_br.uom_id.id or 0}})
            else:
                result.update({'value':{'new_quantity': qty * qty_exchange}})
        return result
    
    def change_product_qty(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        rec_id = context and context.get('active_id', False)
        assert rec_id, _('Active ID is not set in Context')

        inventry_obj = self.pool.get('stock.inventory')
        inventry_line_obj = self.pool.get('stock.inventory.line')
        prod_obj_pool = self.pool.get('product.product')

        res_original = prod_obj_pool.browse(cr, uid, rec_id, context=context)
        for data in self.browse(cr, uid, ids, context=context):
            if data.new_quantity < 0:
                raise osv.except_osv(_('Warning!'), _('Quantity cannot be negative.'))
            inventory_id = inventry_obj.create(cr , uid, {'name': _('INV: %s') % tools.ustr(res_original.name)}, context=context)
            line_data ={
                'inventory_id' : inventory_id,
                'product_qty' : data.new_quantity,
                'location_id' : data.location_id.id,
                'product_id' : rec_id,
                'product_uom' : res_original.uom_id.id,
                'prod_lot_id' : data.prodlot_id.id,
                'qty_other': (res_original.uom_id.id != data.uom_others_id.id and data.other_qty) and data.other_qty or 0,
                'uom_other': (data.uom_others_id.id != res_original.uom_id.id) and data.uom_others_id.id or res_original.uom_id.id,
                'qty_def':  (data.uom_others_id.id == res_original.uom_id.id) and data.other_qty or 0,
            }
            inventry_line_obj.create(cr , uid, line_data, context=context)

            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)
        return {}
        
stock_change_product_qty()

#    For invoice line
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
        'tax_amount': fields.float('Tax Amount'),
    }
    
account_invoice_line()

class taxes_invoice_line(osv.osv_memory):
    _name = "taxes.invoice.line"
    _description = "Add taxes into Invoice Line"
    
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
        'tax_ids':fields.many2many('account.tax', 'account_tax_invoice4line_rel', 'inv_id', 'tax_id', 'Taxes'),
    }
    _defaults = {
        'name': get_default_invoice,
    }

    def change_taxes(self, cr, uid, ids, context=None):
        inv_ob = self.pool.get('account.invoice')
        inv_line_obj = self.pool.get('account.invoice.line')
        non_tax_account = []
        for record1 in self.browse(cr, uid, ids):
            non_tax_account.append(record1.name.account_id.id)            
            for line1 in record1.name.invoice_line:
                sql7 = ''' Delete from account_invoice_line_tax where invoice_line_id = %s  '''%line1.id
                cr.execute(sql7)
#    Update taxes for invoice line
                for tax in record1.tax_ids:
                    sql6 = ''' Insert into account_invoice_line_tax values(%s,%s)  '''%(line1.id, tax.id)
                    print sql6
                    cr.execute(sql6)
#    Update amount
        for record2 in self.browse(cr, uid, ids):
            non_tax_account.append(record2.name.account_id.id)            
            for line2 in record2.name.invoice_line:
                non_tax_account.append(line2.account_id.id)
                sub_total = inv_line_obj._amount_line(cr, uid, [line2.id], 1, 1, 1).values()[0]
                sql3 = ''' Update account_invoice_line Set tax_amount = %s where id = %s '''%((line2.price_unit * line2.quantity) - sub_total, line2.id)
                cr.execute(sql3)
                inv_ob.button_reset_taxes(cr, uid, [record2.name.id])

        return 1

taxes_invoice_line()

def next_multiple(x, y):
    return math.ceil(x/y)*y

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        for xxx in self.browse(cr, uid, ids):
            for xx in xxx.invoice_line:
                if xx.name == 'Rounding Adjustments':
                    self.pool.get('account.invoice.line').unlink(cr, uid, xx.id)
        res = super(account_invoice, self)._amount_all(cr, uid, ids, name, args, context)
        for invoice in self.browse(cr, uid, ids):
            kk = round(next_multiple(res[invoice.id]['amount_tax'] + res[invoice.id]['amount_untaxed'], 0.05),2) - res[invoice.id]['amount_total']
            if kk:
                self.pool.get('account.invoice.line').copy(cr, uid, invoice.invoice_line[0].id, {'product_id':0, 'name': 'Rounding Adjustments','price_unit': kk, 'quantity': 1, 'invoice_line_tax_id': [], 'qty_others': 1, 'tax_amount': 0})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        for idd in ids:
            if vals.get('amount_tax', False):
                tax_line_obj = self.pool.get('account.invoice.tax')
                tax_lid = tax_line_obj.search(cr, uid, [('invoice_id', '=', idd)])
                if tax_lid: tax_line_obj.write(cr, uid, tax_lid, {'amount': vals.get('amount_tax', 0)}) 
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

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
        'get_tax_partner': fields.boolean('Get Partner Taxes'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.invoice.tax': (_get_invoice_tax, None, 20),
                'account.invoice.line': (_get_invoice_line, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 20),
            },
            multi='all'),
    }

    def button_reset_taxes(self, cr, uid, ids, context=None):
        tax_obj = self.pool.get('account.tax')
        for inv in self.browse(cr, uid, ids):
            for line in inv.invoice_line:
                if line.invoice_line_tax_id:
                    self.pool.get('account.invoice.line').write(cr, uid, [line.id], {'tax_amount': tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)), line.quantity, line.product_id, inv.partner_id)['taxes'][0]['amount']})
        return super(account_invoice,self).button_reset_taxes(cr, uid, ids, context)

account_invoice()