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

import time, datetime
from openerp.osv import fields, osv
from openerp.report import report_sxw
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class product_product(osv.osv):
    _inherit = "product.product"
    _columns = {
        'cprice_sale': fields.float('Sale Cost Price', digits_compute= dp.get_precision('Product Price')),
    }
product_product()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _defaults = {
        'quantity': 1,
        'discount': 0.0,
        'price_unit': 1,
        'account_id': 0,
    }
account_invoice_line()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'revision_note': fields.char('Revision Note', size=256),
    }

    def _prepare_order_picking_in(self, cr, uid, order, context=None):
        
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'in',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            #'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
            'crea8s_vec_ob_ref': order.crea8s_vec_ob_ref,
        }

    def create_pickings_in(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        picking_id = picking_obj.search(cr, uid, [('sale_id', 'in', ids), ('type', '=', 'in')])
        picking_id = picking_id and picking_id[0] or 0
        for order in self.browse(cr, uid, ids):
            if not picking_id:
                picking_id = picking_obj.create(cr, uid, self._prepare_order_picking_in(cr, uid, order, context=context))
                for line in order.order_line:
                    date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)
                    if line.product_id:
                        if line.product_id.type in ('product', 'consu'):
                            move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context))
        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
        
        
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of delivery orders to display
        pick_ids = []
        pick_ids += [picking_id]
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',["+','.join(map(str, pick_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_in_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result
    
    def action_view_po(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        purchase_obj = self.pool.get('purchase.order')
        list_po = []
        for po in purchase_obj.search(cr, uid, [('sale_id', '=', ids[0])], context=context):
            list_po.append(po)
        action_model, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'purchase', 'purchase_form_action'))
        action = self.pool.get(action_model).read(cr, uid, action_id, context=context)
        ctx = eval(action['context'])
        action.update({'context': ctx,
                       'domain': "[('id','in',%s)]" % list_po})
        return action
    
sale_order()

class crea8s_so_2po(osv.osv_memory):
    _name = 'crea8s.so.2po'
    _description = 'Link PO into SO'
    _columns = {
        'name': fields.many2one('sale.order', 'Sale Order'),
        'po_ids': fields.many2many('purchase.order', 'so_2po_rel', 'so_id', 'po_id', 'Purchase Order'),
    }
    
    def generate_po(self, cr, uid, ids, context={}):
        po_obj = self.pool.get('purchase.order')
        for record in self.browse(cr, uid, ids):
            sale_id = record.name and record.name.id or 0
            po_ids = [line.id for  line in record.po_ids]
            po_obj.write(cr, uid, po_ids, {'sale_id': sale_id})
        return 1
    
    def get_sale_id(self, cr, uid, context={}):
        if context.get('sale_id', False):
            return context['sale_id']
        return 0
    
    _defaults = {
        'name': get_sale_id,
    }
    
crea8s_so_2po()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
        'revision_note': fields.char('Revision Note', size=256),
        'sale_id': fields.many2one('sale.order', 'Sale Order'),
    }
purchase_order()
class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        if not pricelist:
            return res
        frm_cur = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
        to_cur = self.pool.get('product.pricelist').browse(cr, uid, [pricelist])[0].currency_id.id
        if product:
            purchase_price = self.pool.get('product.product').browse(cr, uid, product).cprice_sale
            price = self.pool.get('res.currency').compute(cr, uid, frm_cur, to_cur, purchase_price, round=False)
            res['value'].update({'purchase_price': price})
        return res
    
sale_order_line()

class crea8s_invoice_commercial(osv.osv):
    _name = 'crea8s.invoice.commercial'
    _inherit = "mail.thread"
    _order = 'date desc'
    _rec_name = 'number'
    _columns = {
        'date': fields.date('Date'),
        'number': fields.char('No', size=32),
        'bill_to': fields.many2one('res.partner', 'Bill To'),
        'ship_to': fields.many2one('res.partner', 'Ship To'),
        'po_no': fields.char('P.O. No.', size=64),
        'payment_term': fields.many2one('account.payment.term', 'Terms'),
        'ship_term': fields.char('Ship Term', size=256),
        'requestor': fields.char('Requestor', size=256),
        'ship_via': fields.char('Ship Via', size=256),
        'curcy': fields.many2one('res.currency', 'Currency'),
        'line': fields.one2many('crea8s.invoice.commercial.line', 'inv_comc_id', 'Invoice Line'),
#        'total': 
    }
crea8s_invoice_commercial()

class crea8s_invoice_commercial_line(osv.osv):
    _name = 'crea8s.invoice.commercial.line'
    _order = 'item'
    def get_cur_rate(self, cr, uid, context={}):
        if context.get('currency_id', False):
            return self.pool.get('res.currency').browse(cr, uid, context['currency_id']).rate_silent
        return 1
        
    _columns = {
        'item': fields.char('Item No', size=16),
        'name': fields.text('Description'),
        'qty': fields.float('Qty'),
        'rate': fields.float('Rate'),
        'amount': fields.float('Amount'),
        'inv_comc_id': fields.many2one('crea8s.invoice.commercial', 'Invoice Commercial'),
    }
    _defaults = {
        'rate': get_cur_rate,
    }
crea8s_invoice_commercial_line()
class crea8s_invoice_commercial_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_invoice_commercial_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total': self.get_total,
        })
    def get_total(self, obj):
        total = sum([x.amount for x in obj])
        return total        

