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
    'name': 'crea8s_vector_quo',
    'version': '1.0',
    'category': 'crea8s_vector_quo',
    'sequence': 14,
    'summary': 'Customizing for Vector project.',
    'description': """  
    * crea8s_vector_quo module with features below:   
    1. Creating reports "Vector Quotation" and "Vector Bill of Material" For VectorInfoTech.
    2. Putting some fields at Quotation, customizing its form view. 
    3. At SO lines: Create field percentage of Profit Margin  
    4. At SO in draft: Field Order Date will be auto-updated to current date. 
    5. At Incoming Shipment: Create field SO number, link to SO.  
    6. At SO: Create Cost Sheet printout. 
    """,
    'author': 'CREA8S',
    'website': 'http://www.crea8s.com/',
    'images': [],
    'depends': ['base', 'sale', 'sale_margin', 'stock' ],
    'data': [
			'crea8s_vector_quo_view.xml',
			'stock_view.xml', 
            'sale_view.xml',
            'res_company_view.xml',
            'report_folder/crea8s_vector_report.xml'
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}



