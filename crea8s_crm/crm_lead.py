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

from openerp.addons.base_status.base_state import base_state
from openerp.addons.base_status.base_stage import base_stage
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time


class crm_district(osv.osv):
    _name = "crm.district"    
    _columns = {
        'name': fields.char('Name', size=256),
        'code': fields.char('Code', size=16),
    }
crm_district()

class crm_territory(osv.osv):
    _name = "crm.territory"    
    _columns = {
        'name': fields.char('Name', size=256),
        'code': fields.char('Code', size=16),
        'road_name': fields.char('Main Road Name', size=256),
        'user_id': fields.many2one('res.users', 'Sale Man'),
        'district_id': fields.many2one('crm.district', 'District'),
    }
crm_territory()

class crm_helpdesk(base_state, base_stage, osv.osv):
    _inherit = "crm.helpdesk"
    _columns = {
        'reference': fields.char('Reference', size=128),
    }
    def create(self, cr, uid, vals, context=None):
        if not 'reference' in vals or not vals['ref']:
            vals.update({'reference': self.pool.get('ir.sequence').get(cr, uid, 'crm.helpdesk')})
        return super(crm_helpdesk, self).create(cr, uid, vals, context)
    
crm_helpdesk()

class crm_lead(osv.Model):
    _inherit = "crm.lead"
    
    _columns = {
        'district_id': fields.many2one('crm.district', 'District'),
        'approve_by': fields.many2one('res.users', 'Approved By'),
        'sale_man_app': fields.many2one('res.users', 'Sale Man'),
        'date_approve': fields.date('Date Approved'),
        'territory_id': fields.many2one('crm.territory', 'Territory'),
        'commercial_partner_id': fields.related('partner_id', 'commercial_partner_id', string='Commercial Entity', type='many2one',
                                                relation='res.partner', readonly=True,
                                                help="The commercial entity that will be used on this lead"),
    }

    def approve_by(self, cr, uid, ids, context={}):
        for x in self.browse(cr, uid, ids):
            self.write(cr, uid, ids, {'date_approve': time.strftime('%Y-%m-%d'),
                                      'approve_by': uid})
        return 1

    def onchange_zip(self, cr, uid, ids, zip, context={}):
        district_obj = self.pool.get('crm.district')
        territory_obj = self.pool.get('crm.territory')
        if zip:
            territory_id = 0
            district_id  = 0
            user_id      = 0
            section_id   = 0
            district_id = district_obj.search(cr, uid, [('name', '=', zip[:2])])
            if district_id:
                district_id = district_id[0]
                territory_code = district_obj.browse(cr, uid, district_id).code
                if territory_code:
                    territory_id = territory_obj.search(cr, uid, [('name', '=', territory_code)])
                    if territory_id:
                        territory_id = territory_id[0]
                    else:
                        territory_id = territory_obj.search(cr, uid, [('district_id', '=', district_id)])
                        territory_id = territory_id and territory_id[0] or 0
            if territory_id:
                user_id = territory_obj.browse(cr, uid, territory_id).user_id
                user_id = user_id and user_id.id or 0
            if user_id:
                section_id = self.pool.get('crm.case.section').search(cr, uid, ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)], context=context)
                section_id = section_id and section_id[0] or 0
            return {'value': {'district_id': district_id,
                              'territory_id': territory_id,
                              'user_id': user_id,
                              'section_id': section_id}}
        return {'value': {'district_id': 0,
                          'territory_id': 0,
                          'user_id': 0,
                          'section_id': 0}}

    def create(self, cr, uid, vals, context=None):
        ids = self.search(cr, uid, [('type', '=', vals.get('type'))])
        result = super(crm_lead, self).create(cr, uid, vals, context)
        partner_id = self.browse(cr, uid, result).commercial_partner_id        
        partner_ids = [(x.commercial_partner_id and x.commercial_partner_id.id or -1) for x in self.browse(cr, uid, ids)]
        partner_id = partner_id and partner_id.id or 0
        if partner_id in partner_ids:
            raise osv.except_osv('Warning !', 'The customer must be unique !')
        return result

    _sql_constraints = [
        ('customer_type_uniq', 'unique(type, partner_name)', 'The customer must be unique !')
    ]
    
crm_lead()

class res_partner(osv.osv):
    _inherit = "res.partner"
        
    _sql_constraints = [
        ('name_uniq', 'unique(name,is_company,)', 'The customer must be unique !')
    ]

    def add_constrain(self, cr, uid, ids, context=None):
        try:
            sql = ''' CREATE UNIQUE INDEX name_uniq_constrain ON res_partner (LOWER(name)); '''
            cr.execute(sql)
            return True
        except:
            return False
        return True

res_partner()