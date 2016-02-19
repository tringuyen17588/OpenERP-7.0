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

class crm_lead(osv.Model):
    _inherit = "crm.lead"
    
    _columns = {
        'ltype': fields.selection([('Selling','Selling'), 
                                   ('Leasing', 'Leasing'),
                                   ('Rental', 'Rental')], 'Type'),
    }
    
crm_lead()

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    _columns = {
        'ltype': fields.selection([('Selling','Selling'), 
                                   ('Leasing', 'Leasing'),
                                   ('Rental', 'Rental')], 'Type'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        'date_inv': fields.date('Date Invoice'),
        'inter_unit': fields.selection([('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months'), ('years', 'Years')], 'Interval Unit'),
        'number_time': fields.integer('Number'),
        'schedule_inv': fields.many2one('ir.cron', 'Schedule Invoices'),
    }
    
    def convert_date(self, str_date):
        result = 0
        if str_date:
            result = datetime.date(int(str_date[:4]),int(str_date[5:7]),int(str_date[8:10]))
        return result
    
    def date_compute_rental(self, cr, uid, ids, date_from, date_to, time_type):
        date_from = self.convert_date(date_from)
        date_to = self.convert_date(date_to)
        btwen = date_to - date_from
        if time_type == 'days' and date_from and date_to:
            btwen = btwen.days
        elif time_type == 'months' and date_from and date_to:
            btwen = date_to.month - date_from.month + (date_to.year - date_from.year) * 12
        return {'value': {'number_time': btwen}}
    
    def auto_gene_inv(self, cr, uid, order_id):
        order = self.browse(cr, uid, order_id)
        line = [x.id for x in order.order_line]
        return self.action_button_confirm(cr, uid, [order_id])
    
    def copy_invoice(self, cr, uid, sale_id, invoice_id):
        invoice_obj = self.pool.get('account.invoice')
        sale_obj = self.pool.get('sale.order')
        record = sale_obj.browse(cr, uid, sale_id) 
        if len(record.invoice_ids) < record.number_time:
            invoice_id = invoice_obj.copy(cr, uid, invoice_id, {'date_due': self.convert_date(record.date_inv) + timedelta(month=len(record.invoice_ids))})
            cr.execute('Insert into sale_order_invoice_rel values(%s,%s)'%(str(sale_id),str(invoice_id)))
        return invoice_id
        
    def create_auto_inv(self, cr, uid, ids, context={}):
        schedule_obj = self.pool.get('ir.cron')
        schedule_inv = 0
        for record in self.browse(cr, uid, ids):
            lines = [x.id for x in record.order_line]
            schedule_inv = schedule_obj.create(cr, uid, {'name': 'Schedule for ' + record.name,
                                          'user_id': 1,
                                          'active': 1,
                                          'model': 'sale.order',
                                          'function': 'auto_gene_inv',
                                          'args':'(%s,%s,)'%(str(ids[0]),str(record.invoice_ids[0])),
                                          'numbercall': record.number_time,
                                          'interval_time':'minutes',
                                          'interval_number':1})
        self.write(cr, uid, ids, {'schedule_inv': schedule_inv})
        return 1
    
sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': line.order_id.number_time and pu / line.order_id.number_time or pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }
        return res
    
sale_order_line()

class crm_make_sale(osv.osv_memory):
    _inherit = "crm.make.sale"
    def makeOrder(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.date.context_today(self,cr,uid,context=context),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                }
                ##################################
                if case.ltype == 'Rental':
                    #    For Rental -> crea8s.rental
                    vals.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'crea8s.rental') or '/',
                                 'ltype': case.ltype and case.ltype or ''})
                elif case.ltype == 'Leasing':
                    #    For Leasing -> crea8s.leasing
                    vals.update({'name': self.pool.get('ir.sequence').get(cr, uid, 'crea8s.leasing') or '/',
                                 'ltype': case.ltype and case.ltype or ''})
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_close(cr, uid, data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value
crm_make_sale()