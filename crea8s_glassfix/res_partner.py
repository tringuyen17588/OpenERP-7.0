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

from openerp.osv import fields,osv
from openerp.tools.translate import _

class res_brand_no(osv.osv):
    _name = 'res.brand.no'
    
    _columns = {
        'name': fields.char('Name', size=128),
        'code': fields.char('Code', size=32),
    }
res_brand_no()

class crea8s_res_number(osv.osv):
    _name = 'crea8s.res.number'
    _columns = {
        'name': fields.char('Name', size=128),
    }
crea8s_res_number()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _order = "create_date desc"

    def get_payment_cus(self, cr, uid, ids, field_name, arg, context=None):
        acc_vc  = self.pool.get('account.voucher')
        inv_obj = self.pool.get('account.invoice')
        jn_obj = self.pool.get("account.journal")
        res = {}
        try:
            for partner in self.browse(cr, uid, ids, context):
                result = ''
                vc_ids = acc_vc.search(cr, uid, [('vehicle', '=', partner.id)])
                if vc_ids:
                    inv_br = acc_vc.browse(cr, uid, vc_ids[0])
                    inv_br = inv_br.journal_id and inv_br.journal_id.name or '' 
                    result = inv_br
                else:
                    result = ''
                res[partner.id] = result
        except:
            pass
        return res

    def get_state_po(self, cr, uid, ids, field_name, arg, context=None):
        po_obj = self.pool.get('purchase.order')
        res = {}
        for record in self.browse(cr, uid, ids):
            if record.po_id:
                if record.po_id.shipped:
                    res[record.id] = 'Received Goods'
                else:
                    res[record.id] = 'Purchase Order'
            else:
                res[record.id] = ''
        return res

    _columns = {
        'invoice_no': fields.char('Invoice No.', size=128),
        'is_insurance': fields.boolean('Insurance Companies'),
        'is_carwrks': fields.boolean('Car Dealers'),
        'is_walkin': fields.boolean('Is Walk-In'),
        'is_mobile': fields.boolean('Mobile'),
        'is_drive': fields.boolean('Drive-in'),
        'con_per': fields.char('Contact Person', size=128),
        'is_he_xing': fields.boolean('He Xing'),
        'is_jae': fields.boolean('JAE'),
        'he_xing1': fields.float('He Xing 1', digits=(16,2)),
        'he_xing2': fields.float('He Xing 2', digits=(16,2)),
        'he_xing3': fields.float('He Xing 3', digits=(16,2)),
        'jae1': fields.float('JAE 1', digits=(16,2)),
        'jae2': fields.float('JAE 2', digits=(16,2)),
        'jae3': fields.float('JAE 3', digits=(16,2)),
        'is_fong_tat': fields.boolean('Fong Tat'),
        'fong_tat1': fields.float('Fong Tat 1', digits=(16,2)),
        'fong_tat2': fields.float('Fong Tat 2', digits=(16,2)),
        'fong_tat3': fields.float('Fong Tat 3', digits=(16,2)),
        'is_race_tat': fields.boolean('Race Tech'),
        'race_tat1': fields.float('Race Tech 1', digits=(16,2)),
        'race_tat2': fields.float('Race Tech 2', digits=(16,2)),
        'race_tat3': fields.float('Race Tech 2', digits=(16,2)),
        'nric': fields.char('NRIC', size=256),
        'technician': fields.many2one('hr.employee', 'Technician'),
        'dob': fields.date('DOB'),
        'wk_shop': fields.selection([('Ubi', 'Ubi'),
                                     ('Bukit Batok', 'Bukit Batok')], 'Workshop'),
        'insurance_com': fields.many2one('res.partner', 'Insurance / Workshop'),
        'solar_film': fields.selection([('yes', 'Yes'), ('no', 'No')],'Solar Film claim'),
        'po_id': fields.many2one('purchase.order', 'PO'),
        'state': fields.function(get_state_po, string='state', type='char'),
        'payment_cus': fields.function(get_payment_cus, string='Payment', type='char'),
    # For Vehicle
        'vcl_name': fields.char('Name', size=128),
        'vcl_street': fields.char('Street', size=128),
        'vcl_street2': fields.char('Street2', size=128),
        'vcl_zip': fields.char('Zip', change_default=True, size=24),
        'vcl_city': fields.char('City', size=128),
        'vcl_state_id': fields.many2one("res.country.state", 'State'),
        'vcl_country_id': fields.many2one('res.country', 'Country'),
        'vcl_country': fields.related('vcl_country_id', type='many2one', relation='res.country', string='Country',
                                  deprecated="This field will be removed as of OpenERP 7.1, use country_id instead"),
        'vcl_email': fields.char('Email', size=240),
        'vcl_phone': fields.char('Phone', size=64),
        'vcl_fax': fields.char('Fax', size=64),
        'vcl_mobile': fields.char('Mobile', size=64),
        'cus_quote': fields.char('Customer Code', size=256),
        'regis_no': fields.char('Registration No.', size=64),
        'brand_id': fields.many2one('res.brand.no', 'Brand/Model'),
        'date_report': fields.datetime('Date/Time Of Report'),
        'policy_no': fields.char('Policy No./Usage', size=64),
        'chassis_no': fields.char('Chassis No', size=128),
        'year_manufacture':fields.integer('Year of Manufacture'),
        'claim_no':fields.char('Claim No', size=64),
        'date_accident': fields.datetime('Date & Time Of Accident'),
        'check_report':fields.char('Report By/Check With', size=128),
        'place_accident':fields.char('Place & Cause of Accident', size=128),
        'rain_sensor': fields.selection([('yes', 'Yes'), ('no', 'No')],'Rain Sensor'),
        'description_crack':fields.text('Remark'),
        'image_nric': fields.binary("NRIC / Driving License"),
        'image_cer': fields.binary("Certificate Of Insurance"),
        'image_aft': fields.binary("After"),
        'image_bef': fields.binary("Before"),
        'image_sagr': fields.binary("Sales Agreement"),
        'date_repair':fields.datetime('Date Repair /Replaced'),
        'amount_cc':fields.float('Amount $'),
        'sf_claim': fields.char('SF Claim (applicable for Aviva & Chartis)', size=128),
        'incent_repair':fields.char('Incentive for repair (Cheque No.)', size=128),
        'amt': fields.float('(Brand/Glass) Amt $'),
        'is_repair': fields.boolean('Repair'),
        'is_frontws': fields.boolean('Front Windscreen'),
        'is_fdg_s': fields.boolean('Front Door Glass'),
        'is_fdg_d': fields.boolean('Front Door Glass'),
        'is_rdg_s': fields.boolean('Rear Door Glass'),
        'is_rdg_d': fields.boolean('Rear Door Glass'),
        'is_rw': fields.boolean('Rear Windscreen'),
        'is_fender_r': fields.boolean('Fender'),
        'is_fender_l': fields.boolean('Fender'),
        'is_quarter_r': fields.boolean('Quarter'),
        'is_quarter_l': fields.boolean('Quarter'),
        'post_code':fields.char('Postal Code', size=128),
        'ic_no':fields.char('I/C No', size=128),
        'occupation':fields.char('Occupation', size=128),
        'vcl_ic_no':fields.char('I/C No', size=128),
        'vcl_occupation':fields.char('Occupation', size=128),
        'no_crack': fields.many2one('crea8s.res.number','No. of Crack(s)'),
        'no_chip': fields.many2one('crea8s.res.number','No. of Chip(s)'),
        'date_appoint': fields.datetime('Appointment (Date / Time)'),
    }
    
    def get_is_company(self, cr, uid, context):
        
        if context.get('default_parent_id') != None:
            return 0
        return 1
    
    _defaults = {
        'is_company': lambda self,cr,uid,c: self.get_is_company(cr, uid, context=c),
    }

    def onchange_insurance(self, cr, uid, ids, insu_id, car_id):
        if not insu_id and not car_id:
            return {'value': {}}
        elif insu_id:
            return {'value': {'is_carwrks': False}}
        else:
            return {'value': {'is_carwrks': True}}
    
    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        result = super(res_partner, self).onchange_address(cr, uid, ids, use_parent_address, parent_id, context)
        if parent_id:
            parent = self.browse(cr, uid, parent_id, context=context)
            result['value'].update({'name': parent.name and parent.name or '',
                                    'con_per': parent.con_per and parent.con_per or '',
                                    'name': parent.name and parent.name or '',
                                    'ic_no': parent.ic_no and parent.ic_no or '',
                                    'occupation': parent.occupation and parent.occupation or '',
                                    'function': parent.function and parent.function or '',
                                    'email': parent.email and parent.email or '',
                                    'mobile': parent.mobile and parent.mobile or '',
                                    'phone': parent.phone and parent.phone or '',
                                    'title': parent.title and parent.title or '',})
        return result

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(res_partner,self).name_get(cr, uid, ids, context=context)
        for record1 in self.browse(cr, uid, ids, context=context):
            if not record1.is_company:
                name = record1.regis_no and record1.regis_no or record1.name
                for x in res:
                    if x[0] == record1.id:
                        res.remove(x) 
                res.append((record1.id, name))
        return res    

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        ids = []
        result = super(res_partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)
        if context.get('vehicle', False):
            ids = self.search(cr, uid, [('regis_no', 'like', name)])
        ids = self.search(cr, uid, [('id', 'in', ids)] + args, limit=limit, context=context)
        if ids:
            return self.name_get(cr, uid, ids, context)
        return result
    
    def onchange_car(self, cr, uid, ids, insu_id, car_id):
        if not insu_id and not car_id:
            return {'value': {}}
        elif car_id:
            return {'value': {'is_insurance': False}}
        else:
            return {'value': {'is_insurance': True}}
                
