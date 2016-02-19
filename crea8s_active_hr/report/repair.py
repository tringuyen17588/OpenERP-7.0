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

class report_repair(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_repair, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_number': self.get_number,
            'get_nature_fault': self.get_nature_fault,
        })
    
    def process_line_wrap(self, character, char_com):
        result = []
        num_char = 0
        line = ''
        arr1 = []
        arr = character.split('\n')
        for tep1 in arr:
            for tep in tep1.split(' '):
                arr1.append(tep)
        for temp in arr1:
            num_char += len(temp)
            if num_char <= char_com:
                line += ' ' + temp
            else:
                result.append(line)
                num_char = len(temp)
                line  = temp
        result.append(line)
        return result
    
    def get_nature_fault(self, cment):
        result = []
        if not cment:
            return result
        arr = cment.split('\n')
        for tep1 in arr:
            result += self.process_line_wrap(tep1, 75)
        
        if len(result) < 8:
            return result
        else:
            result = result[:8]
        return result 
    
    def get_number(self, obj):
        result =[]
        temp = 0
        temp_line = 0
        for line in obj.repair_line:
            temp += 1
            num_line = self.process_line_wrap(line.name, 40)
            if len(num_line) > 1:
                temp_line += len(num_line)
                temp_line -= 1
                line_in = 0
#                for kql in num_line:
#                    if temp_line < 15:
#                        if not line_in:
#                            print kql
#                            result.append({'number': temp,
#                                           'name': kql and kql or '',
#                                           'qty': line.qty and line.qty or '',
#                                           'unit_price': line.unit_price and line.unit_price or '',
#                                           'amount': line.amount and line.amount or '',})
#                            line_in += 1
#                        else:
#                            
#                            result.append({'number': '-',
#                                           'name': kql and kql or '',
#                                           'qty':  0,
#                                           'unit_price': 0,
#                                           'amount': 0,})
            else:
                temp_line += 1
            if temp_line <= 15:
                result.append({'number': temp,
                               'name': line.name and line.name or '',
                               'qty': line.qty and line.qty or '',
                               'unit_price': line.unit_price and line.unit_price or '',
                               'amount': line.amount and line.amount or '',})
        if 15-temp_line > 0:
            for x in range(15-temp_line):
                result.append({'number': '',
                               'name': '',
                               'qty': '',
                               'unit_price': '',
                               'amount': '',})
            
        return result
        
report_sxw.report_sxw('report.report.repair.cr8s', 'crea8s.repair', 'addons/crea8s_repair/report/repair.rml', parser=report_repair, header=False)