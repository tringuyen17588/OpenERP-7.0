# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw

report_type = []

def _get_line_no_(obj, line):
    """
        Get line_no of current line in any objects.

        :author: phongnd
        :return: None
        """
    
    iNo = 0
    for item in obj.order_line:
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



class crea8s_vector_quotation_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_vector_quotation_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
        })
        
report_sxw.report_sxw('report.crea8s_vector_quo01', 'sale.order', 'addons/crea8s_vector/report_folder/quotation_report.rml-asdasdasd', \
                      parser=crea8s_vector_quotation_report, header=False)

class crea8s_vector_quotation_report02(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_vector_quotation_report02, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
        })

report_sxw.report_sxw('report.crea8s_vector_quo02', 'sale.order', 'addons/crea8s_vector/report_folder/crea8s_vector_quo02.rml-asdasdasd', \
                      parser=crea8s_vector_quotation_report02, header=False)

class crea8s_vector_quotation_report03(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(crea8s_vector_quotation_report03, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line_no': _get_line_no_,
            'get_toal_sp': _get_toal_sp_,
            'get_toal_cp': _get_toal_cp_,
            'get_supplier': _get_supplier_,
        })

report_sxw.report_sxw('report.crea8s_vector_quo03', 'sale.order', 'addons/crea8s_vector/report_folder/crea8s_vector_quo03.rml-asdasdasd', \
                      parser=crea8s_vector_quotation_report03, header=False)