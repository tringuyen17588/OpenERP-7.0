# -*- coding: utf-8 -*-..,

from openerp.osv import fields, osv

class stock_picking_in(osv.osv):
#     _name = 'stock.picking'
    _inherit = 'stock.picking.in' 
    _columns = {
        'crea8s_sale_id': fields.many2one('sale.order', 'Sale Order',
            ondelete='set null', select=True),
        'crea8s_sale_text': fields.char('Sales  Order', size=50),
    }
    
    _defaults = {
        'crea8s_sale_id': False,
    }
  
stock_picking_in()

class stock_picking(osv.osv):
    _inherit = 'stock.picking' 
    _columns = {
        'crea8s_sale_id': fields.many2one('sale.order', 'Sale Order',
            ondelete='set null', select=True),
        'crea8s_sale_text': fields.char('Sales  Order', size=50),
    }
    
stock_picking()