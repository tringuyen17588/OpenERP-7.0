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
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import netsvc
import pytz
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
        'do_control':fields.selection([('manu','Manual'),
									   ('before', 'Before make payment'),
									   ('after', 'After make payment')],'DO Control'),
        'lot_id': fields.many2one('stock.location', 'Warehouse'),
        'do_id': fields.many2one('stock.picking', 'Picking'),
    }
    
    def date_to_datetime(self, cr, uid, userdate, context=None):
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATE_FORMAT)
        if context and context.get('tz'):
            tz_name = context['tz']
        else:
            tz_name = self.pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['tz'])['tz']
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date + relativedelta(hours=12.0)
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    
    def _get_date_planned(self, cr, uid, order, start_date, context=None):
        start_date = self.date_to_datetime(cr, uid, start_date, context)
        date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(days=0.0)
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return date_planned
    
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        location_id = order.lot_id.id
        lot_obj = self.pool.get('stock.location')
        output_id = lot_obj.search(cr, uid, [('usage', '=', 'customer')])
        output_id = output_id and output_id[0] or 0
        return {
            'name': line.name,
            'picking_id': move_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.qty_others or line.quantity,
            'product_uom': line.uos_id.id,
            'product_uos_qty': line.qty_others or line.quantity,
            'qty_others': line.qty_others or line.quantity,
            'uom_others': line.uom_others and line.uom_others.id or line.uos_id.id,
            'product_uos': line.uos_id.id,
            'partner_id':  order.partner_id.id, #line.partner_shipping_id and line.partner_shipping_id.id or,
            'location_id': location_id,
            'location_dest_id': output_id,
            'tracking_id': False,
            'state': 'draft',
            'company_id': order.company_id.id,
            'price_unit': line.price_unit or 0.0}
    
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        
        location_id = order.lot_id.id
        lot_obj = self.pool.get('stock.location')
        output_id = lot_obj.search(cr, uid, [('usage', '=', 'customer')])
        output_id = output_id and output_id[0] or 0
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.qty_others or line.quantity,
            'product_uom': line.uos_id.id,
            'product_uos_qty': line.qty_others or line.quantity,
            'qty_others': line.qty_others or line.quantity,
            'uom_others': line.uom_others and line.uom_others.id or line.uos_id.id,
            'product_uos': line.uos_id.id,
            'partner_id':  order.partner_id.id, #line.partner_shipping_id and line.partner_shipping_id.id or,
            'location_id': location_id,
            'location_dest_id': output_id,
            'tracking_id': False,
            'state': 'draft',
            'company_id': order.company_id.id,
            'price_unit': line.price_unit or 0.0
        }
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': self.date_to_datetime(cr, uid, order.date_invoice, context),
            'type': 'out',
            'state': 'auto',
            'move_type': 'direct',
            'partner_id': order.partner_id.id,
            'invoice_state': 'none',
            'company_id': order.company_id.id,
        }
    
    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        proc_ids = []
        for line in order_lines:
            date_planned = self._get_date_planned(cr, uid, order, order.date_invoice, context=context)

            if line.product_id:
                if line.product_id.type in ('product', 'consu'):
                    if not picking_id:
                        picking_id = picking_obj.create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
                    move_id = move_obj.create(cr, uid, self._prepare_order_line_move(cr, uid, order, line, picking_id, date_planned, context=context))
                else:
                    move_id = False
                print self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context)
                proc_id = procurement_obj.create(cr, uid, self._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context))
                proc_ids.append(proc_id)
                line.write({'procurement_id': proc_id})
        wf_service = netsvc.LocalService("workflow")
        if picking_id:
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
#         for proc_id in proc_ids:
#             wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

        return picking_id
    
    def map_picking(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            if record.do_control == 'before':
                temp = self._create_pickings_and_procurements(cr, uid, record, record.invoice_line)
                self.write(cr, uid, ids, {'do_id': temp})
        return 1
    
    def map_picking_paid(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            if record.do_control == 'after':
                temp = self._create_pickings_and_procurements(cr, uid, record, record.invoice_line)
                self.write(cr, uid, ids, {'do_id': temp})
        return 1
    
    def action_view_delivery(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of delivery orders to display
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            so.do_id and pick_ids.append(so.do_id.id)
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',["+','.join(map(str, pick_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_out_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result
    
account_invoice()