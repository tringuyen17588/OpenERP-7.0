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
    'name': 'Add access right',
    'version': '1.0',
    'category': 'Access Right',
    'sequence': 14,
    'summary': 'Add access right',
    'description': """  Add access right for Fanco created By Crea8s  """,
    'author': 'Crea8s',
    'website': 'http://www.crea8s.com/',
    'images': [],
    'depends': ['sale', 'account'],
    'data': ["access_right.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}