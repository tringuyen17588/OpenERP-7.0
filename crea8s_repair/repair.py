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
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import csv
import datetime

class crea8s_repair_user(osv.osv):
    _name = "crea8s.repair.user"
    _columns = {
        'name': fields.char('Name', size=256),
    }
crea8s_repair_user()

#    Add property color into stock move
class crea8s_repair(osv.osv):
    _name = "crea8s.repair"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def compute_total(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        result = 0
        res = {}
        for record in self.browse(cr, uid, ids):
            result = record.labor_charge + record.trans_charge + sum([x.amount for x in record.repair_line])
            res[record.id] = result
        return res 

    def onchange_customer(self,cr, uid, ids, customer_id):
        partner_obj = self.pool.get('res.partner.repair')
        partner_br = partner_obj.browse(cr, uid, customer_id)
        return {'value': {'unit_no': partner_br.unit_no and partner_br.unit_no or '',
                          'pos_code': partner_br.postal_code and partner_br.postal_code or '',
                          'block': partner_br.name and partner_br.name or '',}}

    _columns = {
        'name': fields.char('Job Number', size=128),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'cus_repair_id': fields.many2one('res.partner.repair', 'Customer'),
        'block': fields.char('Block and Street', size=256),
        #related('cus_repair_id','block', type='char', store=True, string='Block'),
        'pos_code': fields.char('Postal Code', size=128),
        'unit_no': fields.char('Unit No', size=128),
        #related('cus_repair_id','postal_code', type='char', store=True, string='Postal Code'),
        'dealer_id': fields.char('Dealer', size=256),
        'telephone1': fields.related('cus_repair_id','telephone1', type='char', string='Telephone', store=True),
        'telephone2': fields.related('cus_repair_id','telephone2', type='char', string='2'),
        'telephone3': fields.related('cus_repair_id','telephone3', type='char', string='3'),
        'date': fields.date('Date'),
        'appointment_date': fields.datetime('Appointment Date'),
        'tech_person': fields.many2one('crea8s.repair.user', 'Technician'),
        'model_no': fields.char('Model No', size=256),
        'purchase_date': fields.char('Purchase Date', size=128),
        'attend_by': fields.many2one('crea8s.repair.user', 'Attend By'),
        'type': fields.selection([('INSTALLING', 'INSTALLING'), ('SERVICING', 'SERVICING')], 'Type'),
        'description': fields.text('Description'),
        'remark': fields.text('Remark'),
        'trans_charge': fields.float('Transport Charge', digits=(16,2)),
        'labor_charge': fields.float('Labour Charge', digits=(16,2)),
        'subtotal_charge': fields.float('Sub-Total Charge', digits=(16,2)),
    #fields.function(compute_total, digits_compute=dp.get_precision('Account'), store=True, string='Sub-Total Charge'),
        'state': fields.selection([('draft', 'Draft'), ('open', 'Open'), ('confirm', 'Confirm')], 'State'),
        'repair_line': fields.one2many('crea8s.repair.line', 'repair_id', 'Repair Line'),
        'is_cash': fields.boolean('CASH'),
        'is_cheque': fields.boolean('CHEQUE'),
        'cheque_num': fields.char('Cheque Number'),
        'hide_remark': fields.text('Internal Remark'),
        'amount_total': fields.function(compute_total, digits_compute=dp.get_precision('Account'), string='Total'),
    }
    
    
    
    def default_name(self, cr, uid, context={}):
        return self.pool.get('ir.sequence').get(cr, uid, 'crea8s.repair') or '/'
    
    _defaults = {

        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'name': '/',
    }
    
    def insert_telephone(self, cr, uid, ids, partner_id, telephone):
        partner_obj = self.pool.get('res.partner.repair')
        return partner_obj.write(cr, uid, partner_id, {'telephone1': telephone})
        
    
    def get_partner(self, cr, uid, ids, partner_name, partner_unitno, telephone):
        partner_obj = self.pool.get('res.partner.repair')
        
        partner_id = partner_obj.search(cr, uid, [('name', '=',partner_name),
                                                  ('unit_no', '=', partner_unitno)])
        partner_id = partner_id and partner_id[0] or 0
        if not partner_id: 
            partner_id = partner_obj.search(cr, uid, [('name', '=',partner_name),
                                                      ('telephone1', '=', telephone)])
            partner_id = partner_id and partner_id[0] or 0
        return partner_id
    
    def get_user(self, cr, uid, ids, user_name):
        user_obj = self.pool.get('crea8s.repair.user')
        user_id = user_obj.search(cr, uid, [('name', '=', user_name)])
        user_id = user_id and user_id[0] or 0
        if not user_id:
            user_id = user_obj.create(cr, uid, {'name': user_name})
        return user_id
    
    def get_date(self, date_or):
        result = datetime.date(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]))
        return result
    
    def get_date_time(self, date_or):
        result = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
        return result
    
    def get_state(self, cr, uid, ids, state):
        result = ''
        if state == 'Draft':
            result = 'draft'
        elif state == 'Open':
            result = 'open'
        else:
            result = 'confirm'
        return result
    
    def import_csv_file(self, cr, uid, ids, context={}):
        user_obj = self.pool.get('crea8s.repair.user')
        partner_obj = self.pool.get('res.partner.repair')
        for record in self.browse(cr, uid, ids):
            ifile = open('C:\\Users\\tri\\Desktop\\import\\July15\\import_fanco.csv', 'rb')
            reader = csv.reader(ifile)
            a = 0
            for row in reader:
                a += 1
                if a > 1:
                    if 2>1:
