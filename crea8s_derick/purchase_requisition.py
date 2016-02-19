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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import math

def next_multiple(x, y):
    return math.ceil(x/y)*y

class uom_box(osv.osv):
    _name = "uom.box"

    _columns = {
        'name': fields.char('Name', size=128),
        'quatity': fields.float('Quantity'),
    }    
    
uom_box()

class product_product(osv.osv):
    _inherit = "product.product"

    def get_product_available(self, cr, uid, ids, context=None):
        """ Finds whether product is available or not in particular warehouse.
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        
        location_obj = self.pool.get('stock.location')
        warehouse_obj = self.pool.get('stock.warehouse')
        shop_obj = self.pool.get('sale.shop')
        
        states = context.get('states',[])
        what = context.get('what',())
        if not ids:
            ids = self.search(cr, uid, [])
        res = {}.fromkeys(ids, 0.0)
        if not ids:
            return res

        if context.get('shop', False):
            warehouse_id = shop_obj.read(cr, uid, int(context['shop']), ['warehouse_id'])['warehouse_id'][0]
            if warehouse_id:
                context['warehouse'] = warehouse_id

        if context.get('warehouse', False):
            lot_id = warehouse_obj.read(cr, uid, int(context['warehouse']), ['lot_stock_id'])['lot_stock_id'][0]
            if lot_id:
                context['location'] = lot_id

        if context.get('location', False):
            if type(context['location']) == type(1):
                location_ids = [context['location']]
            elif type(context['location']) in (type(''), type(u'')):
                location_ids = location_obj.search(cr, uid, [('name','ilike',context['location'])], context=context)
            else:
                location_ids = context['location']
        else:
            location_ids = []
            company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            wids = warehouse_obj.search(cr, uid, [('company_id', '=', company_id)], context=context)
            if not wids:
                return res
            for w in warehouse_obj.browse(cr, uid, wids, context=context):
                location_ids.append(w.lot_stock_id.id)

        # build the list of ids of children of the location given by id
        if context.get('compute_child',True):
            child_location_ids = location_obj.search(cr, uid, [('location_id', 'child_of', location_ids)])
            location_ids = child_location_ids or location_ids
        
        # this will be a dictionary of the product UoM by product id
        product2uom = {}
        uom_ids = []
        for product in self.read(cr, uid, ids, ['uom_id'], context=context):
            product2uom[product['id']] = product['uom_id'][0]
            uom_ids.append(product['uom_id'][0])
        # this will be a dictionary of the UoM resources we need for conversion purposes, by UoM id
        uoms_o = {}
        for uom in self.pool.get('product.uom').browse(cr, uid, uom_ids, context=context):
            uoms_o[uom.id] = uom

        results = []
        results2 = []

        from_date = context.get('from_date',False)
        to_date = context.get('to_date',False)
        date_str = False
        date_values = False
        where = [tuple(location_ids),tuple(location_ids),tuple(ids),tuple(states)]
        if from_date and to_date:
            date_str = "date>=%s and date<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))

        prodlot_id = context.get('prodlot_id', False)
        prodlot_clause = ''
        if prodlot_id:
            prodlot_clause = ' and prodlot_id = %s '
            where += [prodlot_id]

        # TODO: perhaps merge in one query.
        if 'in' in what:
            # all moves from a location out of the set to a location in the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id NOT IN %s '\
                'and location_dest_id IN %s '\
                'and product_id IN %s '\
                'and state IN %s ' + (date_str and 'and '+date_str+' ' or '') +' '\
                + prodlot_clause + 
                'group by product_id,product_uom',tuple(where))
            results = cr.fetchall()
        if 'out' in what:
            # all moves from a location in the set to a location out of the set
            cr.execute(
                'select sum(product_qty), product_id, product_uom '\
                'from stock_move '\
                'where location_id IN %s '\
                'and location_dest_id NOT IN %s '\
                'and product_id  IN %s '\
                'and state in %s ' + (date_str and 'and '+date_str+' ' or '') + ' '\
                + prodlot_clause + 
                'group by product_id,product_uom',tuple(where))
            results2 = cr.fetchall()
            
        # Get the missing UoM resources
        uom_obj = self.pool.get('product.uom')
        uoms = map(lambda x: x[2], results) + map(lambda x: x[2], results2)
        if context.get('uom', False):
            uoms += [context['uom']]
        uoms = filter(lambda x: x not in uoms_o.keys(), uoms)
        if uoms:
            uoms = uom_obj.browse(cr, uid, list(set(uoms)), context=context)
            for o in uoms:
                uoms_o[o.id] = o
                
        #TOCHECK: before change uom of product, stock move line are in old uom.
        context.update({'raise-exception': False})
        # Count the incoming quantities
        for amount, prod_id, prod_uom in results:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                     uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] += amount
        # Count the outgoing quantities
        for amount, prod_id, prod_uom in results2:
            amount = uom_obj._compute_qty_obj(cr, uid, uoms_o[prod_uom], amount,
                    uoms_o[context.get('uom', False) or product2uom[prod_id]], context=context)
            res[prod_id] -= amount
        return res

    _columns = {
        'box_items': fields.many2many('uom.box', 'product_box_rel', 'prod_id', 'box_id', 'Boxes'),
    }

product_product()

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"

    _columns = {
        'rate': fields.float('Rate'),
        'amount_fb': fields.float('F(B)'),
        'amount_fs': fields.float('F(S)'),
        'amount_ctn': fields.char('CTN', size=256),
    }

purchase_requisition()

class purchase_requisition_note(osv.osv):
    _name = "purchase.requisition.note"

    _columns = {
        'name': fields.char('Name'),
        'code': fields.char('Code'),        
    }

purchase_requisition_note()

#    New object in product to add more field to set product of measure with quantity
class product_uom_other(osv.osv):
    _name = "product.uom.other"
    
    def _product_available_ex(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids):
            if record.exchange and record.product_id:
                temp = divmod(product_obj.browse(cr, uid, record.product_id.id, context).qty_available, record.exchange)
                result[record.id] = temp[1] and temp[0] or temp[0] - 1
        return result
    
    def _product_available_def(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids):
            if record.exchange and record.product_id:
                temp = divmod(product_obj.browse(cr, uid, record.product_id.id, context).qty_available, record.exchange)[1]
                result[record.id] = temp and temp or record.exchange
        return result
    
    _columns = {
        'name': fields.char('Name', size=256),
        'u_price': fields.float('Price'),
        'product_id': fields.many2one('product.product', 'Product'),
        'uom_id_ex': fields.many2one('product.uom', 'Unit Of Measure'),
        'uom_id_def': fields.many2one('product.uom', 'Unit Of Measure'),
        'exchange': fields.float('Exchange', digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_ex': fields.function(_product_available_ex, type='float',  digits_compute=dp.get_precision('Product Unit of Measure'), string='Quantity'),
        'qty_def': fields.function(_product_available_def, type='float',digits_compute=dp.get_precision('Product Unit of Measure'), string='Quantity'),
    }
    
    def get_uom_default(self, cr, uid, context):
        result = 0
        if context.get('uom_def', False):
            result = context['uom_def']
        return result
        
    _defaults = {
        'uom_id_def': lambda self, cr, uid, c: self.get_uom_default(cr, uid, context=c),
    }

product_uom_other()

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    
    _columns = {
        'box_items': fields.many2one('uom.box', 'Type Of Box'),
        'uom_other': fields.many2one('product.uom.other', 'Type Of Box'),
        'box_qty': fields.float('Box Qty'),
        'cost': fields.float('Cost'),
        'up': fields.float('Unit Price'),
        'amount_dcur': fields.float('THB'),
        'amount': fields.float('Amount'),
        
        'note': fields.char('TPT/CC BOX'),
        'supp': fields.many2one('purchase.requisition.note', 'SUPP'),
        
    }
    
    def onchange_up(self, cr, uid, ids, up, qty_box):
        box_type = self.pool.get('uom.box')
        if up and qty_box:
            return {'value': {'amount': up * qty_box}}
        return {'value': {'amount': 0}}
    
    def onchange_qty_uom(self, cr, uid, ids, qty, cost):
        if not qty or not cost:
            return {'value': {'amount_dcur': 0}}
        else:
            return {'value': {'amount_dcur': qty * cost}}
        return {'value': {'amount_dcur': 0}}
    
    def get_number_char(self, cr, uid, temp):
        kq = ''
        for b in temp:
            if b.isdigit():
                kq += b
        kq = eval(kq)
        return kq
    
    def round_number(self, cr, uid, ids, number):
        return round(number,1)
    
    def onchange_box_type(self, cr, uid, ids, qty, type_box, cost, price_box, rate):
        uom_other = self.pool.get('product.uom.other') 
        value = {}
        warning = {}
        if not rate:
             warning = {'title':'Warning !','message':'Please input the Rate before choose Type of Box!'}
             return {'value': {'box_qty': 0}, 'warning': warning}
        if type_box:
            uot_qty = uom_other.browse(cr, uid, type_box).exchange
            if price_box and cost:
                price_box = self.get_number_char(cr, uid, price_box)
                price_box = self.round_number(cr, uid, ids, (uot_qty * cost + price_box) /  rate)
                value.update({'up': price_box})
            else:
                value.update({'up': 0})
            if qty:
                box_qtys = divmod(qty,  uot_qty)[0]
                value.update({'box_qty': box_qtys})
            return {'value': value}
        return {'value': {'box_qty': 0}}
    
purchase_requisition_line()
