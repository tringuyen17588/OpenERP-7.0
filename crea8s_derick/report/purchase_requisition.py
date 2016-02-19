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
from openerp.report import report_sxw

report_type = []

class crea8s_requisition(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_requisition, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total': self.get_total,
            'get_qty': self.get_qty,
        })
        
    def get_qty(self, line):
        result = 0
        for l in line:
            result += l.box_qty
        return result
    
    def get_total(self, line):
        result = 0
        for l in line:
            result += l.amount
        return result
   
report_sxw.report_sxw('report.purchase_requisition','purchase.requisition','addons/crea8s_derick/report/purchase_requisition.rml',parser=crea8s_requisition, header=False)

class crea8s_requisition_a5(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_requisition_a5, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total': self.get_total,
            'get_qty': self.get_qty,
        })
        
    def get_qty(self, line):
        result = 0
        for l in line:
            result += l.box_qty
        return result
    
    def get_total(self, line):
        result = 0
        for l in line:
            result += l.amount
        return result
   
report_sxw.report_sxw('report.purchase_requisition_a5','purchase.requisition','addons/crea8s_derick/report/purchase_requisition_a5.rml',parser=crea8s_requisition_a5, header=False)
