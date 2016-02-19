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
    'name': 'MS Media - Crea8s',
    'version': '1.0',
    'category': 'MS Media',
    'sequence': 10,
    'summary': 'MS Media',
    'description': """  Customize MS Media created by CREA8S  """,
    'author': 'Crea8s',
    'website': 'http://www.crea8s.com/',
    'images': [],
    'depends': ['sale', 'account', 'base'],
    'data': ["msmedia_view.xml"],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}

