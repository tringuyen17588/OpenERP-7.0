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
from openerp.osv import fields, osv 
from datetime import timedelta
from openerp.report import report_sxw

class crea8s_report_post_sale(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_report_post_sale, self).__init__(cr, uid, name, context=context)
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

report_sxw.report_sxw('report.crea8s_report_post_sale', 'crea8s.post.sale.system', 
                      'addons/crea8s_crm/report/post_sale_system_report.rml', 
                      parser=crea8s_report_post_sale, header=False)

class crea8s_report_post_sale_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_report_post_sale_order, self).__init__(cr, uid, name, context=context)
        self.number = 0
        self.localcontext.update({
            'time': time,
            'get_number': self.get_number,
            'get_date': self.get_date,
            'get_all': self.get_all,
        })
        
    def get_all(self, obj):
        if not obj:
            raise osv.except_osv('Error !', 'Please create Post Sale System Report before print it !')
        return obj
    
    def get_number(self):
        self.number += 1
        return self.number
    
    def get_date(self, date_or):
        temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        temp += timedelta(hours=8)
        result = time.strftime('%d-%m-%Y %H:%M',time.strptime(str(temp), '%Y-%m-%d %H:%M:%S'))
        return result

report_sxw.report_sxw('report.crea8s_report_post_sale_order', 'sale.order', 
                      'addons/crea8s_crm/report/post_sale_system_report_order.rml', 
                      parser=crea8s_report_post_sale_order, header=False)
