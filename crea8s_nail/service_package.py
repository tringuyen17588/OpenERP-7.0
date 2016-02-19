# -*- coding: utf-8 -*-..,
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
import datetime
from datetime import datetime
import tzlocal
from tzlocal import get_localzone
# 
class crea8s_nail_service_package(osv.osv):
    _name = "crea8s.nail.service.package"
    _description = 'crea8s_nail_service_package.....'
    
    
    def _get_balance(self, cr, uid, ids, field_name, arg, context=None):
       """
       _get_balance: get balance (by last visit date)
        :return res: dictionary value 
        """

       res = {}
       nuBalance = 0.0
       #search details, order by DATE       
       clsSer = self.pool.get('crea8s.nail.service.package');
       clsSerDet = self.pool.get('crea8s.nail.service.package.detail');
       
       
       for service in self.browse(cr, uid, ids, context=context):
           
           nuBalance = 0.0
           arrIDs = clsSerDet.search(cr, uid, [('service_number','=',service.id)], order='date')
           
           if len(arrIDs) > 0:
               objDet = clsSerDet.browse(cr, uid, arrIDs[len(arrIDs)-1], context=None)
               nuBalance = objDet.balance
               
           res[service.id] = nuBalance 
       return res
   
   
    def _get_date(self, cr, uid, ids, field_names, arg, context=None):  
       """
       _get_date: Get start date, last visit date
        :return res: dictionary value 
        """
        
       #search details, order by DATE       
       clsSer = self.pool.get('crea8s.nail.service.package');
       clsSerDet = self.pool.get('crea8s.nail.service.package.detail');
       res = {}
       dCurrentDate = datetime.now(get_localzone())
       strFM = '%Y-%m-%d'     #         dCurrentDate.strftime(strFM)
       dCurrDate = dCurrentDate.strftime(strFM)
       for service in self.browse(cr, uid, ids, context=context):
           
           dLastDate = dCurrDate
           dStartDate = dCurrDate
           res[service.id] = {}
           arrIDs = clsSerDet.search(cr, uid, [('service_number','=',service.id)], order='date')
           
           if len(arrIDs) > 0:
               objDet = clsSerDet.browse(cr, uid, arrIDs[0], context=None)
               dStartDate = objDet.date
               objDet = clsSerDet.browse(cr, uid, arrIDs[len(arrIDs)-1], context=None)
               dLastDate = objDet.date
           res[service.id]['start_date'] = dStartDate
           res[service.id]['late_visit_date'] = dLastDate
#            print res
#            res[service.id] = dLastDate # no multi='aaaa'
       return res
    
    def _get_date_write_value(obj, cr, uid, id, name, value, fnct_inv_arg, context):
        
        return True
    _columns = {
        'name': fields.related('service_list', 'name', type="char", relation="crea8s.nail.service.package.listname", string="Name", readonly=True),
        'service_number': fields.char('Service number', size=20),
        'customer': fields.many2one('res.partner', 'Customer'),# ???: change_default=True, select=True, track_visibility='always'
        
        'service_list': fields.many2one('crea8s.nail.service.listname', 'Service Name', required=True),# ???: change_default=True, select=True, track_visibility='always'
#         'balance': fields.float('Balance', digits=(3,1)),
        'tel': fields.char('Tel', size=12),
        'start_date': fields.function(_get_date, string='Start Date', type='date', readonly=True, fnct_inv=_get_date_write_value, multi="_get_date_multiss"),
        'late_visit_date': fields.function(_get_date, string='Last Visit Date', type='date', readonly=True, fnct_inv=_get_date_write_value, multi="_get_date_multiss"),
#         'late_visit_date': fields.date('Last Visit Date', readonly=True),
        'ref_detail_id': fields.one2many('crea8s.nail.service.package.detail', 'service_number', 'Details'),
        
#         'balance': fields.function(_get_balance, string='Balance.', type='float', method=True)
        'balance': fields.function(_get_balance, string='Balance', type='float', method=True, store=True)
      
    }
        
        
#     strFormatTime = '%Y-%m-%d %H:%M:%S %Z'
    def action_service_detail(self, cr, uid, ids, context={}):
       """
       Showing details under viewing-mode, click 'edit' for entering edit-mode.
        :return dict: dictionary value for created view
        """

#        objDet = self.pool.get('crea8s.nail.service.package.detail').browse(cr, uid, ids)
#        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'crea8s_nail', 'action_crea8s_nail_service_package_detail', context)
#        return res
       
       # redisplay the record as a sales order
       view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'crea8s_nail', 'view_crea8s_nail_service_package_form')
       view_id = view_ref and view_ref[1] or False,
       return {
            'type': 'ir.actions.act_window',
            'name': _('Service Package'),
            'res_model': 'crea8s.nail.service.package',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current', # new: opens in edit mode (as when creating wizards..) ; inline: 
            'nodestroy': True,
            'context': context,
            
        }
        
    def create(self, cr, uid, arrVals, context=None):
        
