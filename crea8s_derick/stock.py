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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP

#######################################
#   Fix quantity in wizard picking
#######################################
#    Fix about can not add quantity into wizard receive incoming shipment
class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    
    def _partial_move_for(self, cr, uid, move):
        result = super(stock_partial_picking, self)._partial_move_for(cr, uid, move)
        if result.has_key('quantity'):
            result['quantity'] = move.product_qty if move.state == 'assigned' or move.picking_id.type == 'in' else 0
        return result
stock_partial_picking()
#######################################
#   Fix quantity in stock picking
#######################################
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    _columns = {
        'requisition_id': fields.many2one('purchase.requisition', 'Purchase Requisition'),
    }
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        result = super(stock_picking, self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context)
        result.update({'uom_others': move_line.uom_others and move_line.uom_others.id or 0,
                       'qty_others': move_line.qty_others and move_line.qty_others or 0,})
        return result
        
stock_picking()

class stock_inventory(osv.osv):
    _inherit = "stock.inventory"
    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        if context is None:
            context = {}
        # to perform the correct inventory corrections we need analyze stock location by
        # location, never recursively, so we use a special context
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in inv.inventory_line_id:
                pid = line.product_id.id
                product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
                change = line.product_qty - amount
                lot_id = line.prod_lot_id.id
                if change:
                    location_id = line.product_id.property_stock_inventory.id
                    value = {
                        'name': _('INV:') + (line.inventory_id.name or ''),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'uom_others': line.uom_other.id,
                        'qty_others': line.qty_other,
                        'prodlot_id': lot_id,
                        'date': inv.date,
                    }

                    if change > 0:
                        value.update( {
                            'product_qty': change,
                            'location_id': location_id,
                            'location_dest_id': line.location_id.id,
                        })
                    else:
                        value.update( {
                            'product_qty': -change,
                            'location_id': line.location_id.id,
                            'location_dest_id': location_id,
                        })
                    move_ids.append(self._inventory_line_hook(cr, uid, line, value))
            self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
            self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)
        return True
