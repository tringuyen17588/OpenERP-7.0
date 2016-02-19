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
from openerp.tools.translate import _

class purchase_requisition_wizard(osv.osv_memory):
    _name = "purchase.requisition.wizard"
    _description = "Purchase Requisition Partner"
    _columns = {
        'from_warehouse': fields.many2one('stock.location', 'From', required=True),
        'to_warehouse': fields.many2one('stock.location', 'To', required=True),
        'purchase_requisition': fields.many2one('purchase.requisition', 'Request', required=True),
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
        
        for order_line in data.purchase_requisition.line_ids:
            stkm_obj.create(cr, uid, {'name': order_line.product_id.name or '',
                'product_id': order_line.product_id.id,
                'product_qty': order_line.box_qty and order_line.box_qty or order_line.product_qty,
                'product_uos_qty': order_line.box_qty and order_line.box_qty or order_line.product_qty,
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