#         arrVals['name'] += '.'
        arrVals['service_number'] = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.nail.service.package')
        return super(crea8s_nail_service_package, self).create(cr, uid, arrVals, context)
    
    def write(self, cr, uid, ids, arrVals, context=None):
        
        # change name; case 2: browse self ; only on WRITE/UPDATE methods   ////
#         # decode/ encode
#         # n''
        objTemp = self.pool.get('crea8s.nail.service.package.detail');

        if arrVals.has_key('balance') == False:
            nuBal = 0.0
            arrService = self.read(cr, uid, ids[0], context=context)
            if  arrService:
                arrDetailID = arrService['ref_detail_id']
                objDetail = objTemp.browse(cr, uid, arrDetailID, context=context)
                
                if len(objDetail) > 1:
                    objItem = objDetail[len(objDetail)-1]
                    nuBal = objItem.balance
            arrVals['balance'] = nuBal 
            
        else:
            arrVals['balance'] = arrVals['balance']
        
        return super(crea8s_nail_service_package, self).write(cr, uid, ids, arrVals, context)
    

class crea8s_nail_service_package_detail(osv.osv):
    _name = "crea8s.nail.service.package.detail"
    _description = 'crea8s_nail_service_package_detail..... '
    _columns = {
        
        'service_number': fields.many2one('crea8s.nail.service.package', 'Service(s)', readonly=True),
        'date': fields.date('Date'),
        'staff': fields.many2one('hr.employee', 'Staff'),
        'service_list': fields.many2one('crea8s.nail.service.listname', 'Service(s)'),
        'balance': fields.float('Balance', digits=(3,1), readonly=True),
        'remarks': fields.text('Remarks', size=256),
        'amount_in': fields.float('In', digits=(3,1)),
        'amount_out': fields.float('Out', digits=(3,1)),
    }
    _default = {
        'remarks': fields.date.context_today, 
    }
    
    def get_balance_total(self, cr, uid, srv_num, idd=None):
        idd = idd and [('service_number', '=', srv_num),('id', '<', idd)] or [('service_number', '=', srv_num)]
        lst_ids = self.search(cr, uid, idd)
        total_in_num = 0
        total_out_num = 0
        for record in self.browse(cr, uid, lst_ids):
            total_in_num += record.amount_in
            total_out_num += record.amount_out
        return total_in_num - total_out_num 
    
    def create(self, cr, uid, arrVals, context=None):
        # calculate balance
        numIn = 0.0 if (arrVals.has_key('amount_in') == False) else arrVals['amount_in'] # requires python version >= 2.5
        numOut = 0.0 if (arrVals.has_key('amount_out') == False) else arrVals['amount_out'] # requires python version >= 2.5
        arrVals['balance'] = numIn- numOut + self.get_balance_total(cr, uid, arrVals['service_number'], None)
        return super(crea8s_nail_service_package_detail, self).create(cr, uid, arrVals, context)
    
    def write(self, cr, uid, ids, arrVals, context=None):
        # detail: LOOP many times.
        clsSer = self.pool.get('crea8s.nail.service.package');
        clsSerDet = self.pool.get('crea8s.nail.service.package.detail');
        arrSerDet2 = clsSerDet.browse(cr, uid, ids[0], context=context)
        arrSer = clsSer.browse(cr, uid, arrSerDet2.service_number.id, context=context)
        # step01: calculate balance for children.
        numIn = arrSerDet2.amount_in if (arrVals.has_key('amount_in') == False) else arrVals['amount_in'] # requires python version >= 2.5
        numOut = arrSerDet2.amount_out if (arrVals.has_key('amount_out') == False) else arrVals['amount_out'] # requires python version >= 2.5
        arrVals['balance'] = numIn - numOut + self.get_balance_total(cr, uid, self.browse(cr, uid, ids[0]).service_number.id, ids[0])
        return super(crea8s_nail_service_package_detail, self).write(cr, uid, ids, arrVals, context)
        
        
class crea8s_nail_service_listname(osv.osv):
    _name = "crea8s.nail.service.listname"
    _description = 'crea8s_nail_service_listname.....'
    _columns = {
        'name': fields.char('Service Name', size=20),
        'service_father': fields.one2many('crea8s.nail.service.package', 'service_list', 'service_father...'),
        'service_child': fields.one2many('crea8s.nail.service.package.detail', 'service_list', 'service_father...'),
        'is_pck': fields.boolean('Package'),
    }
    
    def pck_default(self, cr, uid, context):
        if context.get('is_pck', False):
            return 1
        return 0
    
    _defaults = {
        'is_pck': pck_default,
    }
    
crea8s_nail_service_package()
crea8s_nail_service_package_detail()
crea8s_nail_service_listname()



