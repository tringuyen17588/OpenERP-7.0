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

report_type = []

class report_crea8s_pos(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_crea8s_pos, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_order': self.get_order,
        })
    def process_date_title(self, date_or):
        temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        temp += timedelta(hours=7)
        result = time.strftime('%a %b %d %Y %H:%M:%S',time.strptime(str(temp), '%Y-%m-%d %H:%M:%S'))
        return result
    
    def process_date_nomal(self, date_or):
        temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        temp += timedelta(hours=7)
        result = time.strftime('%d-%m-%Y %H:%M',time.strptime(str(temp), '%Y-%m-%d %H:%M:%S'))
        return result
    
    def group_product(self, lst_product):
        result = []
        lst_uniq = list(set(x.product_id.name for x in lst_product))
        for prod in lst_uniq:
            qty   = 0
            total = 0
            for prod_2 in lst_product:
                if prod == prod_2.product_id.name:
                      qty   += prod_2.qty
                      total += prod_2.price_subtotal
            result.append({'product': prod,
                           'total': total,
                           'qty': float(qty)})
        return result
    
    def get_order(self, session_id):
        result     = []
        
        pos_order_obj = self.pool.get('pos.order')
        order_ids = pos_order_obj.search(self.cr, self.uid, [('session_id', '=', session_id)], order='date_order', limit=10)
        num = 0
        for record in pos_order_obj.browse(self.cr, self.uid, order_ids):
            num += 1
            dct_result = {'number': str(num) + '.  ', 
                          'date_order': self.process_date_title(record.date_order),
                          'name': record.name and record.name or '',
                          'date_of': self.process_date_nomal(record.date_order)
                         }
            
            product = self.group_product(record.lines)
            total = sum([tt.price_subtotal for tt in record.lines])
            dct_result.update({'order_line': product,
                               'total': total})
            result.append(dct_result)
        return result
    
report_sxw.report_sxw('report.crea8s.pos.order', 'pos.session', 'addons/crea8s_pos_report/report/session_order_10.rml', parser=report_crea8s_pos, header=False)

class report_crea8s_pos_all(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_crea8s_pos_all, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_order': self.get_order,
            'get_total_all': self.get_total_all,
            'process_date_nomal': self.process_date_nomal,
        })
    def process_date_title(self, date_or):
        temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        temp += timedelta(hours=7)
        result = time.strftime('%a %b %d %Y %H:%M:%S',time.strptime(str(temp), '%Y-%m-%d %H:%M:%S'))
        return result
    
    def process_date_nomal(self, date_or):
        temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        temp += timedelta(hours=7)
        result = time.strftime('%d-%m-%Y %H:%M',time.strptime(str(temp), '%Y-%m-%d %H:%M:%S'))
        return result
    
    def group_product(self, lst_product):
        result = []
        lst_uniq = list(set(x.product_id.name for x in lst_product))
        for prod in lst_uniq:
            qty   = 0
            total = 0
            for prod_2 in lst_product:
                if prod == prod_2.product_id.name:
                      qty   += prod_2.qty
                      total += prod_2.price_subtotal
            result.append({'product': prod,
                           'total': total,
                           'qty': float(qty)})
        return result
    
    def get_total_all(self, session_id):
        pos_order_obj = self.pool.get('pos.order')
        pos_order_line_obj = self.pool.get('pos.order.line')
        order_ids = pos_order_obj.search(self.cr, self.uid, [('session_id', '=', session_id)])
        order_line_ids = pos_order_line_obj.search(self.cr, self.uid, [('order_id', 'in', order_ids)])
        total = sum([x.price_subtotal for x in pos_order_line_obj.browse(self.cr, self.uid, order_line_ids)])
        return total
    
    def get_order(self, session_id):
        result     = []
        pos_order_obj = self.pool.get('pos.order')
        pos_order_line_obj = self.pool.get('pos.order.line')
        pos_categ_obj = self.pool.get('pos.category')
        temp_id = []
        order_ids = pos_order_obj.search(self.cr, self.uid, [('session_id', '=', session_id)])
        order_line_ids = pos_order_line_obj.search(self.cr, self.uid, [('order_id', 'in', order_ids),
                                                                       ('product_id.ean13', '!=', False)])
        pos_categ_ids = pos_categ_obj.search(self.cr, self.uid, [])
        num = 0
        for x in pos_categ_ids:
            num += 1
            order_line_categ = pos_order_line_obj.search(self.cr, self.uid, [('order_id', 'in', order_ids),
                                                                             ('product_id.pos_categ_id', '=', x),
                                                                             ('product_id.ean13', '!=', False)])
            if order_line_categ == []:
                pass
            else:
                lines = pos_order_line_obj.browse(self.cr, self.uid, order_line_categ) 
                product = self.group_product(lines)
                total = sum([tt.price_subtotal for tt in lines])
                dct_result = {'name': pos_categ_obj.browse(self.cr, self.uid, x).name,
                              'order_line': product,
                              'total': total}
                result.append(dct_result)
                [order_line_ids.remove(y) for y in order_line_categ]
        if order_line_ids:
            rest_lines = pos_order_line_obj.browse(self.cr, self.uid, order_line_ids) 
            product = self.group_product(rest_lines)
            total = sum([tt.price_subtotal for tt in rest_lines])
            dct_result = {'name': 'unused',
                          'order_line': product,
                          'total': total}
            result.append(dct_result)
        return result
    
report_sxw.report_sxw('report.crea8s.pos.order.all', 'pos.session', 'addons/crea8s_pos_report/report/session_order_all.rml', parser=report_crea8s_pos_all, header=False)