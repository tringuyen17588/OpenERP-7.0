# -*- coding: utf-8 -*-..,
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
##############################################################################

from openerp.osv import fields, osv
# from openerp.tools.translate import _
# from openerp import netsvc


class crea8s_springwell(osv.osv):
    _name = "crea8s.springwell"
    _description = 'crea8s_springwell...'
    _columns = {
        'name': fields.char('springwell...', size=30), 
    }
    
crea8s_springwell()


class crea8s_sw_so_validity(osv.osv):
    """
        Adding fields for Sale Order
    """
    _name = "crea8s.sw.so.validity"
    _description = 'crea8s_sw_validity...'
    _columns = {
        'name': fields.char('Validity', size=100), 
    }
    
crea8s_sw_so_validity()

class crea8s_sw_so_delivery(osv.osv):
    """
        Adding fields for Sale Order
    """
    _name = "crea8s.sw.so.delivery"
    _description = 'crea8s_sw_so_delivery...'
    _columns = {
        'name': fields.char('Delivery', size=100), 
    }
    
crea8s_sw_so_delivery()

class crea8s_sw_so_warranty(osv.osv):
    """
        Adding fields for Sale Order
    """
    _name = "crea8s.sw.so.warranty"
    _description = 'crea8s_sw_so_warranty...'
    _columns = {
        'name': fields.char('Warranty', size=100), 
    }
    
crea8s_sw_so_warranty()


class crea8s_sw_sp_delivery_address(osv.osv):
    """
        Adding fields for Stock Picking
    """
    _name = "crea8s.sw.sp.delivery.address"
    _description = 'crea8s_sw_sp_delivery_address...'
    _columns = {
        'name': fields.char('Delivery Address', size=100), 
    }
    
crea8s_sw_sp_delivery_address()




