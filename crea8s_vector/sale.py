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

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    _columns = {
        'is_title': fields.boolean('Is title'),
    }
    _defaults = {
        'is_title': False,
    }
    def onchange_title(self, cr, uid, ids, title):
        
        return {'value': {'product_id': 0,
                          'product_uom_qty': 0,
                          'price_unit': 0}}
    
account_invoice_line()
class sale_order(osv.osv):
    _inherit = 'sale.order'
    def write(self, cr, uid, ids, vals, context={}):
        try:
            return super(sale_order, self).write(cr, uid, ids, vals, context=context)
        except Exception as e:
            if 'Access Denied by record rules for operation: write' in str(e):
                pass
            else:
                raise osv.except_osv('WARNING!', str(e)) 

sale_order()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
        'is_dhl': fields.boolean('Is DHL'),
        'dhl_id': fields.many2one('account.invoice', 'DHL Invoice'),
        'inv_ids': fields.many2many('account.invoice', 'dhl_invoice_rel', 'dhl_id', 'inv_id', 'Delivered For Invoices'),
#        'inv_ids': fields.one2many('account.invoice', 'dhl_id', 'Delivered For Invoices'),
    }
    _defaults = {
        'is_dhl': False,
    }
    
    def write(self, cr, uid, ids, vals, context={}):
        for rc in self.browse(cr, uid, ids):
            inv_ids = rc.inv_ids and [x.id for x in rc.inv_ids] or []
        result = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        for record in self.browse(cr, uid, ids):
#            inv_ids = self.search(cr, uid, [('dhl_id', '=', ids[0])])            
            if record.is_dhl and vals.get('inv_ids', False):
                temp = vals.get('inv_ids')[0][2]
                for idd in inv_ids:
                    if idd not in temp:#    Delete invoice
                         sql_d = ''' Update account_invoice set dhl_id = null where id = %s'''%idd
                         print sql_d
                         cr.execute(sql_d)
                if len(temp)>0:
                    temp = tuple(temp + [-1])
                    sql_u = ''' Update account_invoice set dhl_id = %s where id in %s'''%(record.id, temp)
                    cr.execute(sql_u)                    
        return result
        
account_invoice()
