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

class crea8s_job_candidate(osv.osv):
    _name = "crea8s.job.candidate"
    _order = 'date desc'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.char('Candidate Name', size=256),
        'date': fields.date('Date'),
        'job_pos': fields.many2one('crea8s.job.position', 'Position Apply'),
        'res_user': fields.many2one('res.users', 'Responsible'),
        'wk_exp': fields.char("Work Experience", size=256),
        'sa_exp': fields.char("Expected Salary", size=256),
        'qualification': fields.char('Qualification', size=256),
        'attach_resume': fields.char('Attached Resume', size=256),
        'remark': fields.char('Remarks', size=256),
        'wk_his': fields.text('Work History'),
        'mobile': fields.char('Mobile', size=256),
    }

crea8s_job_candidate()


class crm_phonecall(osv.osv):
    _inherit = "crm.phonecall"
    _columns = {
        'can_id': fields.many2one('crea8s.job.candidate', 'Candidate'),
    }
#    Convert from Logged call into Candidate
    def convert_to_candidate(self, cr, uid, ids, context=None):
        job_candidate_obj = self.pool.get('crea8s.job.candidate')
        can_id = 0
        for record in self.browse(cr, uid, ids):
            if record.can_id:# If exist candidate link to this logged call
                can_id = record.can_id.id
            else:
                can_id = job_candidate_obj.create(cr, uid, {
                     'name': record.con_name and record.con_name or '',
                     'remark': record.description and record.description or '',
                     'date': record.date})
                self.write(cr, uid, ids, {'can_id': can_id})# Update logged call for candidate 
        models_data = self.pool.get('ir.model.data')
        form_view = models_data.get_object_reference(cr, uid, 'crea8s_active_hr', 'view_crea8s_candidate_form')[1]
        tree_view = models_data.get_object_reference(cr, uid, 'crea8s_active_hr', 'view_crea8s_candidate_tree')[1]
        return {'name': _('Candidate'),
                'view_type': 'form',
                'view_mode': 'tree, form',
                'res_model': 'crea8s.job.candidate',
                'res_id': int(can_id),
                'view_id': False,
                'views': [(form_view or False, 'form'),
                        (tree_view or False, 'tree'),
                        (False, 'calendar'), (False, 'graph')],
                'type': 'ir.actions.act_window',}

crm_phonecall()
class res_partner(osv.osv):
    _inherit = "res.partner"
    
    def check_readonly(self, cr, uid, ids, field_name, arg, context=None):
        user_obj = self.pool.get('res.users')
        res = {}
        rs = 0
        for record in self.browse(cr, uid, ids):
            for x in user_obj.browse(cr, uid, uid).groups_id:
                if x.name == 'Only Read Customer':
                    if record.user_id:
                        if record.user_id.id == uid:
                            res[record.id] = 1
                        else:
                            res[record.id] = 0
                    else:
                        res[record.id] = 0
                else:
                    res[record.id] = 0
        return res
    
    _columns = {
        'is_readonly': fields.function(check_readonly, type='boolean', string='Readonly'),
    }
        
res_partner()