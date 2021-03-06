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
import openerp.addons.decimal_precision as dp
from openerp.report import report_sxw


class crea8s_sale_agreement_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_sale_agreement_report, self).__init__(cr, uid, name, context=context)
        self.flag = 0
        self.localcontext.update({
            'time': time,
            'get_line': self.get_line,
        })
        
    def get_line(self, line):
        result = []
        for x in line:
            result.append({'item': x.name and x.name or ' ',
                           'product': x.product_id and  x.product_id.name or ' ',
                           'total': x.total and x.total or 0})
        if len(result)<10:
            for a in range(10-len(result)):
                result.append({'item': ' ',
                               'product': ' ',
                               'total': 0})
        return result
            
report_sxw.report_sxw('report.crea8s_report_sale_agreement',
                          'crea8s.sale.agreement',
                          'addons/crea8s_crm/report/sale_agreement.rml',
                          parser=crea8s_sale_agreement_report, header=False)

class crea8s_sale_agreement_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_sale_agreement_order_report, self).__init__(cr, uid, name, context=context)
        self.flag = 0
        self.localcontext.update({
            'time': time,
            'get_line': self.get_line,
            'get_all': self.get_all,
        })
        
    def get_all(self, obj):
        if not obj:
            raise osv.except_osv('Error !', 'Please create Sale Agreement before print it !')
        return obj
    
    def get_line(self, line):
        result = []
        for x in line:
            result.append({'item': x.name and x.name or ' ',
                           'product': x.product_id and  x.product_id.name or ' ',
                           'total': x.total and x.total or 0})
        if len(result)<10:
            for a in range(10-len(result)):
                result.append({'item': ' ',
                               'product': ' ',
                               'total': 0})
        return result
            
report_sxw.report_sxw('report.crea8s_report_sale_agreement_order',
                          'sale.order',
                          'addons/crea8s_crm/report/sale_agreement_order.rml',
                          parser=crea8s_sale_agreement_order_report, header=False)
