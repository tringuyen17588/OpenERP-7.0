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

from openerp import netsvc
from openerp.osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        properties = []
        bom_point = line.product_id.bom_ids
        bom_point = bom_point and bom_point[0] or 0
        bom_id = line.product_id.bom_ids
        bom_id = bom_id and bom_id[0] or 0
        if not bom_point:            
            if bom_id:
                bom_point = bom_obj.browse(cr, uid, bom_id)

        if not bom_id:
            result = [{
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,}]
            return result
            
        factor = uom_obj._compute_qty(cr, uid, line.product_uom.id, (line.product_uos and line.product_uos_qty) or line.product_uom_qty, bom_point.product_uom.id)
        res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=0)
        result = []
        for x in res[0]:
            x.update({  
                        'picking_id': picking_id,
                        'date': date_planned,
                        'date_expected': date_planned,
                        'product_packaging': line.product_packaging.id,
                        'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
                        'location_id': location_id,
                        'location_dest_id': output_id,
                        'sale_line_id': line.id,
                        'tracking_id': False,
                        'state': 'draft',
                        #'state': 'waiting',
                        'company_id': order.company_id.id,
                        'price_unit': line.product_id.standard_price or 0.0})
            result.append(x)
        return result
    
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        properties = []
        bom_point = line.product_id.bom_ids
        bom_point = bom_point and bom_point[0] or 0
        bom_id = line.product_id.bom_ids
        bom_id = bom_id and bom_id[0] or 0
        if not bom_point:            
            if bom_id:
                bom_point = bom_obj.browse(cr, uid, bom_id)

        if not bom_id:
            return [{
            'name': line.name,
            'origin': order.name,
            'date_planned': date_planned,
            'product_id': line.product_id.id,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty)\
                    or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
            'procure_method': line.type,
            'move_id': move_id,
            'company_id': order.company_id.id,
            'note': line.name,
            'property_ids': [(6, 0, [x.id for x in line.property_ids])],}]
        factor = uom_obj._compute_qty(cr, uid, line.product_uom.id, (line.product_uos and line.product_uos_qty) or line.product_uom_qty, bom_point.product_uom.id)
        res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=0)
        result = []
        for x in res[0]:
            x.update({  'origin': order.name,
                        'date_planned': date_planned,
                        'location_id': order.shop_id.warehouse_id.lot_stock_id.id,
                        'procure_method': line.type,
                        'move_id': move_id,
                        'company_id': order.company_id.id,
                        'note': line.name,
                        'property_ids': [(6, 0, [x.id for x in line.property_ids])],})
        return result
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_order, context),
            'type': 'out',
            'state': 'draft',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
            'auto_picking': True,
        }
    
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')

        for line in order_lines:
            if line.state == 'done':
                continue

            date_planned = self._get_date_planned(cr, uid, order, line, order.date_order, context=context)

            if line.product_id:
                if line.product_id.type in ('product', 'consu'):
                    if not picking_id:
                        
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    for x in self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context):
                        move_id = move_obj.create(cr, uid, x)
                else:
                    # a service has no stock move
                    move_id = False

#                 proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context))
#                 proc_ids.append(proc_id)
#                 line.write({'procurement_id': proc_id})
#                 self.ship_recreate(cr, uid, order, line, move_id, proc_id)
        print picking_id
        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
            picking_obj.force_assign(cr, uid, [picking_id])
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_done', cr)
#         for proc_id in proc_ids:
#             wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        val = {}
        if order.state == 'shipping_except':
            val['state'] = 'progress'
            val['shipped'] = False

            if (order.order_policy == 'manual'):
                for line in order.order_line:
                    if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                        val['state'] = 'manual'
                        break
        order.write(val)
        return True
    
    _columns = {
        'compaign': fields.text('Compaign'),
        }

sale_order()

