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

class crea8s_stock_inventory_move(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_stock_inventory_move, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
             'time': time,
             'qty_total':self._qty_total,
             'get_qty_line1': self.get_qty_line1,
             'get_qty_line2': self.get_qty_line2,
        })

    def get_qty_line1(self, product_id, qty):
        result = []
        prod_obj = self.pool.get('product.product')
        prod_br = prod_obj.browse(self.cr, self.uid, product_id) 
        if prod_br.uom_ids:
            temp = prod_br.uom_ids[0]
            result.append('%.2f %s'%(divmod(qty, temp.qty_ex and round(temp.qty_ex,2) or 0)[0], temp.uom_id_ex and temp.uom_id_ex.name or ' '))
            result.append('%.2f %s'%(divmod(qty, temp.qty_ex and round(temp.qty_ex,2) or 0)[1], temp.uom_id_def and temp.uom_id_def.name or ' '))
        else:
            result.append(' ')
            result.append('%.2f %s'%(qty,prod_br.uom_id and prod_br.uom_id.name or ' '))
        return result
    
    def get_qty_line2(self, product_id, qty):
        result = ''
        prod_obj = self.pool.get('product.product')
        prod_br = prod_obj.browse(self.cr, self.uid, product_id) 
        if prod_br.uom_ids:
            if len(prod_br.uom_ids)>1:
                temp = prod_br.uom_ids[1]
                result = '%.2f %s %.2f %s'%(temp.qty_ex and qty * round(temp.qty_ex,2) or 0,
                                           temp.uom_id_ex and temp.uom_id_ex.name or ' ', 
                                           temp.qty_def and qty * round(temp.qty_def,2) or 0,
                                           temp.uom_id_def and temp.uom_id_def.name or ' ',)
        return result
    
    def _qty_total(self, objects):
        total = 0.0
        uom = objects[0].product_uom.name
        for obj in objects:
            total += obj.product_qty
        return {'quantity':total,'uom':uom}

report_sxw.report_sxw(
    'report.crea8s.stock.inventory.move',
    'stock.inventory',
    'addons/crea8s_derick/report/stock_inventory_move.rml',
    parser=crea8s_stock_inventory_move,
    header='internal'
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
