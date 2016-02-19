# -*- coding: utf-8 -*-..,
##############################################################################
#
#    @author: PhongND
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


# -*- coding: UTF-8 -*-
'''
    sale

    :copyright: (c) 2014-2015 crea8s
	:author: by PhongND
    :license: AGPLv3, see LICENSE for more details
'''
from openerp.osv import osv, fields
# from openerp.tools.translate import _
import time
import datetime
from datetime import timedelta
from datetime import datetime
from openerp import netsvc 

#for logging 
import logging
_logger = logging.getLogger(__name__) 


class sale_order(osv.Model):
    """ Sale Order
    """
    _inherit = 'sale.order'
    _columns = {
#         'crea8s_sw_work_order_no': fields.char('Work Order No', size=128),
#         'crea8s_sw_your_po_no': fields.char('Your P/Order No', size=128),
        'crea8s_sw_validity': fields.many2one('crea8s.sw.so.validity','Validity'),
        'crea8s_sw_delivery': fields.many2one('crea8s.sw.so.delivery','Delivery'),
        'crea8s_sw_warranty': fields.many2one('crea8s.sw.so.warranty','Warranty'),
#         'crea8s_sw_ms': fields.text('M/S'),
        
    }
    
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        copy from: ...\addons\sale\sale.py > class sale_order > def print_quotation(..)
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'quotation_sent', cr)
        datas = {
                 'model': 'sale.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'crea8s_springwell_quo01', 'datas': datas, 'nodestroy': True} 
    
#     def create(self, cr, uid, vals, context=None):
#         # get current sequence of Work Order No... 
#         vals['crea8s_sw_work_order_no'] = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.sw.work.order.no')
# #         _logger.info('def create()..' + str(vals))
#         return super(sale_order, self).create(cr, uid, vals, context)

# , store={
#                 'sale.order.line': (_get_order, ['margin'], 20),
#                 'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 20),
#                 }
    
    # _sql_constraints = [(
        # 'sale_id_instance_unique', 'unique(crea8s_sale_id, crea8s_sale_instance)',
        # 'A sale must be unique in an instance' # PhongND
    # )]


    
# class delivery_order
#     """ Sale Order
#     """