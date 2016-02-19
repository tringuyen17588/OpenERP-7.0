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

#for logging 
import logging
_logger = logging.getLogger(__name__) 


class service_note(osv.Model):
    """ Service Note 
    """
    _name = "crea8s.sw.service.note"
    _columns = {
        'name': fields.char('Work Order No', size=128), #crea8s_sw_work_order_no
        'crea8s_sw_your_po_no': fields.char('Your P/Order No', size=128),
        'crea8s_sw_date': fields.date('Date'),
        'crea8s_sw_model_of_machine': fields.char('Model of Machine', size=128),
        'crea8s_sw_ms': fields.text('M/S'),
        'crea8s_sw_partner_id': fields.many2one('res.partner', 'Customer'), 
        'crea8s_sw_description': fields.text('Description'), 
    }
    
    def create(self, cr, uid, vals, context=None):
        # get current sequence of Work Order No... 
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.sw.work.order.no')
#         _logger.info('def create()..' + str(vals))
        return super(service_note, self).create(cr, uid, vals, context)
# , store={
#                 'service.note.line': (_get_order, ['margin'], 20),
#                 'service.note': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 20),
#                 }
    
    # _sql_constraints = [(
        # 'sale_id_instance_unique', 'unique(crea8s_sale_id, crea8s_sale_instance)',
        # 'A sale must be unique in an instance' # PhongND
    # )]


    
