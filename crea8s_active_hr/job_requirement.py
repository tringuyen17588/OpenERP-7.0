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


class crea8s_job_position(osv.osv):
    _name = "crea8s.job.position"
    _description = 'Job Position'
    _columns = {
        'name': fields.char('Name', size=256),        
    }

crea8s_job_position()

class crea8s_srv_pack_type(osv.osv):
    _name = "crea8s.srv.pack.type"
    _description = 'Service Package Type'
    _columns = {
        'name': fields.char('Name', size=256),        
    }

crea8s_srv_pack_type()

class crea8s_job_requirement(osv.osv):
    _name = "crea8s.job.requirement"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Job Requirement'
    
    _columns = {
        'name': fields.char('Job No.', size=256),
        'date': fields.date('Date'),
        'cus_name': fields.many2one('res.partner', "Customer's Name"),
        'res_user': fields.many2one('res.users', "Responsible"),
        'job_pos': fields.many2one('crea8s.job.position', 'Position'),
        'requirement': fields.char("Requirements", size=256),
        'srv_pck_type': fields.many2one('crea8s.srv.pack.type', 'Service Package Type'),
        'job_des': fields.text("Job Description"),
        'wk_hour': fields.char("Working Hours", size=256),
        'sa_range': fields.char('Salary Range', size=256),
        'vacancy': fields.char('Vacancy', size=256),
        'remark': fields.char('Remarks', size=256),
        'oportunity': fields.many2one('crm.lead', 'Opportunity'),        
    }
    
    _defaults = {
        'name': '/',
    }
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.job.requirement') or '/'
        return super(crea8s_job_requirement, self).create(cr, uid, vals, context)

    def _convert_opportunity_data(self, cr, uid, job_number, customer, section_id=False, context=None):
        crm_stage = self.pool.get('crm.case.stage')
        contact_id = False
        if customer:
            contact_id = self.pool.get('res.partner').address_get(cr, uid, [customer.id])['default']
        val = {
            'name': job_number.name and job_number.name or '',
            'partner_id': customer and customer.id or False,
            'type': 'opportunity',
            'date_action': fields.datetime.now(),
            'date_open': job_number.date,
            'job_requirement_id': job_number.id,
            'description': job_number.remark and job_number.remark or '',
            'job_pos': job_number.job_pos and job_number.job_pos.id or 0,
        }
        return val

    def convert_opportunity(self, cr, uid, ids, context={}):
        customer = False
        oppr_obj = self.pool.get('crm.lead')
        oppr_id = oppr_obj.search(cr, uid, [('id', 'in', ids)])
        partner = self.pool.get('res.partner')
        for lead in self.browse(cr, uid, ids, context=context):
            partner_id = lead.cus_name and lead.cus_name.id or 0
            if partner_id:
                customer = partner.browse(cr, uid, partner_id, context=context)
            section_id = 0
            vals = self._convert_opportunity_data(cr, uid, lead, customer, section_id, context=context)
            if oppr_id:
                oppr_obj.write(cr, uid, oppr_id, vals)
                oppr_id = oppr_id[0]
            else:
                oppr_id = oppr_obj.create(cr, uid, vals)
            print 'gia tri kiem tra   ==   ', oppr_id 
            self.write(cr, uid, lead.id, {'oportunity': oppr_id})
        return {'name': 'Opportunity',
                'view_type': 'form',
                'view_mode': 'kanban,tree,form',
                'view_id': False,
                'domain': "[('type','=','opportunity')]",
                'context': "{'default_job_requirement_id': %s,'stage_type': 'opportunity', 'default_type': 'opportunity'}"%ids[0],
                'res_model': 'crm.lead',
                'type': 'ir.actions.act_window'
        }
    
crea8s_job_requirement()