res_partner()

class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    _columns = {
        'cus_id': fields.many2one('res.partner', 'Vehicle'),
    }
    
    def get_origin(self, cr, uid, context={}):
        result = ''
        partner_obj = self.pool.get('res.partner')
        if context.get('cus_id', False):
            result = partner_obj.browse(cr, uid, context['cus_id']).regis_no
        return result

    def create(self, cr, uid, vals, context={}):
        partner_obj = self.pool.get('res.partner')
        if context.get('cus_id', False):
            vals.update({'cus_id': context['cus_id']})
            order =  super(purchase_order, self).create(cr, uid, vals, context)
            partner_obj.write(cr, uid, [context['cus_id']], {'po_id' : order})
        else:
            order =  super(purchase_order, self).create(cr, uid, vals, context)
        return order

    _defaults = {
        'origin': get_origin,
    }
    
purchase_order()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'vehicle': fields.many2one('res.partner', 'Vehicle'),
    }
    
    def get_vehicle(self, cr, uid, context):
        if context.get('vehicle', False):
            return context['vehicle']
        return 0
    
    _defaults = {
        'vehicle': get_vehicle, 
    }
    
account_voucher()

class invoice(osv.osv):
    _inherit = 'account.invoice'

    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'vehicle': inv.vehicle and inv.vehicle.id or 0,
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }

invoice()