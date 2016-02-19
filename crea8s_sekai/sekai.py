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
import openerp.addons.decimal_precision as dp
import time
import datetime
from datetime import timedelta
from openerp import SUPERUSER_ID
from openerp import netsvc
from decimal import Context


class purchase_wizard(osv.osv_memory):
    _name = 'purchase.wizard'
            
    _columns = {
        'name': fields.many2one('mrp.bom', string='BOM'),
        'mrp_id': fields.many2one('mrp.production', string='Manufacturing Order'),
        'partner_id': fields.many2one('res.partner', string='Partner'),
        'line_id': fields.one2many('purchase.line.wizard', 'parent_id', string='Purchase Line'),
        
    }
    
    def get_name_df(self, cr, uid, context={}):
        if context.get('bom_id', False):
            return context['bom_id']
        return 0

    def get_mo_df(self, cr, uid, context={}):
        if context.get('mrp_id', False):
            return context['mrp_id']
        return 0
    
    def get_line_df(self, cr, uid, context={}):
        result = []
        if context.get('bom_id', False):
            for line in self.pool.get('mrp.bom').browse(cr, uid, context['bom_id']).bom_lines:
                if line.is_use:
                    result.append({'name': line.name and line.name or '', 
                               'product_id': line.product_id and line.product_id.id or 0, 
                               'wh_id': line.des_wh and line.des_wh.id or 0, 
                               'sup_id': line.sup_id and line.sup_id.id or 0,
                               'qty': line.product_qty and line.product_qty or 0, 
                               'parent_id': context.get('bom_id', False),
                               'uom_id': line.product_uom and line.product_uom.id or 0,
                               'date_order': line.date_stop})
        return result 
    
    _defaults = {
        'name': get_name_df,
        'line_id': get_line_df,
        'mrp_id': get_mo_df,
    }
    
    def _seller_details(self, cr, uid, requisition_line, supplier, context=None):
        product_uom = self.pool.get('product.uom')
        pricelist = self.pool.get('product.pricelist')
        product = requisition_line.product_id
        default_uom_po_id = product.uom_po_id.id
        qty = product_uom._compute_qty(cr, uid, requisition_line.uom_id.id, requisition_line.qty, default_uom_po_id)
        seller_qty = False
        for product_supplier in product.seller_ids:
            if supplier.id ==  product_supplier.name and qty >= product_supplier.qty:                
                seller_qty = product_supplier.qty
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        seller_price = pricelist.price_get(cr, uid, [supplier_pricelist.id], product.id, qty, False, {'uom': default_uom_po_id})[supplier_pricelist.id]
        if seller_qty:
            qty = max(qty,seller_qty)
        wh_id = requisition_line.wh_id and requisition_line.wh_id.id or 0
        date_order =  requisition_line.date_order or datetime.datetime.now()
#         date_planned = self._planned_date(requisition_line.requisition_id, seller_delay)
        return seller_price, qty, default_uom_po_id, wh_id, date_order
    
    def generate_purchase(self, cr, uid, ids, context={}):
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        mo_obj = self.pool.get('mrp.production')
        mo_id = 0
        if context.get('mrp_id', False):
            mo_id = context['mrp_id']
        if mo_id:
            mo_id = ' - ' + mo_obj.browse(cr, uid, mo_id).name
        mo_id = mo_id and  mo_id or ''
        #raise osv.except_osv('warning', mo_id)
        for requisition in self.browse(cr, uid, ids, context=context):
            lst_temp = []
            lst_temp1 = []
            for l in requisition.line_id:
                if l.sup_id:
                    if l.sup_id.id not in lst_temp1:
                        lst_temp.append({'location': l.wh_id and l.wh_id.lot_stock_id.id or 1,
                                          'wh_id': l.wh_id and l.wh_id.id or 1,
                                          'sup_id': l.sup_id and l.sup_id.id or 0})
                        lst_temp1.append(l.sup_id.id)
            for partner_id in lst_temp:
                supplier = res_partner.browse(cr, uid, partner_id['sup_id'], context=context)
                supplier_pricelist = supplier.property_product_pricelist_purchase or False 
                purchase_id = purchase_order.create(cr, uid, {
                            'origin': requisition.name.name + mo_id,
                            'mrp_id': requisition.mrp_id and requisition.mrp_id.id or 0, 
                            'partner_id': supplier.id,
                            'mrp_id': requisition.mrp_id and requisition.mrp_id.id or 0,
                            'pricelist_id': supplier_pricelist.id,
                            'location_id': partner_id['location'],
                            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                            'requisition_id':requisition.id,
                            'notes': 'Created by BOM',
                            'warehouse_id': partner_id['wh_id'],
                            'reason': '-',
                })
                for line in requisition.line_id:
                    if line.sup_id.id == partner_id['sup_id']:
                        product = line.product_id
                        seller_price, qty, default_uom_po_id, partner_id['wh_id'], date_order = self._seller_details(cr, uid, line, supplier, context=context)
                        taxes_ids = product.supplier_taxes_id
                        taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                        purchase_order_line.create(cr, uid, {
                            'order_id': purchase_id,
                            'name': product.partner_ref,
                            'product_qty': qty,
                            'product_id': product.id,
                            'product_uom': default_uom_po_id,
                            'price_unit': seller_price,
                            'des_wh': partner_id['wh_id'],
                            'date_planned': date_order,
                            'taxes_id': [(6, 0, taxes)],
                        }, context=context)
                sql = ''' Insert into bom_po_rel values(%s,%s) '''%(requisition.name.id,purchase_id)
                cr.execute(sql)
        return 1
    
