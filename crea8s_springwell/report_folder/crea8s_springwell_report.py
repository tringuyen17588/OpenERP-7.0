# -*- coding: utf-8 -*-
##############################################################################
# 
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Crea8s (http://www.crea8s.com) All Rights Reserved.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>...
#
##############################################################################

import time
import openerp.addons.sale as sale
# import datetime
from openerp.report import report_sxw
# from itertools import count

report_type = []



def _get_line_no_(objLines, line):
    """
        Get line_no of current line in any Lines.

        :author: phongnd
        :return: None
        """
    
    iNo = 0
    for item in objLines: #obj.order_line:
        iNo += 1
        if (item.id == line.id):
            break
    
    return iNo

def _get_toal_sp_(obj):
    """
        Get total Sale Price.

        :author: phongnd
        :return: None
        """
    
    fTotalSP = 0.0
    for item in obj.order_line:
        fTotalSP += item.price_subtotal
    
    return fTotalSP

def _get_toal_cp_(obj):
    """
        Get total Cost Price.
        
        :author: phongnd
        :return: None
        """
    
    fTotal = 0.0
    for item in obj.order_line:
        fTotal += item.purchase_price * item.product_uom_qty
    
    return fTotal 


def _get_supplier_(obj, line):
    """
        Get a supplier of current line product.

        :author: phongnd
        :return: None
        """
    
    iNo = 0
    strRet = None
    for item in obj.order_line:
        iNo += 1
        if (item.id == line.id):
            if (len(item.product_id.seller_ids)>0):
                strRet = item.product_id.seller_ids[0] and item.product_id.seller_ids[0].name.name or None
            break
            
    
    return strRet


def _get_empty_lines(objLines, maxRowsForPageFirstNotTotal, maxRowsForPageSub, nuRequiredEmptyRows, maxRowForTotal):
    """
        _get_empty_lines between content & Signature section of SO, PO, DO, Invoice,...

        :author: phongnd
        :return: arrEmpty[]
        """
    arrEmpty = []
#     iCount = 0
    iTotalLines = len(objLines)     # objLines.count    #count(objLines)
    if iTotalLines <= int(maxRowsForPageFirstNotTotal):
        dStart = 0
        dStop = maxRowsForPageFirstNotTotal - iTotalLines - nuRequiredEmptyRows - maxRowForTotal + 2
        dStep = 1
        for i in xrange(dStart, dStop+1, dStep):
            arrEmpty.append(i) #{str(iCount): iCount }
    else:
#         for item in objLines:
#             arrEmpty.append('') #{str(iCount): iCount }
        dStart = 0
        nuMaxRows_LastPage = ((iTotalLines - maxRowsForPageFirstNotTotal) % maxRowsForPageSub)
        dStop = maxRowsForPageSub - nuMaxRows_LastPage - nuRequiredEmptyRows - maxRowForTotal
        dStep = 1
        for i in xrange(dStart, dStop+1, dStep):
            arrEmpty.append(i) #{str(iCount): iCount }
    
#     print(str(arrEmpty))
    return arrEmpty
        
        
    
def _get_text_to_array(strText):
    """
        _get_empty_lines between content & Signature section of SO, PO, DO, Invoice,...

        :author: phongnd
        :return: arrEmpty[]
        """
    
    temp = strText.split('\n')
#     print str(temp) 
    return temp


def _get_empty_lines_service_note(descServiceNote, maxRowsForPageFirstNotTotal, maxRowsForPageSub, nuRequiredEmptyRows, maxRowForTotal):
    """
        _get_empty_lines_service_note ,...

        :author: phongnd
        :return: None
        """
    objLines = _get_text_to_array(descServiceNote)
    print str(objLines)
    return _get_empty_lines(objLines, maxRowsForPageFirstNotTotal, maxRowsForPageSub, nuRequiredEmptyRows, maxRowForTotal)

def _get_empty_lines_with_note(objLines, maxRowsForPageFirstNotTotal, maxRowsForPageSub, nuRequiredEmptyRows, maxRowForTotal, strNote, nuLineNotesPerROW):
    """
        _get_empty_lines_with_note ,...

        :author: phongnd
        :return: None
        """
    objLines02 = _get_text_to_array(strNote)
    dStop = len(objLines02) / nuLineNotesPerROW
#     dStop = len(objLines02) / 2
    
#     dStart = 0
#     dStep = 1
#     objLines02_reduce = []
#     for i in xrange(dStart, dStop+1, dStep):
#         objLines02_reduce.append(i)
#     objLines +=  objLines02_reduce
    # increase Total lines
    maxRowForTotal += dStop
#     print str(objLines)
    return _get_empty_lines(objLines, maxRowsForPageFirstNotTotal, maxRowsForPageSub, nuRequiredEmptyRows, maxRowForTotal)
#     arrEmpty =  [1,2,3,4] # [] #
#     arrEmpty.append(1)
#     arrEmpty.append(2)
#     return arrEmpty

# Sale Order
class crea8s_springwell_so_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_springwell_so_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
            'show_discount': self._show_discount,
            'get_empty_lines': self.get_empty_line,
            'get_empty_line12': self.get_empty_line12,
        })
        
        
    def process_line_wrap1(self, character, char_com):
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
    
    def process_line_wrap(self, character, char_com):
        result = []
        arr = character.split('\n')
        if len(arr) > 1:
            for x in arr:
                for xx in self.process_line_wrap1(x, char_com):
                    result.append(xx)
        else:
            result = self.process_line_wrap1(character, char_com)
        return result

    def get_empty_line12(self, lines):
        result = []
        count_line = 0
        for a in lines:
            arr = self.process_line_wrap(a.name, 40)
            count_line += len(arr)
        count_line = divmod(count_line,24)
        if count_line[0]:
            for a in range(12):
                result.append(1) 
        return result
        
    def get_empty_line(self, lines):
        result = []
        count_line = 0
        for a in lines:
            arr = self.process_line_wrap(a.name, 40)
            count_line += len(arr)
        count_line = divmod(count_line,24)
        print 'count_line == ', count_line
        if count_line[1]:
            for a in range(24 - count_line[1]):
                result.append(1) 
        return result
    
    def _show_discount(self, uid, context=None):
        cr = self.cr
        try: 
            group_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'group_discount_per_so_line')[1]
        except:
            return False
        return group_id in [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context=context).groups_id]
        