stock_inventory()
#######################################
#   Fix quantity in stock move
#######################################
class stock_move(osv.osv):
    _inherit = "stock.move"

    _columns = {
        'requisition_line_id': fields.many2one('purchase.requisition.line', 'Purchase Requisition Line'),
#        Add more field to manage other UOM
        'uom_others': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'qty_others': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
    }
    
    def onchange_quantity_other(self, cr, uid, ids, product_id, product_qty,
                          product_uom):
        product_obj = self.pool.get('product.product')
        uom_other = self.pool.get('product.uom.other')
        lst_measure = []
        def_measure = 0
        result = {}
        if product_id:
            product_br = product_obj.browse(cr, uid, product_id)
            def_measure = product_br.uom_id.id
            lst_measure = [(x.uom_id_ex and x.uom_id_ex.id or -1) for x in product_br.uom_ids ] 
            if product_uom:
                if product_uom not in lst_measure + [def_measure]: 
                    result.update({'warning': {'title': 'Warning !', 
                    'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                    result.update({'value':{'uom_others'  : 0}})
                    return result
                else:
                    if def_measure != product_uom:
                        if product_uom :
                            uom_other_id = uom_other.search(cr, uid, [('product_id', '=', product_id),
                                                                      ('uom_id_ex', '=', product_uom)])
                            uom_other_id = uom_other_id and uom_other_id[0] or 0
                            result = {'value':{'product_qty'  : float(uom_other.browse(cr, uid, uom_other_id).exchange) * product_qty}}
                            return result
                    else:
                        if product_uom :
                            result = {'value':{'product_qty'  : product_qty}}
        return result
    
    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):
        product_obj = self.pool.get('product.product')
        result = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, partner_id)
        if result.get('value', False) and prod_id:
            product_br = product_obj.browse(cr, uid, prod_id)
            result['value'].update({'uom_others': product_br.uom_id and product_br.uom_id.id or 0})
        return result        
            
stock_move()
#######################################
#   Fix inventory in stock
#######################################
class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"
    
    def _product_available_1(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids):
            if record.uom_ids:
                temp = record.uom_ids[0]
                result[record.id] = '%.2f %s and %.2f %s'%(temp.qty_ex and round(temp.qty_ex,2) or 0, 
                                                     temp.uom_id_ex and temp.uom_id_ex.name or ' ', 
                                                     temp.qty_def and temp.qty_def or 0,
                                                     temp.uom_id_def and temp.uom_id_def.name or ' ',)
            else:
                result[record.id] = '%.2f %s'%(record.qty_available, record.uom_id and record.uom_id.name or ' ')
        return result
    
    def _product_available_2(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids):
            if record.uom_ids and len(record.uom_ids)>1:
                temp = record.uom_ids[1]
                result[record.id] = '%.2f %s and %.2f %s'%(temp.qty_ex and round(temp.qty_ex,2) or 0, 
                                                     temp.uom_id_ex and temp.uom_id_ex.name or ' ', 
                                                     temp.qty_def and temp.qty_def or 0,
                                                     temp.uom_id_def and temp.uom_id_def.name or ' ',)
            else:
                result[record.id] = ' '
        return result
    
    def onchange_qty_other(self, cr, uid, ids, product_id, qty_other, qty_def, uom_other, uom_def):
        result = {}
        qty_final = 0
        product_obj = self.pool.get('product.product')
        ouom_obj = self.pool.get('product.uom.other')
        if product_id:
            print product_id, qty_other, qty_def, uom_other, uom_def
            product_br = product_obj.browse(cr, uid, product_id)
            lst_uom = [(x.uom_id_ex and x.uom_id_ex.id or -1) for x in product_br.uom_ids]
            exchange = 1
            if qty_other and uom_other:
                if uom_other not in lst_uom:
                    result.update({'warning': {'title': 'Warning !', 'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                ouom_id = ouom_obj.search(cr, uid, [('product_id', '=', product_id),
                                                    ('uom_id_ex', '=', uom_other)])
                ouom_id = ouom_id and ouom_id[0] or 0
                if ouom_id:
                    exchange = ouom_obj.browse(cr, uid, ouom_id).exchange
                qty_final += exchange *  qty_other
            if qty_def and uom_def:
                default_uom = product_br.uom_id and product_br.uom_id.id or 0
                if uom_def != default_uom:
                    result.update({'warning': {'title': 'Warning !', 'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                qty_final += qty_def
            result.update({'value': {'product_qty': qty_final}})
        return result
    
    _columns = {
        'qty_other': fields.float('Quantity'),
        'uom_other': fields.many2one('product.uom', 'UOM'),
        'uom_ids': fields.one2many('product.uom.other', 'product_id', 'UOM Others'),
        'qty_def': fields.float('Quantity'),
        'qty_1': fields.function(_product_available_1, type='char', size=128, string='Quantity 1'),
        'qty_2': fields.function(_product_available_2, type='char', size=128, string='Quantity 2'),
    }
    
stock_inventory_line()
#######################################
#   Fix quantity in location
#######################################
class stock_location(osv.osv):
    _inherit = "stock.location"
    
    def _product_get_report(self, cr, uid, ids, product_ids=False,
            context=None, recursive=False):
        if context is None:
            context = {}
        product_obj = self.pool.get('product.product')
        context['currency_id'] = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id
        context['compute_child'] = False
        if not product_ids:
            product_ids = product_obj.search(cr, uid, [], context={'active_test': False})

        products = product_obj.browse(cr, uid, product_ids, context=context)
        products_by_uom = {}
        products_by_id = {}
        for product in products:
            products_by_uom.setdefault(product.uom_id.id, [])
            products_by_uom[product.uom_id.id].append(product)
            products_by_id.setdefault(product.id, [])
            products_by_id[product.id] = product

        result = {}
        result['product'] = []
        for id in ids:
            quantity_total = 0.0
            total_price = 0.0
            for uom_id in products_by_uom.keys():
                fnc = self._product_get
                if recursive:
                    fnc = self._product_all_get
                ctx = context.copy()
                ctx['uom'] = uom_id
                qty = fnc(cr, uid, id, [x.id for x in products_by_uom[uom_id]],
                        context=ctx)
                for product_id in qty.keys():
                    if not qty[product_id]:
                        continue
                    product = products_by_id[product_id]
                    quantity_total += qty[product_id]
                    amount_unit = product.price_get('standard_price', context=context)[product.id]
                    price = qty[product_id] * amount_unit
                    total_price += price
                    result['product'].append({
                        'price': amount_unit,
                        'prod_name': product.name,
                        'code': product.default_code,
                        'variants': product.variants or '',
                        'uom': product.uom_id.name,
                        'prod_qty': qty[product_id],
                        'price_value': price,
                        'product_br': product,
                        'qty1': product.qty_1 and product.qty_1 or '',
                        'qty2': product.qty_2 and product.qty_2 or '',
                    })
        result['total'] = quantity_total
        result['total_price'] = total_price
        return result
    
stock_location()
#######################################
#   Fix quantity in product
#######################################
class product_product(osv.osv):
    _inherit = "product.product"

    def _product_available_1(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids):
            if record.uom_ids:
                temp = record.uom_ids[0]
                result[record.id] = '%.2f %s and %.2f %s'%(temp.qty_ex and round(temp.qty_ex,2) or 0, 
                                                     temp.uom_id_ex and temp.uom_id_ex.name or ' ', 
                                                     temp.qty_def and temp.qty_def or 0,
                                                     temp.uom_id_def and temp.uom_id_def.name or ' ',)
            else:
                result[record.id] = '%.2f %s'%(record.qty_available, record.uom_id and record.uom_id.name or ' ')
        return result
    
    def _product_available_2(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        product_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids):
            if record.uom_ids and len(record.uom_ids)>1:
                temp = record.uom_ids[1]
                result[record.id] = '%.2f %s and %.2f %s'%(temp.qty_ex and round(temp.qty_ex,2) or 0, 
                                                     temp.uom_id_ex and temp.uom_id_ex.name or ' ', 
                                                     temp.qty_def and temp.qty_def or 0,
                                                     temp.uom_id_def and temp.uom_id_def.name or ' ',)
            else:
                result[record.id] = ' '
        return result

    _columns = {
        'uom_ids': fields.one2many('product.uom.other', 'product_id', 'UOM Others'),
        'qty_1': fields.function(_product_available_1, type='char', size=128, string='Quantity 1'),
        'qty_2': fields.function(_product_available_2, type='char', size=128, string='Quantity 2'),
    }
        
product_product()

#######################################
#   Fix quantity in sale order line
#######################################
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, line.qty_others and line.qty_others or line.product_uom_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'uom_others': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'qty_others': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        
        'qty_others_1': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        
        'is_other': fields.boolean('Is Other UOM'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }    
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        product_obj = self.pool.get('product.product')
        uom_o_obj   = self.pool.get('product.uom.other')
        if result.get('value',False):
            if product:
                prod_br = product_obj.browse(cr, uid, product)
                uom_def = prod_br.uom_id.id
                lst_uom = [x.uom_id_ex and x.uom_id_ex.id or -1 for x in prod_br.uom_ids] + [uom_def]
#                print lst_uom, '           ', uom
                if uom in lst_uom:
                    pass # print ' trong list'
                else:
                    uom = uom_def
                result['value'].update({'uom_others'  : uom, 
                                        'product_uom' : uom_def,})
            else:
                result['value'].update({'uom_others': 0,
                                        'qty_others': 0})
        return result
    
    def onchange_product_qty(self, cr, uid, ids, uom_other, uom_def, product, qty):
        result = {}
        product_obj = self.pool.get('product.product')
        uom_other_obj = self.pool.get('product.uom.other')
        product_br = product_obj.browse(cr, uid, product)
        if uom_other and uom_def and product:
            uom_other_id = uom_other_obj.search(cr, uid, [('product_id', '=', product),
                                                          ('uom_id_ex', '=', uom_other)])
            uom_other_id = uom_other_id and uom_other_id[0] or 0 
            if uom_other != uom_def and uom_other_id:
                if uom_other:
                    result = {'product_uom_qty'  : float(uom_other_obj.browse(cr, uid, uom_other_id).exchange) * qty}
                else:
                    result = {'product_uom_qty'  : qty}
            else:
                result = {'product_uom_qty'  : qty}
        else:
            result = {'product_uom_qty'  : qty}
        return {'value': result}
    
    def product_uom_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, context=None):
        product_obj = self.pool.get('product.product')
        uom_other = self.pool.get('product.uom.other')
        measure_st = uom
        context = context or {}
        lang = lang or ('lang' in context and context['lang'])
        if not uom:
            return {'value': {'price_unit': 0.0, 'product_uom' : uom or False}}
        result = self.product_id_change(cursor, user, ids, pricelist, product,
                qty=qty, uom=uom, qty_uos=qty_uos, uos=uos, name=name,
                partner_id=partner_id, lang=lang, update_tax=update_tax,
                date_order=date_order, context=context)
        if result.get('value', False):
            def_measure = 0
            if product:
                product_br = product_obj.browse(cursor, user, product)
                def_measure = product_br.uom_id.id
                lst_measure = [(x.uom_id_ex and x.uom_id_ex.id or -1) for x in product_br.uom_ids ]
                lst_measure = lst_measure + [def_measure]
                if measure_st:
                    a = lst_measure
                    if measure_st not in lst_measure + [def_measure]: 
                        result.update({'warning': {'title': 'Warning !', 'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                        result['value'].update({'uom_others'  : 0,
                                                'is_other': 0,
                                                })
                        return result
                    else:
                        if measure_st != def_measure:
                            if measure_st:
                                result['value'].update(self.onchange_product_qty(cursor, user, ids, measure_st, def_measure, product, qty)['value'])
                            result['value'].update({'is_other'  : 1})
                            uom_other_id = uom_other.search(cursor, user, [('product_id', '=', product),
                                ('uom_id_ex', '=', measure_st)])
                            uom_other_id = uom_other_id and uom_other_id[0] or 0
                            result['value'].update({'price_unit': uom_other.browse(cursor, user, uom_other_id).u_price or 0})
                        else:
                            result['value'].update({'is_other': 0})
                
            else:
                result['value'].update({'uom_others': 0,
                                        'qty_others': 0,})
        return result
    
        #    Add color into the invoice
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
                #    Add more color about other quantity and other uom
                'uom_others': line.uom_others and line.uom_others.id or 0,
                'qty_others': line.qty_others and line.qty_others or 0,
            }
        return res
    
sale_order_line()
#######################################
#   Fix quantity in sale order
#######################################
class sale_order(osv.osv):
    _inherit = "sale.order"
#    Fix function in work flow when confirm sale order
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        return {
            'name': line.name,
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id) or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0,
            'uom_others': line.uom_others and line.uom_others.id or 0,
            'qty_others': line.qty_others and line.qty_others or 0,
        }

sale_order()

############################################
#   Fix invoice with more UOM
############################################
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit * (1-(line.discount or 0.0)/100.0)
            taxes = tax_obj.compute_all(cr, uid, line.invoice_line_tax_id, price, line.qty_others and line.qty_others or line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _columns = {
        'uom_others': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'qty_others': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'price_subtotal': fields.function(_amount_line, string='Amount', type="float", digits_compute= dp.get_precision('Account')),
    }
#    Add other UOM for this line
    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None, get_partner=False):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id, 'force_company': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined!'),_("You must first select a partner!") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain':{'product_uom':[]}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain':{'product_uom':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        if type in ('out_invoice','out_refund'):
            a = res.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)
         
        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        result['name'] = res.partner_ref

        result['uos_id'] = uom_id or res.uom_id.id
        if res.description:
            result['name'] += '\n'+res.description

        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}

        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            if type in ('in_invoice', 'in_refund'):
                res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if result['uos_id'] and result['uos_id'] != res.uom_id.id:
            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])
            res_final['value']['price_unit'] = new_price
        
        if res_final.get('value', False):
            res_final['value'].update({'uom_others': res_final['value'].get('uos_id',0)})
        if partner_id:
            if get_partner:
                del res_final['value']['invoice_line_tax_id']
                partner_obj = self.pool.get('res.partner')
                tag_ids = [x.id for x in partner_obj.browse(cr, uid, partner_id).category_id]
                tax_id = []
                if tag_ids:
                    partner_cate_obj = self.pool.get('res.partner.category')
                    for a in tag_ids:
                        temp = partner_cate_obj.browse(cr, uid, a).tax_ids
                        if temp:
                            tax_id += [b.id for b in temp]
                    tax_id = list(set(tax_id))
                res_final['value'].update({'invoice_line_tax_id': tax_id})
        return res_final
        
    def onchange_account_id(self, cr, uid, ids, product_id, partner_id, inv_type, fposition_id, account_id, get_partner=False):
        if not account_id:
            return {}
        unique_tax_ids = []
        fpos = fposition_id and self.pool.get('account.fiscal.position').browse(cr, uid, fposition_id) or False
        account = self.pool.get('account.account').browse(cr, uid, account_id)
        if not product_id:
            taxes = account.tax_ids
            unique_tax_ids = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)
        else:
            product_change_result = self.product_id_change(cr, uid, ids, product_id, False, type=inv_type,
                partner_id=partner_id, fposition_id=fposition_id,
                company_id=account.company_id.id, get_partner=get_partner)
            if product_change_result and 'value' in product_change_result and 'invoice_line_tax_id' in product_change_result['value']:
                unique_tax_ids = product_change_result['value']['invoice_line_tax_id']
        return {'value':{'invoice_line_tax_id': unique_tax_ids}}
    
    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None, get_partner=False):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id})
        warning = {}
        res = self.product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context=context, get_partner=get_partner)
        if not uom:
            res['value']['price_unit'] = 0.0
        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('The selected unit of measure is not compatible with the unit of measure of the product.')
                }
                res['value'].update({'uos_id': prod.uom_id.id})
            return {'value': res['value'], 'warning': warning}
        return res
