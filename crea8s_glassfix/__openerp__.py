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
    'name': 'Glass-Fix Pte Ltd Project',
    'version': '1.0',
    'category': 'Glass-Fix Pte Ltd',
    'sequence': 14,
    'summary': 'Messaging, Sales, Accounting, Purchases, Human Resource',
    'description': """  Refer on website: ....  """,
    'author': 'Crea8s',
    'website': 'http://www.crea8s.com/',
    'images': ["images/crea8s.gif"],
    'depends': ['base', 'sale', 'account', 'purchase', 'hr', 'product', 'crm', 'account_voucher'],
    'data': ["sale_security.xml",
             
             "sale_view.xml",
             
             "glassfix_report.xml","account_view.xml",],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
