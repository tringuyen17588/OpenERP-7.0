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
    'name': 'Document Management Crea8s',
    'version': '1.0',
    'category': 'Document Management',
    'sequence': 14,
    'summary': 'Document Magagement Module created by Crea8s',
    'description': """  Document Magagement Module created by Crea8s  """,
    'author': 'Crea8s',
    'website': 'http://www.crea8s.com',
    'images': [],
    'depends': ['base', 'document', 'crm'],
    'data': ["res_partner_view.xml",
             "security/security.xml",
             "security/ir.model.access.csv"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

