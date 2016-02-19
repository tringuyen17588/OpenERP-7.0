# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#     Copyright (C) 2013 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
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
from lxml import etree
from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_statement_from_invoice_lines(osv.osv_memory):
    _inherit = "account.statement.from.invoice.lines"
    
    def get_period(self, cr, uid, context={}):
        print 'Gia tri ddd ttt  ===   ', context 
        if context.get('period_id', False):
            return context['period_id']
        return 0
    
    _columns = {
        'period_id': fields.many2one('account.period', 'Period'),
    }
    
    _defaults = {
        'period_id': get_period,
    }