#    Change product quantity default
    def onchange_product_qty(self, cr, uid, ids, uom_other, uom_def, product, qty):
        result = {}
        product_obj = self.pool.get('product.product')
        uom_other_obj = self.pool.get('product.uom.other')
        product_br = product_obj.browse(cr, uid, product)
        if uom_other and uom_def and product:
            uom_other_id = uom_other_obj.search(cr, uid, [('product_id', '=', product),
                                                          ('uom_id_ex', '=', uom_other)])
            uom_other_id = uom_other_id and uom_other_id[0] or 0 
            if uom_other != uom_def and uom_other_id:
                if uom_other:
                    result = {'quantity'  : float(uom_other_obj.browse(cr, uid, uom_other_id).exchange) * qty}
                else:
                    result = {'quantity'  : qty}
            else:
                result = {'quantity'  : qty}
        else:
            result = {'quantity'  : qty}
        return {'value': result}

    _defaults = {
        'qty_others': 1,
    }
    
account_invoice_line()

#######################################
#   Fix quantity in sale order line
#######################################
class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"


    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.qty_others, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'uom_others': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'qty_others': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
        'qty_others_1': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS')),
        'is_other': fields.boolean('Is Other UOM'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
    }    

    def onchange_product_qty(self, cr, uid, ids, uom_other, uom_def, product, qty):
        result = {}
        product_obj = self.pool.get('product.product')
        uom_other_obj = self.pool.get('product.uom.other')
        product_br = product_obj.browse(cr, uid, product)
        if uom_other and uom_def and product:
            uom_other_id = uom_other_obj.search(cr, uid, [('product_id', '=', product),
                                                          ('uom_id_ex', '=', uom_other)])
            uom_other_id = uom_other_id and uom_other_id[0] or 0 
            if uom_other != uom_def and uom_other_id:
                if uom_other:
                    result = {'product_qty'  : float(uom_other_obj.browse(cr, uid, uom_other_id).exchange) * qty}
                else:
                    result = {'product_qty'  : qty}
            else:
                result = {'product_qty'  : qty}
        else:
            result = {'product_qty'  : qty}
        return {'value': result}

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        result = super(purchase_order_line, self).product_id_change(cr, uid, ids, pricelist, product, \
                qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        product_obj = self.pool.get('product.product')
        if result.get('value',False):
            if product:
                result['value'].update({'uom_others'  : product_obj.browse(cr, uid, product).uom_id.id, 
#                                        'product_uom': product_obj.browse(cr, uid, product).uom_id.id,
                                        })
            else:
                result['value'].update({'uom_others'  : 0,
                                        'qty_others': 0})
        return result
    
    def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        product_obj = self.pool.get('product.product')
        uom_other = self.pool.get('product.uom.other')
        measure_st = uom_id
        context = context or {}
        result = super(purchase_order_line, self).onchange_product_uom(cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order, fiscal_position_id, date_planned, name, price_unit, context)
        if result.get('value', False):
            def_measure = 0
            if product_id:
                product_br = product_obj.browse(cr, uid, product_id)
                def_measure = product_br.uom_id.id
                lst_measure = [(x.uom_id_ex and x.uom_id_ex.id or -1) for x in product_br.uom_ids ]
                lst_measure = lst_measure + [def_measure]
                if measure_st:
                    temp = lst_measure
                    if measure_st not in lst_measure:
                        result.update({'warning': {'title': 'Warning !', 'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                        result['value'].update({'uom_others'  : 0})
                        return result
                    else:
                        if measure_st != def_measure:
                            if measure_st:
                                result['value'].update(self.onchange_product_qty(cr, uid, ids, measure_st, def_measure, product_id, qty)['value'])
            else:
                result['value'].update({'uom_others': 0,
                                        'qty_others': 0,})
        return result

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, context=None):
        if context is None:
            context = {}
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res
        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        dummy, name = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
        if product.description_purchase:
            name += '\n' + product.description_purchase
        res['value'].update({'name': name})
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id
            res['value'].update({'uom_others': product_uom_po_id})
        if product_id:
            product_br = product_product.browse(cr, uid, product_id)
            def_measure = product_br.uom_id.id
            lst_measure = [(x.uom_id_ex and x.uom_id_ex.id or -1) for x in product_br.uom_ids ]
            lst_measure = lst_measure + [def_measure]
            if uom_id:
                if uom_id not in lst_measure:
                    res.update({'warning': {'title': 'Warning !', 'message': 'The selected unit of measure is not compatible with the unit of measure of the product.'}})
                    res['value'].update({'uom_others'  : 0})

        res['value'].update({'product_uom': product_uom_po_id})
        if not date_order:
            date_order = fields.date.context_today(self,cr,uid,context=context)
        supplierinfo = False
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if (qty or 0.0) < min_qty: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})
        if pricelist_id:
            price = product_pricelist.price_get(cr, uid, [pricelist_id],
                    product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order})[pricelist_id]
        else:
            price = product.standard_price

        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})
        return res
    
purchase_order_line()



class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        result = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context)
        result.update({'uom_others': order_line.uom_others and order_line.uom_others.id or 0,
                       'qty_others': order_line.qty_others and order_line.qty_others or 0,})
        return  result
    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        result = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context)
        result.update({'uom_others': order_line.uom_others and order_line.uom_others.id or 0,
                       'qty_others': order_line.qty_others and order_line.qty_others or 0,})
        return result
    
purchase_order()

class res_partner_category(osv.osv):
    _inherit = "res.partner.category"
    _columns = {
        'tax_ids': fields.many2many('account.tax', 'partner_cate_tax_rel', 'partner_cate_id', 'tax_id', 'Taxes'),
    }
    
res_partner_category()