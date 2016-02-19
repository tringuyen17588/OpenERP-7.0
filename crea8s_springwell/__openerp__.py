# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Crea8s (http://www.crea8s.com) All Rights Reserved.
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
    'name': 'crea8s_springwell',
    'version': '1.0',
    'category': 'crea8s_springwell',
    'sequence': 14,
    'summary': 'Customizing for Springwell project.',
    'description': """  
    * crea8s_springwell module with features below:   
    1. Creating report "Springwell Quotation/Order" For SO, PO.
    2. Creating report "Springwell Delivery Order".
    3. Creating report "Springwell Service Note".
    4. Creating report "Springwell Invoice".
    5. Creating new function "Service Note".
    6. Putting some fields at SO,PO,DO,Invoice; customizing their form views. 
    """,
    'author': 'CREA8S',
    'website': 'http://www.crea8s.com/',
    'images': [],
    'depends': ['base', 'sale', 'purchase', 'stock', 'account'],         
    'data': [
			'crea8s_springwell_view.xml',
			'sale_view.xml',
			'service_note.xml',
			'stock_view.xml',
			'purchase_view.xml',
			'account_view.xml',
            'report_folder/crea8s_springwell_report.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
	
}