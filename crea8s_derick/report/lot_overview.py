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
from openerp import pooler
import time
from openerp.report import report_sxw

class crea8s_lot_overview(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_lot_overview, self).__init__(cr, uid, name, context=context)
        self.price_total = 0.0
        self.grand_total = 0.0
        self.localcontext.update({
            'time': time,
            'process':self.process,
            'price_total': self._price_total,
            'grand_total_price':self._grand_total,
            'get_qty1': self.get_qty1,
            'get_qty2': self.get_qty2,
        })

    def get_qty1(self, product_br, prod_qty, uom_def):
        result = []
        if product_br.uom_ids:
            for x in product_br.uom_ids:
                result.append({'qty1': x.qty_ex,
                               'uom1': x.uom_id_ex and x.uom_id_ex.name or ' '})
        else:
            result.append({'qty1': '',
                           'uom1': ''})
        return result
    
    def get_qty2(self, product_br, prod_qty, uom_def):
        result = []
        if product_br.uom_ids:
            for x in product_br.uom_ids:
                result.append({'qty2': x.qty_def,
                               'uom2': x.uom_id_def and x.uom_id_def.name or ' ',})
        else:
            result.append({'qty2': prod_qty,
                           'uom2': uom_def})
        return result

    def process(self, location_id):
        location_obj = pooler.get_pool(self.cr.dbname).get('stock.location')
        data = location_obj._product_get_report(self.cr,self.uid, [location_id])
        if data.has_key('product'):
            for prod in data['product']:
                prod['product_br']
        data['location_name'] = location_obj.read(self.cr, self.uid, [location_id],['complete_name'])[0]['complete_name']
        self.price_total = 0.0
        self.price_total += data['total_price']
        self.grand_total += data['total_price']
        return [data]

    def _price_total(self):
        return self.price_total

    def _grand_total(self):
        return self.grand_total

report_sxw.report_sxw('report.crea8s.lot.stock.overview', 'stock.location', 'addons/crea8s_derick/report/lot_overview.rml', parser=crea8s_lot_overview,header='internal')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

