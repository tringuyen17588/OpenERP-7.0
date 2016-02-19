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
import datetime
from datetime import timedelta
from openerp.report import report_sxw

#    For customer report
class report_customer(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_customer, self).__init__(cr, uid, name, context=context)
        self.number = 0
        self.localcontext.update({
            'time': time,
            'get_number': self.get_number,
            'get_date': self.get_date,
        })
    
    def get_number(self):
        self.number += 1
        return self.number

    def get_date(self, date_or):
        temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        temp += timedelta(hours=8)
        result = time.strftime('%d-%m-%Y %H:%M',time.strptime(str(temp), '%Y-%m-%d %H:%M:%S'))
        return result
report_sxw.report_sxw('report.customer_report', 'res.partner', 'addons/crea8s_glassfix/report/customer_report.rml', parser=report_customer, header=False)
#    For sale order
class crea8s_sale_order_fix(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_sale_order_fix, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'show_discount':self._show_discount,
        })

    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]

report_sxw.report_sxw('report.crea8s.sale.order.fix', 'sale.order', 'addons/crea8s_glassfix/report/sale_order.rml', parser=crea8s_sale_order_fix, header=False)
