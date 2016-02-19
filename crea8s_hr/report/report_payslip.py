#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.report import report_sxw
from openerp.tools import amount_to_text_en

class payslip_report_fix(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(payslip_report_fix, self).__init__(cr, uid, name, context)
        self.sum_gross = 0
        self.sum_deduct = 0
        self.localcontext.update({
            'get_payslip_lines_gross': self.get_payslip_lines_gross,
            'get_payslip_lines_deduction': self.get_payslip_lines_deduction,
            'get_gross': self.get_gross,
            'get_deduct': self.get_deduct,
            'get_net': self.get_net,
        })

    def get_payslip_lines_deduction(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        salary_rule = self.pool.get('hr.salary.rule.category')
        self.sum_deduct = 0
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                ids.append(obj[id].id)
        if ids:
            salary_rule_ids = salary_rule.search(self.cr, self.uid, ['|', 
                                                                     ('name', '=', 'Deduction'),
                                                                     ('name', '=', 'deduction')])
            idd = payslip_line.search(self.cr, self.uid, [('id', 'in', ids),
                                                          '|', '|', 
                                                          ('rate', '<', 0),
                                                          ('category_id', 'in', salary_rule_ids),
                                                          ('amount', '<', 0)])
            res = payslip_line.browse(self.cr, self.uid, idd)            
            self.sum_deduct = abs(sum([x.total for x in res]))
        return res
    
    def get_payslip_lines_gross(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        salary_rule = self.pool.get('hr.salary.rule.category')
        self.sum_gross = 0
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip == True:
                ids.append(obj[id].id)
        if ids:
            salary_rule_ids = salary_rule.search(self.cr, self.uid, [
                                                                     '|', 
                                                                     ('name', '=', 'Deduction'),
                                                                     ('name', '=', 'deduction')])
            idd = payslip_line.search(self.cr, self.uid, [('id', 'in', ids),
                                                          ('category_id', 'not in', salary_rule_ids)])
            res = payslip_line.browse(self.cr, self.uid, idd)
            self.sum_gross = abs(sum([x.is_compute and x.total or 0 for x in res]))
        return res
    
    def get_gross(self):
        return self.sum_gross
    
    def get_deduct(self):
        return self.sum_deduct
    
    def get_net(self):
        return self.sum_gross - self.sum_deduct
    
report_sxw.report_sxw('report.payslip_report_fix', 'hr.payslip', 'crea8s_hr/report/report_payslip.rml', parser=payslip_report_fix)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