report_sxw.report_sxw('report.crea8s_springwell_quo01', 'sale.order', 'addons/crea8s_springwell/report_folder/quotation_report.rml-asdasdasd', parser=crea8s_springwell_so_report, header=False)


# Purchase Order 
class crea8s_springwell_po_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_springwell_po_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
            'get_empty_lines': _get_empty_lines,
            'get_empty_lines_with_note': _get_empty_lines_with_note,
        })

report_sxw.report_sxw('report.crea8s_springwell_po01', 'purchase.order', 'addons/crea8s_springwell/report_folder/purchase_order.rml-asdasdasd', parser=crea8s_springwell_po_report, header=False)


# Purchase Order 02 - Request Order
class crea8s_springwell_po_report02(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_springwell_po_report02, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
            'get_empty_lines': _get_empty_lines,
        })

report_sxw.report_sxw('report.crea8s_springwell_po02', 'purchase.order', 'addons/crea8s_springwell/report_folder/purchase_order.rml-asdasdasd', parser=crea8s_springwell_po_report02, header=False)


# stock picking 
class crea8s_springwell_stock_picking_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_springwell_stock_picking_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc,
            'get_empty_lines': _get_empty_lines,
        })
    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc
    
report_sxw.report_sxw('report.crea8s_springwell_stock_picking_out', 'stock.picking.out', 'addons/crea8s_springwell/report_folder/stock_picking.rml-asdasdasd', parser=crea8s_springwell_stock_picking_report, header=False)


# SO->tab: Service Note
class crea8s_springwell_servive_note_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_springwell_servive_note_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
            'get_empty_lines': _get_empty_lines,
            'get_text_to_array': _get_text_to_array,
            'get_empty_lines_service_note': _get_empty_lines_service_note,
            'make_wrap': self.make_wrap,
        })
    def make_wrap(self, str_digit):
        temp1 = 0
        result = []
        for a in str_digit.split('\n'):
            temp1 += 1
            if len(a) >= 120:
                k = divmod(len(a), 120)
                temp1 += k[0]
                if k[1] > 0:
                    temp1 += 1
        if temp1 < 27:
            for x in range(27 - temp1):
                result.append(' ')
        return result
                
        
report_sxw.report_sxw('report.crea8s_springwell_servive_note_report_name', 'crea8s.sw.service.note', 'addons/crea8s_springwell/report_folder/service_note.rml-asdasdasd', parser=crea8s_springwell_servive_note_report, header=False)

# SO Invoice
# phongnd 20150108 - inherit openerp.addons.sale.report.sale_order.order
class crea8s_springwell_invoice_report(sale.report.sale_order.order): #report_sxw.rml_parse
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_springwell_invoice_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
            'get_empty_lines': _get_empty_lines,
            'get_empty_lines_with_note': _get_empty_lines_with_note,
        
        })
report_sxw.report_sxw('report.crea8s_springwell_invoice_report_name', 'account.invoice', 'addons/crea8s_springwell/report_folder/invoice.rml-asdasdasd', parser=crea8s_springwell_invoice_report, header=False)