#                    try:
                        cus_id = self.get_partner(cr, uid, ids, row[2], row[5], row[23])
                        attend_id = self.get_user(cr, uid, ids, row[1])
                        tech_id = self.get_user(cr, uid, ids, row[3])
                        vals_re = {
                                        'name': row[4],
                                        'cus_repair_id': cus_id,
                                        'block': row[9],
                                        'pos_code': row[19],
                                        'unit_no': row[5],
                                        'dealer_id': row[14],
                                        'tech_person': tech_id,
                                        'model_no': row[18],
                                        'purchase_date': row[20],
                                        'attend_by': attend_id,
                                        'type': row[6],
                                        'description': row[15],
                                        'remark': row[21],
                                        'trans_charge': row[24] and float(row[24]) or 0,
                                        'labor_charge': row[17] and float(row[17]) or 0,
                                        'subtotal_charge': row[22] and float(row[22]) or 0,
                                        'state': self.get_state(cr, uid, ids, row[7]),
                                        'is_cash': row[10],
                                        'is_cheque': row[11],
                                        'cheque_num': row[12],
                                        'hide_remark': row[16],}
                        if row[13]:
                            vals_re.update({'date': self.get_date(row[13]),})
                        if row[8]:
                            vals_re.update({'appointment_date': self.get_date_time(row[8])})
                        self.create(cr, uid, vals_re)
#                    except:
#                        print row[4], '  ', row[2], '    ', row[5], '    ', row[23]
        return 1
    
    def create(self, cr, uid, vals, context={}):
        if vals.get('name', False) == '/':
            vals['name'] = self.default_name(cr, uid, context)
        return super(crea8s_repair, self).create(cr, uid, vals, context)
    
    def action_open(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'open'})
        #print self.pool.get('res.partner.repair').search(cr, uid, [])
        return 1
    
    def action_confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'confirm'})
        return 1
    
    def action_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'})
        return 1

    def button_dummy(self,cr, uid, ids, context={}):
        return 1
    
crea8s_repair()

