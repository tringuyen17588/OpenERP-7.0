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
    Purchase Order

    :copyright: (c) 2014-2015 crea8s
	:author: by PhongND
    :license: AGPLv3, see LICENSE for more details
'''
from openerp.osv import osv, fields
# from openerp.tools.translate import _ 

#for logging 
import logging
_logger = logging.getLogger(__name__) 
from openerp import netsvc

class purchase_order(osv.Model):
    """ Purchase Order
    """
    _inherit = 'purchase.order'
    _columns = {
        'crea8s_terms': fields.char('Terms', size=100),
        
    }
    
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the request for quotation and mark it as sent, so that we can see more easily the next step of the workflow
        copy from ...\addons\purchase\purchase.py > 
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'purchase.order', ids[0], 'send_rfq', cr)
        datas = {
                 'model': 'purchase.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'crea8s_springwell_po01', 'datas': datas, 'nodestroy': True}
    
    
    # _sql_constraints = [(
        # 'sale_id_instance_unique', 'unique(crea8s_sale_id, crea8s_sale_instance)',
        # 'A sale must be unique in an instance' # PhongND
    # )]

