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

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'remark': fields.text('Remark'),
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
        'remark': fields.text('Remark'),
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
    
stock_picking_out()

# class crea8s_vector_picking_note(report_sxw.rml_parse):
#     def __init__(self, cr, uid, name, context):
#         super(crea8s_vector_picking_note, self).__init__(cr, uid, name, context=context)
#         self.localcontext.update({
#             'time': time,
# 
#         })
#     def get_product_desc(self, move_line):
#         desc = move_line.product_id.name
#         if move_line.product_id.default_code:
#             desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
#         return desc
# 
# for suffix in ['', '.in', '.out']:
#     report_sxw.report_sxw('report.crea8s.vector.stock.picking.list' + suffix,
#                           'stock.picking' + suffix,
#                           'addons/crea8s_address_delivery/picking.rml',
#                           parser=crea8s_vector_picking_note, header=False)
   