class crea8s_repair_line(osv.osv):
    _name = "crea8s.repair.line"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'name': fields.char('Description', size=256),
        'qty': fields.float('Qty', digits=(16,2)),
        'unit_price': fields.float('Unit Price', digits=(16,2)),
        'amount': fields.float('Amount', digits=(16,2)),
        'repair_id': fields.many2one('crea8s.repair', 'Repair'),
    }
    
    def get_product(self, cr, uid, ids, product_name):
        product_obj = self.pool.get('product.product')
        product_id = product_obj.search(cr, uid, [('name', '=',product_name)])
        product_id = product_id and product_id[0] or 0
        return product_id
    
    def get_repair(self, cr, uid, ids, user_name):
        repair_obj = self.pool.get('crea8s.repair')
        repair_id = repair_obj.search(cr, uid, [('name', '=', user_name)])
        repair_id = repair_id and repair_id[0] or 0
        print user_name, ' gia tri repair la ', repair_id 
        return repair_id
        
    def import_csv_file(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            ifile = open('C:\\Users\\tri\\Desktop\\import\\July15\\import_fanco_line.csv', 'rb')
            reader = csv.reader(ifile)
            a = 0
            for row in reader:
                a += 1
                if a > 1:
                    try:
                        product_id = self.get_product(cr, uid, ids, row[1])
                        repair_id = self.get_repair(cr, uid, ids, row[7])
                        vals_re = { 'product_id': product_id,
                                    'name': row[1],
                                    'qty': row[3] and float(row[3]) or 0,
                                    'unit_price': row[4] and float(row[4]) or 0,
                                    'amount': row[5] and float(row[5]) or 0,
                                    'repair_id': repair_id,}
                        self.create(cr, uid, vals_re)
                    except:
                        print row[1], '   ', row[2], '    ', row[7]
        return 1
    
    def onchange_product_id(self, cr, uid, ids, prod_id):
        prod_obj = self.pool.get('product.product')
        result = ''
        if prod_id:
            result = prod_obj.browse(cr, uid, prod_id).name
        return {'value': {'name': result, 
                          'unit_price': 1,
                          'qty': 0,
                          'amount': 0}}
    
    def onchange_quantity(self, cr, uid, ids, prod_id, qty, unit_price):
        return {'value': {'amount': unit_price * qty}}
    
crea8s_repair_line()

class crea8s_warranty(osv.osv):
    _name = "crea8s.warranty"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def compute_total(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        result = 0
        res = {}
        for record in self.browse(cr, uid, ids):
            result = record.labor_charge + record.trans_charge
            res[record.id] = result
        return res 

    _columns = {
        'name': fields.char('Warranty No', size=128),
        'cus_war_id': fields.many2one('res.partner.repair', 'customer'),
        'cus_name': fields.related('cus_war_id','type', type='char', string='''Customer's Name'''),
        'block': fields.char('Block and Street', size=256),
        'pos_code': fields.related('cus_war_id','postal_code', type='char', string='Postal Code'),
        'street': fields.related('cus_war_id','name', type='char', string='Street Name'),
        'unit_no': fields.related('cus_war_id','unit_no', type='char', string='Unit No.'),
        'telephone': fields.related('cus_war_id','telephone1', type='char', string='Telephone'),
        'telephone2': fields.related('cus_war_id','telephone2', type='char', string='2'),
        'pur_inv_no': fields.char('Purchase Invoice No', size=256),
        'model_no': fields.char('Model No.', size=256),
        'purchase_date': fields.date('Date of Purchase'),
        'install_date': fields.date('Date of Installation'),
        'install_by': fields.char('Installed By', size=256),
        'dealer_id': fields.many2one('res.partner', '''Dealer's Name'''),
        'contact_no1': fields.char('Contact No.1', size=256),
        'contact_no2': fields.char('Contact No.2', size=256),
        'contact_no3': fields.char('Contact No.3', size=256),
        'email': fields.related('cus_war_id','email', type='char', string='Email'),
        'state': fields.selection([('draft', 'Draft'), ('open', 'Open'), ('confirm', 'Confirm')], 'State'),
        'remark': fields.text('Remark'),
    }
    
    
    
    def default_name(self, cr, uid, context={}):
        return self.pool.get('ir.sequence').get(cr, uid, 'crea8s.warranty') or '/'
    
    _defaults = {
        'purchase_date': lambda *a: time.strftime('%Y-%m-%d'),
        'state': 'draft',
        'name': '/',
    }
    
    def create(self, cr, uid, vals, context={}):
        
        if vals.get('name', False) == '/':
            vals['name'] = self.default_name(cr, uid, context)
        return super(crea8s_warranty, self).create(cr, uid, vals, context)
    
    def action_open(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'open'})
        return 1
    
    def action_confirm(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'confirm'})
        return 1
    
    def action_cancel(self, cr, uid, ids, context={}):
        self.write(cr, uid, ids, {'state': 'draft'})
        return 1

    def button_dummy(self,cr, uid, ids, context={}):
        return 1
    
crea8s_warranty()