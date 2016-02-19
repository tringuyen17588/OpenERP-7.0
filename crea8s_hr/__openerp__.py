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

{
    'name': 'Employee Management By Crea8s',
    'version': '1.1',
    'author': 'Crea8s',
    'category': 'Human Resources',
    'sequence': 21,
    'website': 'http://www.crea8s.com',
    'summary': 'Jobs, Departments, Employees Details',
    'description': """ Human Resources Management """,
    'images': ["images/crea8s.gif"],
    'depends': ['survey', 'hr', 'hr_recruitment', 'hr_contract', 'hr_attendance', 'hr_holidays', 'hr_timesheet', 'hr_payroll'],
    'data': ["res_partner_view.xml",
             "hr_security.xml",
             "hr_recruitment_view.xml",
             "hr_contract_view.xml",
             "hr_view.xml",
             "hr_payroll_report.xml",
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
