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
        'is_readonly': fields.function(check_readonly, type='boolean', string='Readonly', store={
                'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['user_id'], 20)}),
    }
    
res_partner()

class crea8s_job_candidate(osv.osv):
    _inherit = "crea8s.job.candidate"
    def check_readonly(self, cr, uid, ids, field_name, arg, context=None):
        user_obj = self.pool.get('res.users')
        res = {}
        rs = 0
        for record in self.browse(cr, uid, ids):
            for x in user_obj.browse(cr, uid, uid).groups_id:
                if x.name == 'Only Read Customer':
                    if record.res_user:
                        if record.res_user.id == uid:
                            res[record.id] = 1
                        else:
                            res[record.id] = 0
                    else:
                        res[record.id] = 0
                else:
                    res[record.id] = 0
        return res
    _columns = {
        'is_readonly': fields.function(check_readonly, type='boolean', string='Readonly', store={
                'crea8s.job.candidate': (lambda self, cr, uid, ids, c={}: ids, ['res_user'], 20)}),
    }
crea8s_job_candidate()