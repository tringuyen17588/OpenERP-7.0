# -*- coding: utf-8 -*-

##############################################################################
#    Module : POS Cashiers
#    Manage cashiers for Point Of Sale
#    Author : Thierry Godin <thierry@lapinmoutardepommedauphine.com>
#    Copyright (C) 2013 Thierry Godin 
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
##############################################################################

{
    'name': 'POS Discount',
    'version': '1.0.0',
    'category': 'Point Of Sale',
    'sequence': 3,
    'author': 'CREA8S',
    'summary': 'Created by CREA8S',
    'website': 'http://wwww.crea8s.com/',
    'summary': 'Created by CREA8S',
    'description': """ Created by CREA8S, Make discount for total amount in POS Order   """,
    'depends': ["point_of_sale"],
    'data': [
    ],
    'js': [
        'static/src/js/pos_discount.js',
    ],
    'css': [
        'static/src/css/pos_discount.css',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}