purchase_wizard()

class purchase_line_wizard(osv.osv_memory):
    _name = 'purchase.line.wizard'
            
    _columns = {
        'name': fields.char('Description', size=256),
        'product_id': fields.many2one('product.product', string='Product'),
        'uom_id': fields.many2one('product.uom', string='UOM'),
        'wh_id': fields.many2one('stock.warehouse', string='Warehouse'),
        'qty': fields.float('Quantity'),
        'date_order': fields.date('Date Required'),
        'sup_id': fields.many2one('res.partner', 'Supplier'),
        'parent_id': fields.many2one('purchase.wizard', string='Purchase'),
        
    }
        
purchase_line_wizard()

class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'
            
    _columns = {
        'des_wh': fields.many2one('stock.warehouse',string='Warehouse'),
        'stkm_id': fields.many2one('stock.move', 'Stock Move'),
        'status_mov': fields.related('stkm_id', 'state', type='char', string='Shipping Status'),
#        'status_mov': fields.related('stkm_id', 'rate', type='float', string='Exchange Rate', digits=(12,6)),
        'is_use': fields.boolean('Select'),
        'chk_all': fields.boolean('Check All'),
        'sup_id': fields.many2one('res.partner', 'Supplier'),
        'po_ids': fields.many2many('purchase.order', 'bom_po_rel', 'bom_id', 'po_id', 'Request For Quotation'),
        'incoming_ids': fields.many2many('stock.picking', 'crea8s_bom_pick_rel', 'bom_id', 'pick_id', 'Picking List'),
        'note': fields.text('Note'),

    }

    def get_stock_move(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            lines = [{'prod_id': 0, 'bom_id': 0}]
            if record.bom_lines:
                lines = [{'prod_id': x.product_id.id, 'bom_id': x.id} for x in record.bom_lines]
            for po in record.po_ids:
                for pick in po.picking_ids:
                    for move in pick.move_lines:
                        for kk in lines:
                            if move.product_id.id == kk['prod_id']:
                                self.write(cr, uid, kk['bom_id'],{'stkm_id': move.id})
                
        return 1

    def get_qty_prod(self, cr, uid, context={}):
        if context.get('qty_bom', False):
            return context['qty_bom']
        return 1
   
    def get_squence(self, cr, uid, context={}):
        if context.get('cr8s_line', False):
            return len(context['cr8s_line']) + 1
        return 1
    
    def onchange_bom_compo(self, cr, uid, ids, bom_line, context={}):
        if not context.get('squence', False):
            context['squence'] = 1
        else:
            context['squence'] += 1
        return {'value': {}}

    def onchange_product_id(self, cr, uid, ids, product_id, name, context={}):
        result = super(mrp_bom, self).onchange_product_id(cr, uid, ids, product_id, name, context)
        if context.has_key('mrp_name'):
            if context.get('mrp_name', False):
                result['value']['name'] = context.get('mrp_name', False) + ' BOM'
        return result

    _defaults = {
        'product_qty': get_qty_prod,
        'sequence': get_squence,
    }
    def _seller_details(self, cr, uid, requisition_line, supplier, context=None):
        product_uom = self.pool.get('product.uom')
        pricelist = self.pool.get('product.pricelist')
        product = requisition_line.product_id
        default_uom_po_id = product.uom_po_id.id
        qty = product_uom._compute_qty(cr, uid, requisition_line.product_uom.id, requisition_line.product_uos_qty and requisition_line.product_uos_qty or requisition_line.product_qty, default_uom_po_id)
        seller_qty = False
        for product_supplier in product.seller_ids:
            if supplier.id ==  product_supplier.name and qty >= product_supplier.qty:                
                seller_qty = product_supplier.qty
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        seller_price = pricelist.price_get(cr, uid, [supplier_pricelist.id], product.id, qty, False, {'uom': default_uom_po_id})[supplier_pricelist.id]
        if seller_qty:
            qty = max(qty,seller_qty)
        wh_id = requisition_line.des_wh and requisition_line.des_wh.id or 0
        date_order =  datetime.datetime.now()
#         date_planned = self._planned_date(requisition_line.requisition_id, seller_delay)
        return seller_price, qty, default_uom_po_id, wh_id, date_order
    
    def generate_purchase(self, cr, uid, ids, context={}):
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        mo_obj = self.pool.get('mrp.production')
        mo_id = 0
        if context.get('mrp_id', False):
            mo_id = context['mrp_id']
        if mo_id:
            mo_id = ' - ' + mo_obj.browse(cr, uid, mo_id).name
        mo_id = mo_id and  mo_id or ''
        #raise osv.except_osv('warning', mo_id)
        for requisition in self.browse(cr, uid, ids, context=context):
            lst_temp = []
            lst_temp1 = []
            for l in requisition.bom_lines:
                if l.sup_id and l.is_use:
                    if l.sup_id.id not in lst_temp1:
                        lst_temp.append({'location': l.des_wh and l.des_wh.lot_stock_id.id or 1,
                                          'wh_id': l.des_wh and l.des_wh.id or 1,
                                          'sup_id': l.sup_id and l.sup_id.id or 0})
                        lst_temp1.append(l.sup_id.id)
            for partner_id in lst_temp:
                supplier = res_partner.browse(cr, uid, partner_id['sup_id'], context=context)
                supplier_pricelist = supplier.property_product_pricelist_purchase or False 
                purchase_id = purchase_order.create(cr, uid, {
                            'origin': requisition.name + mo_id,
                            'mrp_id': context.get('mrp_id', 0), 
                            'partner_id': supplier.id,
                            'pricelist_id': supplier_pricelist.id,
                            'location_id': partner_id['location'],
                            'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                            'requisition_id':requisition.id,
                            'notes': 'Created by BOM',
                            'warehouse_id': partner_id['wh_id'],
                            'reason': '-',
                })
                for line in requisition.bom_lines:
                    if line.sup_id.id == partner_id['sup_id'] and line.is_use:
                        product = line.product_id
                        seller_price, qty, default_uom_po_id, partner_id['wh_id'], date_order = self._seller_details(cr, uid, line, supplier, context=context)
                        taxes_ids = product.supplier_taxes_id
                        taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                        purchase_order_line.create(cr, uid, {
                            'order_id': purchase_id,
                            'name': product.partner_ref,
                            'product_qty': qty,
                            'product_id': product.id,
                            'product_uom': default_uom_po_id,
                            'price_unit': 0,
                            'des_wh': partner_id['wh_id'],
                            'date_planned': date_order,
                            'taxes_id': [(6, 0, taxes)],
                        }, context=context)
                sql = ''' Insert into bom_po_rel values(%s,%s) '''%(requisition.id,purchase_id)
                cr.execute(sql)
        return 1
    
    def check_all(self, cr, uid, ids, check_all):
        if ids:
            if check_all:
                print 'cba'
                for record in self.browse(cr, uid, ids):
                    lst_component = [x.id for x in record.bom_lines]
                    self.write(cr, uid, lst_component, {'is_use': 1})
            else:
                print 'abc'
                for record in self.browse(cr, uid, ids):
                    lst_component = [x.id for x in record.bom_lines]
                    self.write(cr, uid, lst_component, {'is_use': 0})
        return {'value': {}}

    def write(self, cr, uid, ids, vals, context=None):
        check_all = 0
        if not vals.get('is_use', False):
            return super(mrp_bom, self).write(cr, uid, ids, vals, context=context)
        mrp_production_obj = self.pool.get('mrp.production')
#        raise osv.except_osv('check !', ids)
        mrp_ids = mrp_production_obj.search(cr, uid, [('bom_id', 'in', ids)])
        res_group = self.pool.get('res.groups') 
        group_id_ma = res_group.search(cr, uid, [('name', '=', 'Select line')])
        group_h = [x.id for x in self.pool.get('res.users').browse(cr, uid, uid).groups_id]
        if group_id_ma not in group_h:
            vals.update({'is_use': 1})
        if mrp_ids:
            for idd in mrp_ids:
                wf_service = netsvc.LocalService("workflow")
                self.pool.get('mrp.production').chk_bom_created(cr, uid, [idd])
                wf_service.trg_validate(uid, 'mrp.production', idd, 'bom_created', cr)
        if vals.get('chk_all', False):
            check_all = vals['chk_all']
        if check_all:
            for record in self.browse(cr, uid, ids):
                lst_component = [x.id for x in record.bom_lines]
                self.write(cr, uid, lst_component, {'is_use': 1})
        else:
            for record in self.browse(cr, uid, ids):
                lst_component = [x.id for x in record.bom_lines]
                self.write(cr, uid, lst_component, {'is_use': 0})
        return  super(mrp_bom, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context=None):
        mrp_production_obj = self.pool.get('mrp.production')
        if vals.get('bom_id', False):
            mrp_ids = mrp_production_obj.search(cr, uid, [('bom_id', '=', vals['bom_id'])])
            #raise osv.except_osv('kiemtra', '%s'%mrp_ids)
            if mrp_ids:
                for idd in mrp_ids:
                    wf_service = netsvc.LocalService("workflow")
                    #wf_service.trg_validate(uid, 'mrp.production', idd, 'bom_created_act', cr)
                    mrp_production_obj.write(cr, uid, [idd], {'state': 'bom_created'})
                    wf_service.trg_validate(uid, 'mrp.production', idd, 'bom_created', cr)
        return super(mrp_bom, self).create(cr, uid, vals, context)

    def generate_po(self, cr, uid, ids, context={}):
        self.generate_purchase(cr, uid, ids, context)
        return 1
#     {
#             
#             'name': 'Request for Quotation',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'purchase.wizard',
#             
#             'type': 'ir.actions.act_window',
#             'nodestroy': True,
#             'target': 'new',
#         }
    
    #    Generate Incoming Shipment
    #    Change information before create a picking list
    def generate_order_picking(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            lst_temp = []
            lst_temp1 = []
            lst_date = []
            for l in record.bom_lines:
                if l.is_use:
                    if l.sup_id.id not in lst_temp1:
                        lst_temp.append({'location': l.des_wh and l.des_wh.lot_stock_id.id or 1,
                                          'wh_id': l.des_wh and l.des_wh.id or 1,
                                          'sup_id': l.sup_id and l.sup_id.id or 0,
                                          'date': l.date_stop and l.date_stop or '',
                                          'name': '[%s] %s'%(l.product_id.default_code and l.product_id.default_code or '', l.product_id.name and l.product_id.name or ''),
                                          'uom': l.product_uom and l.product_uom.id or 0,
                                          'prod_id': l.product_id and l.product_id.id or 0,
                                          'qty': l.product_qty and l.product_qty or l.product_uos})
                    lst_temp1.append(l.des_wh and l.des_wh.id or 1,)
                    lst_date.append(l.date_stop)
            pick_id = self.pool.get('stock.picking').create(cr, uid, {
                    'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                    'origin': record.name,
                    'date': min(lst_date),
                    'mrp_id': context.get('mrp_id', 0),
                    'partner_id': 0,
                    'invoice_state': 'none',
                    'type': 'in',            
                    'company_id': record.company_id.id,
                    'move_lines' : [],
                })
            sql = ''' Insert into crea8s_bom_pick_rel values(%s,%s) '''%(record.id,pick_id)
            cr.execute(sql)
            for info in lst_temp:
                self.pool.get('stock.move').create(cr, uid, {
                    'name': info.get('name', ''),
                    'product_id': info.get('prod_id', 0),
                    'product_qty': info.get('qty', 0),
                    'product_uos_qty': info.get('qty', 0),
                    'product_uom': info.get('uom', 0),
                    'product_uos': info.get('uom', 0),
                    'date': info.get('date', ''),
                    'date_expected': info.get('date', ''),
                    'location_id': self.pool.get('res.partner').browse(cr, uid, info['sup_id']).property_stock_supplier.id,
                    'location_dest_id': info.get('location', 0),
                    'picking_id': pick_id,
                    'partner_id': info.get('sup_id', 0),
                    'move_dest_id': 0,
                    'state': 'draft',
                    'type':'in',
                    'purchase_line_id': 0,
                    'company_id': record.company_id.id,
                    'price_unit': 0,
                })
        return 1
    
mrp_bom()

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def _get_date_between(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        line_obj = self.pool.get('crea8s.sekai.line')
        for record in self.browse(cr, uid, ids, context=context):
            result[record.id] = 0
        return result

    _columns = {
        'note': fields.text('Note'),
        'time_comp':fields.function(_get_date_between, string='Time Taken'),
    }
mrp_production_workcenter_line()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
            
    _columns = {
        'des_wh': fields.many2one('stock.warehouse',string='Warehouse'),
    }    

purchase_order_line()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
            
    _columns = {
        'mrp_id': fields.many2one('mrp.production',string='Manufacturing Order'),
        'reason': fields.text('Reason'),
        'date_required': fields.date('Date Required'),
        'job_no': fields.many2one('mrp.production', 'Job No'),
        'state': fields.selection([
        ('draft', 'Request For Quotation'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], 'Status', readonly=True, help="The status of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' status. Then the order has to be confirmed by the user, the status switch to 'Confirmed'. Then the supplier must confirm the order to change the status to 'Approved'. When the purchase order is paid and received, the status becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the status becomes in exception.", select=True),
    }
#    Change information before create a picking list
    def _prepare_order_picking(self, cr, uid, order, context=None):
        result = super(purchase_order, self)._prepare_order_picking(cr, uid, order, context=context)
        return {
            'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
            'origin': order.name + ((order.origin and (':' + order.origin)) or ''),
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'mrp_id': order.mrp_id and order.mrp_id.id or 0,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'invoice_state': '2binvoiced' if order.invoice_method == 'picking' else 'none',
            'type': 'in',
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'purchase_id': order.id,
            'company_id': order.company_id.id,
            'move_lines' : [],
        }
#    Change information before create all line for picking
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        result = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context)
        return {
            'name': order_line.name or '',
            'product_id': order_line.product_id.id,
            'product_qty': order_line.product_qty,
            'product_uos_qty': order_line.product_qty,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order_line.des_wh and order_line.des_wh.lot_stock_id.id or order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id or order.partner_id.id,
            'move_dest_id': order_line.move_dest_id and order_line.move_dest_id.id or 0,
            'state': 'draft',
            'type':'in',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': order_line.price_unit
        }

    def create(self, cr, uid, vals, context=None):
        #    List Module
        cr.execute('''  select id from ir_module_category where name = 'Purchases' ''')
        kq1 = cr.dictfetchall()
        kq1 = kq1 and [x['id'] for x in kq1] or []
        #    List Group 
        cr.execute('''  select id from res_groups where category_id = %s '''%str(kq1[0]))
        kq2 = cr.dictfetchall()
        kq2 = kq2 and [x1['id'] for x1 in kq2] or []
        #    List User
        group_obj = self.pool.get('res.groups')
        lst_result = []
        for group in kq2:
            usrs = [x2.partner_id.id for x2 in group_obj.browse(cr, uid, group).users]
            lst_result += usrs
        lst_result = list(set(lst_result))
        vals.update({'message_follower_ids': [(6, 0, lst_result)]})
        result = super(purchase_order, self).create(cr, uid, vals, context)
        return result
    
purchase_order()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    def total_calc(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for prod in self.browse(cr, uid, ids, context=context):
            kqq = 0
            for wc in prod.move_lines:
                kqq += wc.product_qty
            result[prod.id] = kqq
        return result
    _columns = {
        'mrp_id': fields.many2one('mrp.production',string='Manufacturing Order'),
        'indicate_total': fields.function(total_calc, type='float', string='Indicate Qty Receive'),
    }
#    Check all picking list related with MO in this picking and change status of MO. 
    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S')})
        for record in self.browse(cr, uid, ids):
            if record.mrp_id:
                picking_list_id = self.search(cr, uid, [('mrp_id', '=', record.mrp_id.id),
                                                        ('id', '!=', record.id),
                                                        ('state', '!=', 'done')])
                if not picking_list_id:
                    wf_service = netsvc.LocalService("workflow")
        return True
stock_picking()

class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    def total_calc(self, cr, uid, ids, prop, unknow_none, context=None):
        result = {}
        for prod in self.browse(cr, uid, ids, context=context):
            kqq = 0
            for wc in prod.move_lines:
                kqq += wc.product_qty
            result[prod.id] = kqq
        return result
    _columns = {
        'mrp_id': fields.many2one('mrp.production',string='Manufacturing Order'),
        'indicate_total': fields.function(total_calc, type='float', string='Qty Ordered'),
        'state': fields.selection(
            [('draft', 'Draft'),
            ('auto', 'Waiting Another Operation'),
            ('confirmed', 'Waiting Availability'),
            ('assigned', 'Not Received'),
            ('done', 'Received'),
            ('cancel', 'Cancelled'),],
            'Status', readonly=True, select=True,
            help="""* Draft: not confirmed yet and will not be scheduled until confirmed\n
                 * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n
                 * Waiting Availability: still waiting for the availability of products\n
                 * Ready to Receive: products reserved, simply waiting for confirmation.\n
                 * Received: has been processed, can't be modified or cancelled anymore\n
                 * Cancelled: has been cancelled, can't be confirmed anymore"""),
    }

    def schedule_send_email(self, cr, uid, ids=False, context={}):
        mail_compose = self.pool.get('stock.picking.in')
        time_search = datetime.datetime.now()
        date_from = datetime.datetime(time_search.year, time_search.month, time_search.day, 0,0,0)
        date_to = datetime.datetime(time_search.year, time_search.month, time_search.day, 23,59,59)
        idd = mail_compose.search(cr, uid, [('min_date', '>=', str(date_from)),
                                            ('min_date', '<=', str(date_to)),
                                            ('type', '=', 'in')])
        for record in self.browse(cr, uid, idd):
            content = { 'body': 'You will receive incomming shipment %s'%record.name,
                        'parent_id': 0,
                        'partner_ids': [4],
                        'attachment_ids': [],
                        'report_template': 'stock.picking.list.in', 
                        'subject': 'Notification for Shipment'}
            mail_id = mail_compose.message_post(cr, uid, [23], type='comment', subtype='mail.mt_comment', context=context, **content)
            self.pool.get('mail.notification')._notify(cr, uid, mail_id, [4], context=context)
    
stock_picking_in()


class change_mrp_production(osv.osv_memory):
    _name = 'change.mrp.production'
    _columns = {
        'name': fields.float('Quantity'),
    }
    def ok_fnc(self, cr, uid, ids, context={}):
        mrp_obj = self.pool.get('mrp.production')
        bom_obj = self.pool.get('mrp.bom')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')

        for record in self.browse(cr, uid, ids):
            production = mrp_obj.browse(cr, uid, context['active_id']) 
            status = mrp_obj.browse(cr, uid, context['active_id']).state
            if status != 'done':
                mrp_obj.write(cr, uid, [context['active_id']], {'product_qty': record.name, 'product_uos_qty': record.name})
            if status != 'bom_created':
                bom_point = production.bom_id
                bom_id = production.bom_id.id
                if not bom_point:
                    bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, [])
                    if bom_id:
                        bom_point = bom_obj.browse(cr, uid, bom_id)
                        routing_id = bom_point.routing_id.id or False
                        self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})
                factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
                res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, [], routing_id=production.routing_id.id)
                qty1 = record.name
                for rs in production.move_created_ids2:
                    if rs.product_id.id == production.product_id.id:
                        qty1 -= rs.product_qty and rs.product_qty or 0
                for rs1 in production.move_created_ids:
                    if rs1.product_id.id == production.product_id.id:
                            move_obj.write(cr, uid, [rs1.id], {'product_qty': qty1})
                print res
                
                for x in res[0]:
                    qty = 0
                    for z in production.move_lines2:
                        if x['product_id'] == z.product_id.id:
                            qty -= z.product_qty and z.product_qty or 0
                    for y in production.move_lines:
                        if x['product_id'] == y.product_id.id:
                            qty += x['product_qty']
                            move_obj.write(cr, uid, [y.id], {'product_qty': qty})                
        return 1
        
        
