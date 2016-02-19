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

class default_tax_so(osv.osv):
    _name = "default.tax.so"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _columns = {
        'name': fields.char('Name', size=256),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'tax_id': fields.many2many('account.tax', 'crea8s_sale_line_tax', 'df_id', 'tax_id', 'Tax'),
    }
    
default_tax_so()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    def create(self, cr, uid, vals, context={}):
        default_tax_obj = self.pool.get('default.tax.so')
        if not vals['tax_id'][0][2]:
            tax_df = default_tax_obj.search(cr, uid, [])
            tax_default = []
            for x in tax_df:                
                 tax_default = [xx.id for xx in default_tax_obj.browse(cr, uid, x).tax_id]
            vals['tax_id'][0][2] = tax_default
        print 'after  check  =  ', vals
        return super(sale_order_line, self).create(cr, uid, vals, context)
    
sale_order_line()