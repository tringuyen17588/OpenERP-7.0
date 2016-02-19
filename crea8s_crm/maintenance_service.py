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


class crea8s_maintenance_service(osv.osv):
    _name = "crea8s.maintenance.service"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Maintenance Services'

    def create(self, cr, uid, vals, context=None):
        if not 'name' in vals or not vals['name']:
            vals.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'crea8s.maintenance.service')})
        return super(crea8s_maintenance_service, self).create(cr, uid, vals, context)

    def compute_total(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        result = 0
        res = {}
        for x in self.browse(cr, uid, ids):
            for record in x.line_ids:
                result += record.total
            res[x.id] = result
        return res
    
    def compute_gst(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        result = 0
        res = {}
        for x in self.browse(cr, uid, ids):
            for record in x.line_ids:
                result += record.total
            res[x.id] = result * 7 / 100
        return res

    def compute_totalall(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        res = {}
        for record in self.browse(cr, uid, ids):
            res[record.id] = record.total + record.gst
        return res

    _columns = {
        'claim_id': fields.many2one('crm.claim', 'Claim'),
        'name': fields.char('Service No', size=128),
        'cus_name': fields.char('Name', size=256),
        'designation': fields.char('Designation', size=128),
        'contact_person': fields.text('Contact Person'),
        'service_done': fields.text('Service Done'),
        'part_use': fields.text('Parts Used'),
        'date': fields.datetime('Date'),
        'res_partner': fields.many2one('res.partner', 'Partner'),
        'clearing': fields.boolean('Clearing Of Virus'),
        'hard_df': fields.boolean('Hard Disk Failure'),
        'soft_s': fields.boolean('Software Support'),
        'general_serving': fields.boolean('General Servicing'),
        'train': fields.boolean('Training'),
        'other': fields.boolean('Others'),
        'name_engineer': fields.char('Name Of Engineer', size=256),
        'time_arr': fields.datetime('Time Arrived'),
        'time_depart': fields.datetime('Time Departed'),
        'date_call': fields.date('Date of Call'),
        'contract': fields.boolean('Contract'),
        'warranty': fields.boolean('Warranty'),
        'chargeable': fields.boolean('Chargeable'),
        'others': fields.boolean('Others'),
        'case_close': fields.boolean('Case Closed'),
        'case_nclose': fields.boolean('Case not closed, must return'),
        'place_return': fields.char('Place Return', size=256),
        'new_type': fields.char('Others Type', size=256),
        'line_ids': fields.one2many('crea8s.maintenance.service.line', 'maintenance_id', 'Maintenance Line'),
        'total': fields.function(compute_total, digits_compute=dp.get_precision('Account'), string='Total'),
        'gst': fields.function(compute_gst, digits_compute=dp.get_precision('Account'), string='Add GST'),
        'grand_total': fields.function(compute_totalall, digits_compute=dp.get_precision('Account'), string='Grand Total'),
    }
crea8s_maintenance_service()

class crea8s_maintenance_service_line(osv.osv):
    _name = "crea8s.maintenance.service.line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Maintenance Services Line'

    _columns = {
        'name': fields.char('Name', size=256),
        'product_id': fields.many2one('product.product', 'Product'),
        'maintenance_id': fields.many2one('crea8s.maintenance.service', 'Maintenance'),
        'brand': fields.char('Brand', size=256),
        'model': fields.char('Model', size=256),
        'serial': fields.char('Serial No', size=256),
        'qty': fields.float('qty', digits=(16, 2)),
        'unit_price': fields.float('Unit Price', digits=(16, 2)),
        'part_change': fields.char('Parts Used / Time Charge', size=256),
        'total': fields.float('Total', digits=(16, 2)),        
    }
    
    def onchange_qty_up(self, cr, uid, ids, up, qty):
        if up and qty:
            return {'value': {'total': up * qty}}
        return {'value': {'total': 0}}
    
crea8s_maintenance_service_line()

class crea8s_post_sale_system(osv.osv):
    _name = "crea8s.post.sale.system"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Post Sale System Support'

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale order'),
        'name': fields.char('Number', size=128),
        'date': fields.date('Date'),
        'contact_person': fields.char('Contact Person', size=256),
        'delivery_date': fields.date('Delivery Date'),
        'deli_am': fields.boolean('am'),
        'deli_pm': fields.boolean('pm'),
        'install_date': fields.date('Installation Date'),
        'instal_am': fields.boolean('am'),
        'instal_pm': fields.boolean('pm'),
        'instal': fields.boolean('Installation'),
        'instal_con': fields.boolean('Installation Continuation'),
        'training': fields.boolean('Training'),
        'trouble_con': fields.boolean('Troubleshooting / Configuration'),
        'other': fields.boolean('Others (please specify)'),
        'other_def': fields.char('Others'),
        'num_com': fields.float('Number of Computer', digits=(16, 2)),
        'mac_os': fields.boolean('Mac'),
        'mac_info': fields.char('Mac Info'),
        'win_2000': fields.boolean('Windows 2000 / XP'),
        'win7_32': fields.boolean('Windows 7 (32 bit)'),
        'win7_64': fields.boolean('Windows 7 (64 bit)'),
        'win_vista_32': fields.boolean('Windows Vista (32 bit)'),
        'win_vista_64': fields.boolean('Windows Vista (64 bit)'),
        'scan_server': fields.boolean('Scan to Server'),
        'scan_email': fields.boolean('Scan to Email'),
        'au_on': fields.boolean('On'),
        'au_off': fields.boolean('Off'),
        'hard_cp': fields.boolean('Hard Copy'),
        'email': fields.boolean('Email'),
        'smb': fields.boolean('SMB'),
        'mail_box': fields.boolean('Mailbox'),
        'docuwork': fields.boolean('Docuworks'),
        'network': fields.boolean('Network Set up / Router / Switch'),
        'net_point': fields.boolean('Network Point'),
        'fax_point': fields.boolean('Fax Point'),
        'cap_str': fields.boolean('Straight'),
        'cap_cross': fields.boolean('Cross'),
        'extra_length': fields.float('Extra length needed', digits=(16, 2)),
        'cus_name': fields.char('Name', size=256),
        'designation': fields.char('Designation', size=256),
#    For Authorised
        'ab_delivery_date': fields.date('Delivery Date'),
        'ab_deli_am': fields.boolean('am'),
        'ab_deli_pm': fields.boolean('pm'),
        'ab_install_date': fields.date('Installation Date'),
        'ab_instal_am': fields.boolean('AM (9am - 12noon)'),
        'ab_instal_pm': fields.boolean('PM (2:30pm - 5:00pm)'),
        'ab_instal_am911': fields.boolean('9:00am - 11:00am'),
        'ab_instal_am111': fields.boolean('11:00am - 1:00pm'),
        'ab_instal_am13': fields.boolean('1:00pm - 3:00pm'),
        'ab_instal_am35': fields.boolean('3:00am - 5:00pm'),
        'if_kit': fields.boolean('iFax Kit'),
        'u_kit': fields.boolean('USB Kit'),
        'ps_kit': fields.boolean('Postscript Kit'),
        'firm_up_y': fields.boolean('Yes'),
        'firm_up_n': fields.boolean('No'),
        'res_partner': fields.many2one('res.partner', 'Partner'),
        'sale_man': fields.many2one('res.users', 'Sale Person'),
#    For product information
        'line_ids': fields.one2many('crea8s.post.sale.system.line', 'parent_id', 'Lines'),
    }
    
    def get_ref_name(self, cr, uid, context={}):
        sale_obj = self.pool.get('sale.order')
        if context.get('default_sale_id', False):
            temp = sale_obj.browse(cr, uid, context['default_sale_id']).name
            temp = 'PSSR-' + temp
        else:
            temp = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.post.sale.system')
        return temp
    
    def get_line(self, cr, uid, context={}):
        sale_obj = self.pool.get('sale.order')
        temp = []
        if context.get('default_sale_id', False):
            for line in sale_obj.browse(cr, uid, context['default_sale_id']).order_line:
                temp.append({'product_id': line.product_id and line.product_id.id or 0,
                             'name': line.product_id and line.product_id.name or '',})
        return temp
    
    _defaults = {
        'name': lambda self, cr, uid, c: self.get_ref_name(cr, uid, c),
        'line_ids': lambda self, cr, uid, c: self.get_line(cr, uid, c), 
    }
    
crea8s_post_sale_system()

class crea8s_post_sale_system_line(osv.osv):
    _name = "crea8s.post.sale.system.line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Post Sale System Support Line'

    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'name': fields.char('Machine Model', size=256),
        'serial': fields.char('Serial No', size=256),
        'parent_id': fields.many2one('crea8s.post.sale.system', 'Parent'),
    }
    
    def onchange_product_id(self, cr, uid, ids, prod_id):
        result = {}
        product_obj = self.pool.get('product.product')
        if prod_id:
            result = {'name': product_obj.browse(cr, uid, prod_id).name}
        return {'value': result}
        
crea8s_post_sale_system_line()

class crea8s_service_agreement(osv.osv):
    _name = "crea8s.service.agreement"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Service Agreement'

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale order'),
        'name': fields.char('Agreement No', size=256),
        'ref': fields.char('Reference', size=256),
        'customer_bill_id': fields.many2one('res.partner', '''Customer's Billing Address'''),
        'customer_install_id': fields.many2one('res.partner', '''Customer's Address For Installation'''),
        'ser_date': fields.date('Service Commencement Date'),
        'mini_equip': fields.float('Equipment Minimum Period'),
        'main_charge': fields.float('Maintenance Charge'),
        'comited_copy1': fields.char('Committed Number of Copies', 256),
        'comited_copy2': fields.char('Committed Number of Copies 2', 256),
        'price_copy': fields.float('Price Per Copy'),
        'mini_soft': fields.float('Software Minimum Period'),
        'year_charge_soft': fields.float('Yearly Software Maintenance Charge'),
        'remark': fields.text('Remark'),
        'date': fields.date('Date'),
        'line_ids': fields.one2many('crea8s.service.agreement.line', 'parent_id', 'Service Agreement Line'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
    }
    
    def get_ref_name(self, cr, uid, context={}):
        sale_obj = self.pool.get('sale.order')
        if context.get('default_sale_id', False):
            temp = sale_obj.browse(cr, uid, context['default_sale_id']).name
            temp = 'SRVAGR-' + temp
        else:
            temp = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.service.agreement')
        return temp

    def get_line(self, cr, uid, context={}):
        sale_obj = self.pool.get('sale.order')
        temp = []
        if context.get('default_sale_id', False):
            for line in sale_obj.browse(cr, uid, context['default_sale_id']).order_line:
                temp.append({'product_id': line.product_id and line.product_id.id or 0,
                             'name': line.product_id and line.product_id.name or '',})
        return temp
    
    _defaults = {
        'currency_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id, 
        'name': lambda self, cr, uid, c: self.get_ref_name(cr, uid, c),
        'line_ids': lambda self, cr, uid, c: self.get_line(cr, uid, c), 
    }

crea8s_service_agreement()

class crea8s_service_agreement_line(osv.osv):
    _name = "crea8s.service.agreement.line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Service Agreement Line'

    _columns = {
        'name': fields.char('Name', size=256),
        'product_id': fields.many2one('product.product', 'Product'),
        'Serial': fields.char('Serial Number'),
        'type': fields.selection([('e_fxs', 'Equipment FXS'), ('e_nfxs', 'Equipment non-FXS'), ('s_fxs', 'Software FXS'), ('s_nfxs', 'Software non-FXS')], 'type'),
        'parent_id': fields.many2one('crea8s.service.agreement', 'Parent'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id):
        result = ''
        product_obj = self.pool.get('product.product')
        if product_id:
            return {'value': {'name': product_obj.browse(cr, uid, product_id).name}}
        return {'value': {'total': 0}}

    _defaults = {
        'type': 'e_fxs',
    }
crea8s_service_agreement_line()

class crea8s_sale_agreement(osv.osv):
    _name = "crea8s.sale.agreement"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Sale Agreement'

    _columns = {
        'sale_id': fields.many2one('sale.order', 'Sale order'),
        'name': fields.char('Sale Agreement No', size=256),
        'date': fields.date('Day of'),
        'ref': fields.char('Reference', size=256),
        'partner_id': fields.many2one('res.partner', 'Company Name'),
        'contact_person': fields.char('Contact Person', 256),
        'designation': fields.char('Designation'),
        'spec_instruction': fields.text('Special Instruction'),
        'rent_lc': fields.selection([('Rental','Rental'),('Leasing','Leasing'),('Cash','Cash')],'Type'),
        'deposit_down': fields.float('Deposit / Downpayment'),
        'monthly_payment': fields.float('Monthly Payment'),
        'term': fields.char('Term', 256),
        'final_payment': fields.float('Final Payment'),
        'bw_copy_charge': fields.float('B & W Copy Charge'),
        'color_copy_charge': fields.float('Colour Copy Charge'),
        'sale_consultant': fields.char('Sale Consultant', 256),
        'amount_receive': fields.float('Amount Received'),
        'cash_cheque_num': fields.char('Cash / Cheque Number', 256),
        'line_ids': fields.one2many('crea8s.sale.agreement.line', 'parent_id', 'Service Agreement Line'),
        'currency_id': fields.many2one('res.currency', 'Currency'),
    }
    
    def get_ref_name(self, cr, uid, context={}):
        sale_obj = self.pool.get('sale.order')
        if context.get('default_sale_id', False):
            temp = sale_obj.browse(cr, uid, context['default_sale_id']).name
            temp = 'SAGR-' + temp
        else:
            temp = self.pool.get('ir.sequence').get(cr, uid, 'crea8s.sale.agreement')
        return temp
    
    def get_line(self, cr, uid, context={}):
        sale_obj = self.pool.get('sale.order')
        temp = []
        if context.get('default_sale_id', False):
            for line in sale_obj.browse(cr, uid, context['default_sale_id']).order_line:
                temp.append({'product_id': line.product_id and line.product_id.id or 0,
                             'name': line.product_uom_qty and str(line.product_uom_qty) or '',
                             'total': line.price_unit and line.price_unit or 0})
        return temp
    
    _defaults = {
        'currency_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id, 
        'name': lambda self, cr, uid, c: self.get_ref_name(cr, uid, c),
        'line_ids': lambda self, cr, uid, c: self.get_line(cr, uid, c),
    }
        
crea8s_sale_agreement()

class crea8s_sale_agreement_line(osv.osv):
    _name = "crea8s.sale.agreement.line"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Sale Agreement Line'

    _columns = {
        'name': fields.char('Item', size=256),
        'product_id': fields.many2one('product.product', 'Product'),
        'total': fields.float('Total Contractual Price', digits=(16, 2)),
        'parent_id': fields.many2one('crea8s.sale.agreement', 'Parent'),
    }
crea8s_sale_agreement_line()

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _get_sale_agrment(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        sale_agr_obj = self.pool.get('crea8s.sale.agreement')
        sale_id = 0
        for rec in self.browse(cr, uid, ids, context=context):
            sale_id = sale_agr_obj.search(cr, uid, [('sale_id', '=', rec.id)])
            sale_id = sale_id and sale_id[0] or 0
            result[rec.id] = sale_id
        return result
    
    def _get_service_agrment(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        sale_agr_obj = self.pool.get('crea8s.service.agreement')
        sale_id = 0
        for rec in self.browse(cr, uid, ids, context=context):
            sale_id = sale_agr_obj.search(cr, uid, [('sale_id', '=', rec.id)])
            sale_id = sale_id and sale_id[0] or 0
            result[rec.id] = sale_id
        return result
    
    def _get_post_sale_sys(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        sale_agr_obj = self.pool.get('crea8s.post.sale.system')
        sale_id = 0
        for rec in self.browse(cr, uid, ids, context=context):
            sale_id = sale_agr_obj.search(cr, uid, [('sale_id', '=', rec.id)])
            sale_id = sale_id and sale_id[0] or 0
            result[rec.id] = sale_id
        return result
    
    def action_view_sale_agr1(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.sale_agr_id
            sale_agr_id = sale_agr_id and sale_agr_id.id or 0
        return {'name': 'Sale Agreement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.sale.agreement',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
    
    def action_view_sale_agr2(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.sale_agr_id
            sale_agr_id = sale_agr_id and sale_agr_id.id or 0
        return {'name': 'Sale Agreement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.sale.agreement',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
    
    def action_view_post_sale1(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.post_sale_sys_id
            sale_agr_id = sale_agr_id and sale_agr_id.id or 0
        return {'name': 'Post Sale System Support',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.post.sale.system',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
        
    def action_view_post_sale2(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.post_sale_sys_id
            sale_agr_id = sale_agr_id and sale_agr_id.id or 0
        return {'name': 'Post Sale System Support',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.post.sale.system',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
        
    def action_view_serv_agr1(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.service_agr_id
            sale_agr_id = sale_agr_id and sale_agr_id.id or 0
        return {'name': 'Service Agreement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.service.agreement',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
    
    def action_view_serv_agr2(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.service_agr_id
            sale_agr_id = sale_agr_id and sale_agr_id.id or 0
        return {'name': 'Service Agreement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.service.agreement',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
    
    _columns = {
        'sale_agr_id': fields.function(_get_sale_agrment, type='many2one', relation='crea8s.sale.agreement', string='Sale Agreement'),
        'service_agr_id': fields.function(_get_service_agrment, type='many2one', relation='crea8s.service.agreement', string='Service Agreement'),
        'post_sale_sys_id': fields.function(_get_post_sale_sys, type='many2one', relation='crea8s.post.sale.system', string='Post Sale System Support'),
    }
    
    def get_serial_number(self, cr, uid, ids, context):
        result  = []
        lot_ids = []
        lot_obj = self.pool.get('stock.production.lot')
        for x in self.browse(cr, uid, ids):
            for y in x.order_line:
                result.append(y.product_id and y.product_id.id or -1)
                lot_ids = lot_obj.search(cr, uid, [('product_id', 'in', result),
                                                   ('stock_available', '>', 10)])
        return {'name': 'Product Serial Number',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'stock.production.lot',
            'type': 'ir.actions.act_window',
            'res_id': lot_ids,
            'domain': "[('id', '=', %s)]"%str(lot_ids),
            'target': 'current',
            'nodestroy' : True,}
        
    def kiemtra_chaytudong(self, cr, uid, ids):
        
        return 1
sale_order()

class crm_claim(osv.osv):
    _inherit = "crm.claim"
    
    def _get_main_srv(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        sale_agr_obj = self.pool.get('crea8s.maintenance.service')
        sale_id = 0
        for rec in self.browse(cr, uid, ids, context=context):
            sale_id = sale_agr_obj.search(cr, uid, [('claim_id', '=', rec.id)])
            sale_id = sale_id and sale_id[0] or 0
            result[rec.id] = sale_id        
        return result
    
    def view_maintenance_serv(self, cr, uid, ids, context=None):
        sale_agr_id = 0
        result = {}
        for record in self.browse(cr, uid, ids):
            sale_agr_id = record.maintenance_id and record.maintenance_id.id or 0
        return {'name': 'Maintenance Service',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'crea8s.maintenance.service',
            'type': 'ir.actions.act_window',
            'res_id': sale_agr_id,
            'domain': "[('id', '=', %s)]"%str(sale_agr_id),
            'target': 'current',
            'nodestroy' : True,
        }
    
    _columns = {
        'maintenance_id': fields.function(_get_main_srv, type='many2one', relation='crea8s.maintenance.service', string='Maintenance Service'),
    }
    
crm_claim()