change_mrp_production()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _order = 'date_planned desc'

    def get_price_revenue(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids):
            res[record.id] = 0
            if record.product_id:
                res[record.id] = record.product_id.list_price * record.product_qty
        return res
    
    def change_qty(self, cr, uid, ids, context={}):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Change Quantity',
            'res_model': 'change.mrp.production',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': ids[0]},
            'nodestroy': True,
        }

    def get_shiping_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids):
            res[record.id] = 0
            kq = 0
            if record.bom_id.po_ids:
                for po in record.bom_id.po_ids:
                    for pick in po.picking_ids:
                        if pick.state != 'done':
                            kq += 1
            if not kq:
                res[record.id] = 0
            else:
                res[record.id] = 1
        return res

    _columns = {
        'note': fields.text('Note'),
        'date_required': fields.datetime('Date Required'),
        'partner_id': fields.many2one('res.partner', 'Customer'),
        'standard_price': fields.float('Sale Price', digits_compute=dp.get_precision('Product Price'), groups="base.group_user"),
        'sale_revenue': fields.function(get_price_revenue, type="float", digits_compute=dp.get_precision('Account'), string="Job Value (S$)"),
        'shipping_state': fields.function(get_shiping_state, type="boolean", string="Shipping State"),
        'state': fields.selection(
            [('draft', 'New'), ('cancel', 'Cancelled'), ('picking_except', 'Picking Exception'), ('bom_created', 'BOM Created'), ('confirmed', 'Awaiting Raw Materials'),
                ('ready', 'Ready to Produce'), ('in_production', 'Production Started'), ('done', 'Done')],
            string='Status', readonly=True,
            track_visibility='onchange',
            help="When the production order is created the status is set to 'Draft'.\n\
                If the order is confirmed the status is set to 'Waiting Goods'.\n\
                If any exceptions are there, the status is set to 'Picking Exception'.\n\
                If the stock is available then the status is set to 'Ready to Produce'.\n\
                When the production gets started then the status is set to 'In Production'.\n\
                When the production is over, the status is set to 'Done'."),
    }

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        result = super(mrp_production, self).product_id_change(cr, uid, ids, product_id, context=context)
        if product_id:
            prod_obj = self.pool.get('product.product')
            result['value'].update({'standard_price': prod_obj.browse(cr, uid, product_id).list_price})
        else:
            result['value'].update({'standard_price': 0})
        return result

    def create_po(self, cr, uid, ids, production):
        
        return

    def schedule_send_email(self, cr, uid, ids=False, context={}):
        mail_compose = self.pool.get('mrp.production')
        time_search = datetime.datetime.now()
        date_from = datetime.datetime(time_search.year, time_search.month, time_search.day, 0,0,0)
        date_from = date_from - timedelta(days=2)
        date_to = datetime.datetime(time_search.year, time_search.month, time_search.day, 23,59,59)
        date_to = date_to - timedelta(days=2)
        idd = mail_compose.search(cr, uid, [('date_required', '>=', str(date_from)),
                                            ('date_required', '<=', str(date_to)), ('state', '!=', 'done')])
        for record in self.browse(cr, uid, idd):
            content = { 'body': ''' This is a automated reminder email that Job Order %s (Date Required
%s) will be due soon.


Product: %s
Customer: %s 
Product Quantity: %s Unit(s) '''%(record.name, record.date_required, record.product_id.name_template, record.partner_id.name, record.product_qty),
                        'parent_id': 0,
                        'partner_ids': [4],
                        'attachment_ids': [], 
                        'subject': ''' Job Order %s (Date Required %s) due soon '''%(record.name, record.date_required)}
            mail_id = mail_compose.message_post(cr, uid, record.id, type='comment', subtype='mail.mt_comment', context=context, **content)
            self.pool.get('mail.notification')._notify(cr, uid, mail_id, [4], context=context)

    def chk_bom_created(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            if record.bom_id:
                if len(record.bom_id.bom_lines) >= 0:
                    self.write(cr, uid, [record.id], {'state': 'bom_created'})
        return 1

    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('standard_price'):
            for record in self.browse(cr, uid, ids):
                self.pool.get('product.product').write(cr, uid, [record.product_id.id], {'list_price': vals['standard_price']})
        return super(mrp_production, self).write(cr, uid, ids, vals, context)

    def validate_wfl_again(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_create(uid, 'mrp.production', ids[0], cr)
        return 1
    
    def delete_wfl_again(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_delete(uid, 'mrp.production', ids[0], cr)
        return 1

    def create(self, cr, uid, vals, context=None):
        if vals.get('bom_id', False):
            bom_obj = self.pool.get('mrp.bom')
            if len(bom_obj.browse(cr, uid, vals['bom_id']).bom_lines) >= 0:
                vals.update({'state': 'bom_created'})
                result = super(mrp_production, self).create(cr, uid, vals, context)
                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_create(uid, 'mrp.production', result, cr, context=None)
                self.pool.get('mrp.production').chk_bom_created(cr, uid, [result])
                wf_service.trg_validate(uid, 'mrp.production', result, 'bom_created', cr)
                return result
        return super(mrp_production, self).create(cr, uid, vals, context)

    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            if not production.bom_id.bom_lines:
                raise osv.except_osv('Warning!', 'Please check again your bill of material!')
            p_ids = prod_line_obj.search(cr, SUPERUSER_ID, [('production_id', '=', production.id)], context=context)
            prod_line_obj.unlink(cr, SUPERUSER_ID, p_ids, context=context)
            w_ids = workcenter_line_obj.search(cr, SUPERUSER_ID, [('production_id', '=', production.id)], context=context)
            workcenter_line_obj.unlink(cr, SUPERUSER_ID, w_ids, context=context)

            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)

    def test_if_product(self, cr, uid, ids):
        """
        @return: True or False
        """
        res = True
        for production in self.browse(cr, uid, ids):
            if not production.bom_id.bom_lines:
                raise osv.except_osv('Warning!', 'Please check again your bill of material!')
            if not production.product_lines:
                if not self.action_compute(cr, uid, [production.id]):
                    res = False
            if not production.routing_id:
                raise osv.except_osv('Warning!', 'Please choose routing before confirm this Order!')
        return res

    def _dest_id_default_fp(self, cr, uid, ids, context=None):
        try:
            location_id = self.pool.get('stock.location').search(cr, uid, [('is_finish_prod', '=', True)])
        except:
            location_id = False
        location_id = location_id and location_id[0] or 0
        return location_id

    def _dest_id_default_rm(self, cr, uid, ids, context=None):
        try:
            location_id = self.pool.get('stock.location').search(cr, uid, [('is_raw_material', '=', True)])
        except:
            location_id = False
        location_id = location_id and location_id[0] or 0
        return location_id

    _defaults = {
        'location_dest_id': _dest_id_default_fp,
        'location_src_id': _dest_id_default_rm,
    }
    
mrp_production()

class mrp_routing(osv.osv):
    _inherit = 'mrp.routing'
    _order = 'id desc'
    _columns = {
        'user_create': fields.many2one('res.users', 'Created User'),
    }

    def get_df_name(self, cr, uid, context={}):
        if context.get('mrp_id', False):
            return self.pool.get('mrp.production').browse(cr, uid, context['mrp_id']).name + ' R'
        if context.get('mrp_name', False):
            return context.get('mrp_name', False) + ' R'
        return ''

    def get_created_user(self, cr, uid, context={}):
        return uid

    _defaults = {
        'name': get_df_name,
        'user_create': get_created_user,
    }

mrp_routing()

class stock_location(osv.osv):
    _inherit = "stock.location"
    _columns = {
        'is_finish_prod': fields.boolean('Finished Product'),
        'is_raw_material': fields.boolean('Raw Material'),
    }

stock_location()

class mrp_product_produce(osv.osv_memory):
    _inherit = "mrp.product.produce"
    _columns = {
     'mode': fields.selection([('consume_produce', 'Completion of Production'),
                                  ('consume', 'Consume Only')], 'Mode', required=True,
                                  help="'Consume only' mode will only consume the products with the quantity selected.\n"
                                        "'Consume & Produce' mode will consume as well as produce the products with the quantity selected "
                                        "and it will finish the production order when total ordered quantities are produced."),
    }
    def get_mode(self, cr, uid, context={}):
        if context.get('mode_df', False):
            if context['mode_df'] == 'in_production':
                return 'consume_produce'
        return 'consume'
    
    _defaults = {
         'mode': get_mode
    }
mrp_product_produce()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
        'warehouse_id': fields.related('picking_id', 'purchase_id', 'warehouse_id', type='many2one', relation='stock.warehouse', string='Warehouse'),
    }
stock_move()
from openerp.report import report_sxw

class crea8s_po_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_po_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.crea8s.purchase.order.sekai','purchase.order','addons/crea8s_sekai/order.rml',parser=crea8s_po_order)

class crea8s_workcenter(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_workcenter, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time})

report_sxw.report_sxw('report.crea8s.workcenter.sekai','mrp.routing.workcenter','addons/crea8s_sekai/workcenter.rml',parser=crea8s_workcenter)
