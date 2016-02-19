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
from openerp.osv import fields, osv
from openerp.report import report_sxw
from openerp.tools.translate import _
import csv

class account_invoice_ms_media(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_ms_media, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line': self.get_line,
            'get_description': self.get_description,
            'get_more_line': self.get_more_line,
        })
    def get_more_line(self, character_keying):
        arr = character_keying.split('\n') 
        return arr
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
        return len(result)

    def get_line(self,line):
        result = []
        result1 = []
        result2 = []
        result3 = []
        result4 = []
        temp = 0
        for x in line:
            temp += self.process_line_wrap(x.name, 20)            
            if temp < 20:
                result1.append(x)
            elif temp >= 20 and temp < 34:
                result2.append(x)
            elif temp >= 34 and temp < 48:
                result3.append(x)
            else:
                result4.append(x)
        result.append(result1)
        result.append(result2)
        result.append(result3)
        result.append(result4)
        return result
    
    def get_description(self, line):
        result = ''
        product_name    = line.product_id and line.product_id.name or ''
        product_barcode = line.product_id and (line.product_id.ean13 and line.product_id.ean13 or '') or '' 
        description = line.name
        if product_barcode:
            if product_name in description:
                kq = description.split(product_name)
                kq = kq[len(kq) - 1]
                if '-' in kq:
                    kq = kq.split('-')
                    kq = kq[len(kq) - 1]
                else:
                    kq = ''
                result = '[%s] %s - %s'%(product_barcode, product_name, kq)
        else:
            result = description
        return result

report_sxw.report_sxw(
    'report.account.invoice.msmedia',
    'account.invoice',
    'addons/crea8s_msmedia_fix/account_print_invoice.rml',
    parser=account_invoice_ms_media, header=False)

class crea8s_order_msmedia(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_order_msmedia, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time, 
            'show_discount':self._show_discount,
            'get_more_line': self.get_more_line,
            'get_line': self.get_line,
        })

    def get_more_line(self, character_keying):
        arr = character_keying.split('\n') 
        return arr

    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]

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
        return len(result)

    def get_line(self,line):
        result = []
        result1 = []
        result2 = []
        result3 = []
        result4 = []
        temp = 0
        for x in line:
            temp += self.process_line_wrap(x.name, 20)            
            if temp < 20:
                result1.append(x)
            elif temp >= 20 and temp < 34:
                result2.append(x)
            elif temp >= 34 and temp < 48:
                result3.append(x)
            else:
                result4.append(x)
        result.append(result1)
        result.append(result2)
        result.append(result3)
        result.append(result4)
        return result
    
    def get_description(self, line):
        result = ''
        product_name    = line.product_id and line.product_id.name or ''
        product_barcode = line.product_id and (line.product_id.ean13 and line.product_id.ean13 or '') or '' 
        description = line.name
        if product_barcode:
            if product_name in description:
                kq = description.split(product_name)
                kq = kq[len(kq) - 1]
                if '-' in kq:
                    kq = kq.split('-')
                    kq = kq[len(kq) - 1]
                else:
                    kq = ''
                result = '[%s] %s - %s'%(product_barcode, product_name, kq)
        else:
            result = description
        return result

report_sxw.report_sxw('report.crea8s.sale.order.msmedia', 'sale.order', 'addons/crea8s_msmedia_fix/sale_order.rml', parser=crea8s_order_msmedia, header=False)

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
        'compaign': fields.text('Compaign'),
        }

sale_order()