report_sxw.report_sxw(
    'report.rp_crea8s_invoice_commercial',
    'crea8s.invoice.commercial',
    'addons/crea8s_address_delivery/account_print_invoice.rml',
    parser=crea8s_invoice_commercial_report, header=False
)

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'other_add': fields.text('Opt Delivery Address'),
        'is_add': fields.boolean('Other Address'),
        'inv_comc': fields.many2one('crea8s.invoice.commercial', 'Commercial Invoice'),
    }
stock_picking()

class stock_picking_out(osv.osv):
    _name = "stock.picking.out"
    _inherit = "stock.picking"
    _table = "stock_picking"
    _description = "Delivery Orders"

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        return self.pool.get('stock.picking').search(cr, user, args, offset, limit, order, context, count)

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        return self.pool.get('stock.picking').read(cr, uid, ids, fields=fields, context=context, load=load)

    def check_access_rights(self, cr, uid, operation, raise_exception=True):
        #override in order to redirect the check of acces rights on the stock.picking object
        return self.pool.get('stock.picking').check_access_rights(cr, uid, operation, raise_exception=raise_exception)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        #override in order to redirect the check of acces rules on the stock.picking object
        return self.pool.get('stock.picking').check_access_rule(cr, uid, ids, operation, context=context)

    def _workflow_trigger(self, cr, uid, ids, trigger, context=None):
        #override in order to trigger the workflow of stock.picking at the end of create, write and unlink operation
        #instead of it's own workflow (which is not existing)
        return self.pool.get('stock.picking')._workflow_trigger(cr, uid, ids, trigger, context=context)

    def _workflow_signal(self, cr, uid, ids, signal, context=None):
        #override in order to fire the workflow signal on given stock.picking workflow instance
        #instead of it's own workflow (which is not existing)
        return self.pool.get('stock.picking')._workflow_signal(cr, uid, ids, signal, context=context)

    def message_post(self, *args, **kwargs):
        """Post the message on stock.picking to be able to see it in the form view when using the chatter"""
        return self.pool.get('stock.picking').message_post(*args, **kwargs)

    _columns = {
        'backorder_id': fields.many2one('stock.picking.out', 'Back Order of', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help="If this shipment was split, then this field links to the shipment which contains the already processed part.", select=True),
        'other_add': fields.text('Opt Delivery Address'),
        'is_add': fields.boolean('Other Address'),
        'inv_comc': fields.many2one('crea8s.invoice.commercial', 'Commercial Invoice'),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Ready to Deliver'),
            ('done', 'Delivered'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Deliver: products reserved, simply waiting for confirmation.\n
                 * Delivered: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }
    _defaults = {
        'type': 'out',
    }
    
    def commercial_inv(self, cr, uid, ids, context={}):
        inv_comc_obj = self.pool.get('crea8s.invoice.commercial')
        inv_comc_line_obj = self.pool.get('crea8s.invoice.commercial.line')
        for record in self.browse(cr, uid, ids):
            if record.inv_comc:
                return 1
            sale_id = record.sale_id and record.sale_id or 0
            inv_id = inv_comc_obj.create(cr, uid, {
                'date': record.min_date and record.min_date or 0,
                'number': record.name and record.name or '',
                'bill_to': sale_id and (sale_id.partner_invoice_id and sale_id.partner_invoice_id.id or 0) or 0,
                'ship_to': sale_id and (sale_id.partner_shipping_id and sale_id.partner_shipping_id.id or 0) or 0,
                'po_no': '',
                'payment_term': sale_id and (sale_id.payment_term and sale_id.payment_term.id or 0) or 0,
                'ship_term': '',
                'requestor': '',
                'ship_via': '',
                'curcy': sale_id and (sale_id.currency_id and sale_id.currency_id.id or 0) or 0,
            })
            curr_id = sale_id and (sale_id.currency_id and sale_id.currency_id.id or 0) or 0
            for pick_lines in record.move_lines:
                inv_comc_line_obj.create(cr, uid, { 
                    'item': '',
                    'name': pick_lines.name and pick_lines.name or '',
                    'qty': pick_lines.product_uos_qty and pick_lines.product_uos_qty or pick_lines.product_qty,
                    'rate': curr_id and self.pool.get('res.currency').browse(cr, uid, curr_id).rate_silent or 1,
                    'amount': 0,
                    'inv_comc_id': inv_id,
                })
        return self.pool.get('stock.picking').write(cr, uid, ids, {'inv_comc': inv_id})
    
stock_picking_out()

class crea8s_vector_picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_vector_picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,

        })
    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

for suffix in ['', '.in', '.out']:
    report_sxw.report_sxw('report.crea8s.vector.stock.picking.list' + suffix,
                          'stock.picking' + suffix,
                          'addons/crea8s_address_delivery/picking.rml',
                          parser=crea8s_vector_picking, header=False)
    
class account_analytic_account(osv.osv): 
    _inherit = 'account.analytic.account'
    def auto_warning_email(self, cr, uid, para='', content='', context={}):
        time_search = datetime.datetime.now()
        date_from = datetime.date(time_search.year, time_search.month, time_search.day) - datetime.timedelta(days=30)
        raise osv.except_osv('Warning !', str(date_from)) 
        idd = self.search(cr, uid, [('date', '=', str(date_from))])
        for record in self.browse(cr, uid, idd):
            if record.manager_id:
                content = { 'body': content and content or 'EXP for %s'%record.name,
                            'parent_id': 0,
                            'partner_ids': [record.manager_id.id],
                            'attachment_ids': [], 
                            'subject': 'Notification for Contract'}
                mail_id = self.message_post(cr, uid, [23], type='comment', subtype='mail.mt_comment', context=context, **content)
                self.pool.get('mail.notification')._notify(cr, uid, mail_id, [4], context=context)
        return 1