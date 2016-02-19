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

class crm_lead(osv.osv):
    _inherit = "crm.lead"
    
    _columns = {
        'natu_bs': fields.char('Nature Of Business', size=256),
        'job_requirement_id': fields.many2one('crea8s.job.requirement', 'Job Requirement'),
        'job_pos': fields.many2one('crea8s.job.position', 'Position'),
    }
    
    def schedule_phonecall(self, cr, uid, ids, schedule_time, call_summary, desc, phone, contact_name, user_id=False, section_id=False, categ_id=False, action='schedule', context=None):
        """
        :param string action: ('schedule','Schedule a call'), ('log','Log a call')
        """
        phonecall = self.pool.get('crm.phonecall')
        model_data = self.pool.get('ir.model.data')
        phonecall_dict = {}
        if not categ_id:
            res_id = model_data._get_id(cr, uid, 'crm', 'categ_phone2')
            if res_id:
                categ_id = model_data.browse(cr, uid, res_id, context=context).res_id
        for lead in self.browse(cr, uid, ids, context=context):
            if not section_id:
                section_id = lead.section_id and lead.section_id.id or False
            if not user_id:
                user_id = lead.user_id and lead.user_id.id or False
            vals = {
                'name': call_summary,
                'opportunity_id': lead.id,
                'user_id': user_id or False,
                'categ_id': categ_id or False,
                'description': desc or '',
                'date': schedule_time,
                'section_id': section_id or False,
                'partner_id': lead.partner_id and lead.partner_id.id or False,
                'partner_phone': phone or lead.phone or (lead.partner_id and lead.partner_id.phone or False),
                'partner_mobile': lead.partner_id and lead.partner_id.mobile or False,
                'priority': lead.priority,
                'com_name': lead.partner_name and lead.partner_name or '',
                'con_name': lead.contact_name and lead.contact_name or '',
            }
            new_id = phonecall.create(cr, uid, vals, context=context)
            phonecall.case_open(cr, uid, [new_id], context=context)
            if action == 'log':
                phonecall.case_close(cr, uid, [new_id], context=context)
            phonecall_dict[lead.id] = new_id
            self.schedule_phonecall_send_note(cr, uid, [lead.id], new_id, action, context=context)
        return phonecall_dict
    
crm_lead()

class crm_phonecall(osv.osv):
    _inherit = "crm.phonecall"
    _columns = {
        'com_name': fields.char('Company Name', size=256),
        'con_name': fields.char('Contact Name', size=256),
        'name': fields.char('Call Summary', size=64),
        'wk_his': fields.text('Work History'),
    }

    def schedule_another_phonecall(self, cr, uid, ids, schedule_time, call_summary, \
                    user_id=False, section_id=False, categ_id=False, action='schedule', context=None):
        """
        action :('schedule','Schedule a call'), ('log','Log a call')
        """
        model_data = self.pool.get('ir.model.data')
        phonecall_dict = {}
        if not categ_id:
            res_id = model_data._get_id(cr, uid, 'crm', 'categ_phone2')
            if res_id:
                categ_id = model_data.browse(cr, uid, res_id, context=context).res_id
        for call in self.browse(cr, uid, ids, context=context):
            if not section_id:
                section_id = call.section_id and call.section_id.id or False
            if not user_id:
                user_id = call.user_id and call.user_id.id or False
            if not schedule_time:
                schedule_time = call.date
            vals = {
                    'name' : call_summary,
                    'user_id' : user_id or False,
                    'categ_id' : categ_id or False,
                    'description' : call.description or False,
                    'date' : schedule_time,
                    'section_id' : section_id or False,
                    'partner_id': call.partner_id and call.partner_id.id or False,
                    'partner_phone' : call.partner_phone,
                    'partner_mobile' : call.partner_mobile,
                    'priority': call.priority,
                    'com_name': call.com_name and call.com_name or '',
                    'con_name': call.con_name and call.con_name or '',
                    
            }
            new_id = self.create(cr, uid, vals, context=context)
            if action == 'log':
                self.case_close(cr, uid, [new_id])
            phonecall_dict[call.id] = new_id
        return phonecall_dict

crm_phonecall()