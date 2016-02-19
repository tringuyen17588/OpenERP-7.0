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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
import datetime
from datetime import timedelta
import psycopg2

class crea8s_migration(osv.osv):
    _name = "crea8s.migration"
    
    _columns = {
        'name': fields.char('Localhost', size=128),
        'user': fields.char('User', size=128),
        'password': fields.char('Password', size=128),
        'database': fields.char('Database', size=128),
        'port': fields.char('Port', size=128),
        'model': fields.many2one('ir.model', 'Model'),
    }
    
    def connect(self, cr, uid, ids, context={}):
        connect = False
        try:
            for record in self.browse(cr, uid, ids):
                connect = psycopg2.connect(database=record.database, user=record.user, password=record.password,host=record.name, port=record.port)
        except:
            print 'Ket noi khong thanh cong'
        return connect
    
    def migration_database(self, cr, uid, ids, context={}):
        model = ''
        all_line = []
        result = 0
        partner_obj = self.pool.get('res.partner')
        connect = self.connect(cr, uid, ids, context)
        for record in self.browse(cr, uid, ids):
            model = record.model and record.model.model or ''
            cursor = connect.cursor()
            sql = ''' select name from ir_model_fields where model = '%s' '''%model
            cursor.execute(sql)
            result = cursor.fetchall()
            str_columns = ''
            columns = []
            for x in result:
                if x[0] not in ['contact_address', 'child_ids', 'user_ids', 'has_image','commercial_partner_id', 'tz_offset', 
                                'bank_ids', 'country', 'category_id', 'message_summary','message_unread', 'message_follower_ids', 
                                'message_is_follower', 'message_ids', 'property_product_pricelist', 'invoice_ids', 'signup_valid',
                                'signup_url', 'property_account_position', 'contract_ids', 'ref_companies', 'property_account_receivable',
                                'property_account_payable', 'property_supplier_payment_term', 'property_payment_term',
                                'property_stock_customer', 'property_stock_supplier', 'property_product_pricelist_purchase', 'debit', 'credit', 
                                'sale_order_ids', 'sale_order_count', 'opportunity_count', 'phonecall_ids', 'meeting_ids', 'meeting_count',
                                'opportunity_ids', 'purchase_order_count', 'purchase_order_ids', 'vcl_country', 'state', 'payment_cus', 
                                'country_id', 'image', 'has_image', 'image_medium', 'image_small', 'brand_id']:
                    str_columns += x[0] + ','
                    columns.append(x[0])
            str_columns = str_columns[:len(str_columns)-1]
            sql_db = ''' select %s from res_partner '''%str_columns
            cursor.execute(sql_db)
            result = cursor.fetchall()
            for kq in result:
                dict = {}
                for index in range(0,len(columns)-1):
                    dict.update({columns[index]: kq[index]})
                partner_obj.create(cr, uid, dict)
#                all_line.append(dict)
            print all_line
        return 1
    
crea8s_migration()
