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

#    Address type for customer repair
class res_partner_repair_type(osv.osv):
    _name = "res.partner.repair.type"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.char('Name', size=256),
        'code': fields.char('Code', size=128),
    }
        
res_partner_repair_type()

#    Address for customer repair
class res_partner_repair(osv.osv):
    _name = "res.partner.repair"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.char('Block and Street', size=256),
        'unit_no': fields.char('Unit No', size=128),
        'type': fields.char('Type', size=256),
        'area': fields.char('Area', size=256),
        'stress': fields.char('Name', size=256),
        'postal_code': fields.char('Postal Code', size=32),
        'block': fields.char('Block', size=256),
        'telephone1': fields.char('Telephone', size=128),
        'telephone2': fields.char('Telephone 2', size=128),
        'telephone3': fields.char('Telephone 3', size=128),
        'email': fields.char('Email', size=128),
        'remark': fields.text('Remark'),
        'is_serving': fields.boolean('Is Serving'),
        'is_warranty': fields.boolean('Is Warranty'),
    }
    def add_constrain(self, cr, uid, ids, context=None):
        try:
            cr.execute('DROP INDEX IF EXISTS block_street_unitno_unique;')
            sql = ''' CREATE UNIQUE INDEX block_street_unitno_unique ON res_partner_repair (LOWER(name), LOWER(unit_no), is_serving, is_warranty); '''
            cr.execute(sql)
            return True
        except:
            return False
        return True
    _sql_constraints = [
        ('block_street_unitno_uniq', 'unique(name, unit_no, is_serving, is_warranty)', 'The block and street and unit no must be unique !')
    ]
    
    def import_partner(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            ifile = open('C:\\Users\\tri\\Desktop\\import\\July15\\partner_import.csv', 'rb')
            reader = csv.reader(ifile)
            a = 0
            for row in reader:
                a += 1
                if a > 1:
                    try:
                        vals_re = { 'name': row[0] and row[0] or '',
                                    'unit_no': row[10] and row[10] or '',
                                    'type': row[3] and row[3] or '',
                                    'area': row[11] and row[11] or '',
                                    'stress': row[4] and row[4] or '',
                                    'postal_code': row[5] and row[5] or '',
                                    'block': '',
                                    'telephone1': row[7] and row[7] or '',
                                    'telephone2': row[8] and row[8] or '',
                                    'telephone3': row[9] and row[9] or '',
                                    'email': '',
                                    'remark': row[6] and row[6] or '',
                                    'is_serving': row[1] and row[1] or '',
                                    'is_warranty': row[2] and row[2] or '',}
                        if not self.search(cr, uid, [('name', '=', row[0]),
                                                 ('unit_no', '=', row[10])]):
                            self.create(cr, uid, vals_re)
                    except:
                        print row[1], '   ', row[2], '    ', row[7]
        return 1
    
    def create(self, cr, uid, vals, context=None):
        result = 0
        try:
            result = super(res_partner_repair, self).create(cr, uid, vals, context)
        except:
            raise osv.except_osv('Warning !', 'The block and street and unit no must be unique !')
        return result 
    
    def write(self, cr, uid, ids, vals, context=None):
        repair_obj = self.pool.get('crea8s.repair')
        if type(ids) != type([]):
            ids = [ids]
        repair_id = repair_obj.search(cr, uid, [('cus_repair_id', 'in', ids)])
        if vals.get('name', False):
            if repair_id:
                repair_obj.write(cr, uid, repair_id, {'block': vals['name']})
        if vals.get('postal_code', False):
            if repair_id:
                repair_obj.write(cr, uid, repair_id, {'pos_code': vals['postal_code']})
        return super(res_partner_repair, self).write(cr, uid, ids, vals, context=context)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name and record.name + "\n" or ''
            if name:
                name =  '%s %s'%(name, record.unit_no and record.unit_no + "\n" or '')  
                name =  '%s %s'%(name, record.postal_code and record.postal_code + "\n" or '') 
                name =  '%s %s'%(name, record.type and record.type + "\n" or '')
            res.append((record.id, name))
        return res
    
    def get_repair_type(self, cr, uid, context):
        if context.get('is_repair', False):
            return 1
        return 0
    
    def get_warranty_type(self, cr, uid, context):
        if context.get('is_warranty', False):
            return 1
        return 0
    
    _defaults = {
        'is_serving': lambda self,cr,uid,context: self.get_repair_type(cr, uid, context),
        'is_warranty': lambda self,cr,uid,context: self.get_warranty_type(cr, uid, context),
    }
    
res_partner_repair()

class crea8s_repair(osv.osv):
    _inherit = "crea8s.repair"
    
    def onchange_partner(self, cr, uid, ids, partner_id):
        value = {}
        res_partner_obj = self.pool.get('res.partner.repair')
        if partner_id:
            res_br = res_partner_obj.browse(cr, uid, partner_id)
            value = {'block': res_br.name and res_br.name or '',
                     'pos_code': res_br.postal_code and res_br.postal_code or '',
                     'telephone1': res_br.telephone1 and res_br.telephone1 or '',
                     'telephone2': res_br.telephone2 and res_br.telephone2 or '',
                     'telephone3': res_br.telephone3 and res_br.telephone3 or '',
                     'unit_no': res_br.unit_no and res_br.unit_no or '',}
        else:
            value = {'block': '',
                     'pos_code': '',
                     'telephone1': '',
                     'telephone2': '',
                     'telephone3': '',
                     'unit_no': '',}
        return {'value': value}
    
crea8s_repair()

class crea8s_warranty(osv.osv):
    _inherit = "crea8s.warranty"
    
    def onchange_partner(self, cr, uid, ids, partner_id):
        value = {}
        res_partner_obj = self.pool.get('res.partner.repair')
        if partner_id:
            res_br = res_partner_obj.browse(cr, uid, partner_id)
            value = {'block': res_br.name and res_br.name or '',
                     'pos_code': res_br.postal_code and res_br.postal_code or '',
                     'telephone': res_br.telephone1 and res_br.telephone1 or '',
                     'telephone2': res_br.telephone2 and res_br.telephone2 or '',
                     'unit_no': res_br.unit_no and res_br.unit_no or '',}
        else:
            value = {'block': '',
                     'pos_code': '',
                     'telephone': '',
                     'telephone2': '',
                     'unit_no': '',}
        return {'value': value}
    
crea8s_warranty()