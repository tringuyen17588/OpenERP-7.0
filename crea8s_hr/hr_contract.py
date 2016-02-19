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
import time

from openerp.osv import fields, osv

class hr_notice_period(osv.osv):
    _name = 'hr.notice.period'
    _columns = {
        'name': fields.char('Name', size=128, required=1),
        'code': fields.char('code', size=128),
    }
hr_notice_period()

class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
        'wkpe_date': fields.date('Work Permit Expiry Date'),
        'notice_period': fields.many2one('hr.notice.period', 'Notice Period'),
    }

    _defaults = {
        'wkpe_date': lambda *a: time.strftime("%Y-%m-%d"),
    }

hr_contract()

class hr_payslip_line(osv.osv):

    _inherit = 'hr.payslip.line'
    _columns = {
        'is_compute': fields.boolean('Is Compute'),
    }
    
    _defaults = {
        'is_compute': True,
    }
    
hr_payslip_line()

class hr_salary_rule(osv.osv):

    _inherit = 'hr.salary.rule'
    _columns = {
        'is_compute': fields.boolean('Is Compute'),
    }
    
    _defaults = {
        'is_compute': True,
    }

hr_salary_rule()

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        result = super(hr_payslip, self).get_payslip_lines(cr, uid, contract_ids, payslip_id, context)
        salary_rule_obj = self.pool.get('hr.salary.rule')
        salary_rule_id = salary_rule_obj.search(cr, uid, [('is_compute', '=', False)])
        salary_rule_info = [xx.code for xx in salary_rule_obj.browse(cr, uid, salary_rule_id)]
        if salary_rule_id:
            temp = 0
            for x in result:
                if x.get('code', False) in salary_rule_info:
                    result[temp].update({'is_compute': False})
                temp += 1
        return result
hr_payslip()
