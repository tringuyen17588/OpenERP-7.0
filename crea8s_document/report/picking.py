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
from openerp.report import report_sxw

class picking_inship_company(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_inship_company, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc1': self.get_product_desc1,
            'get_product_desc2': self.get_product_desc2,
            'get_qty_onhand': self.get_qty_onhand,
            'get_others_qty': self.get_others_qty,
        })
    def get_product_desc1(self, move_line):
        desc = ''
        if move_line.product_id.default_code:
            desc = move_line.product_id.default_code
        return desc
    
    def get_product_desc2(self, move_line):
        desc = move_line.product_id.name
        return desc
    
    def get_qty_onhand(self, product_id, location_id):
        product_obj = self.pool.get('product.product')
        if product_id and location_id:
            qty = product_obj.get_product_available(self.cr, self.uid, [product_id], {'location':[location_id],
                                                                                      'compute_child': True,
                                                                                      'states': ('done',), 
                                                                                      'what': ('in', 'out')})
        return qty[product_id]

    def get_others_qty(self, product_id, qty):
        result = []
        product_obj = self.pool.get('product.product')
        if product_id and qty:
            for line_info in product_obj.browse(self.cr, self.uid, product_id).box_items:
                result.append({'name': line_info.name,
                               'qty_box': divmod(qty,line_info.quatity)[0],})
        return result

report_sxw.report_sxw('report.picking_inship_company',
                          'stock.picking.in',
                          'addons/crea8s_derick/report/picking.rml',
                          parser=picking_inship_company, header=False)
