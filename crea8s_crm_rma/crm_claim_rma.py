# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2013 Camptocamp
#    Copyright 2009-2013 Akretion,
#    Author: Emmanuel Samyn, Raphaël Valyi, Sébastien Beau,
#            Benoît Guillot, Joel Grand-Guillaume
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

from openerp.osv import fields, orm, osv
from datetime import datetime
from dateutil.relativedelta import relativedelta

class account_invoice_claim(osv.osv_memory):
    _name = 'account.invoice.claim'

    _columns = {
        'name': fields.many2one('account.invoice', 'Invoice'),
        'inv_line':fields.many2many('account.invoice.line', 'invoice_claim_ref', 'invclaim_id', 'invline_id', 'Line'),
    }

    def get_invoice(self,cr,uid,context={}):
        if context.get('active_id'):
            return context['active_id']
        return 0

    _defaults = {
        'name': get_invoice,
    }

    def action_view_po(self, cr, uid, ids, context=None):
        context = {}
        claim_obj = self.pool.get('crm.claim')
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        lst_claim = []
        for record1 in self.browse(cr, uid, ids):
            record = invoice_obj.browse(cr, uid, record1.name.id)
            lst_claim = claim_obj.search(cr, uid, [('invoice_id', 'in', ids)])
            print record 
            if not lst_claim:
                claim_id = claim_obj.create(cr, uid, {
                    'name': 'Issue for Invoice %s'%record.number and record.number or '',
                    'claim_type': record.type == 'in_invoice' and 'supplier' or 'customer',
                    'date': datetime.now(),
                    'warehouse_id':claim_obj._get_default_warehouse(cr, uid,context),
                    'partner_id': record.partner_id and record.partner_id.id or 0,
                    'delivery_address_id': record.partner_id and record.partner_id.id or 0,
                    'invoice_id': record.id,
                })
                lst_claim.append(claim_id)
                claim_line_obj = self.pool.get('claim.line')
                warehouse_id = claim_obj._get_default_warehouse(cr, uid,context)
                for invoice_line in invoice_line_obj.browse(cr, uid, [x.id for x in record1.inv_line]):
                    print invoice_line
                    location_dest_id = claim_line_obj.get_destination_location(
                        cr, uid, invoice_line.product_id.id,
                        warehouse_id, context)
                    claim_line_obj.create(cr, uid, {
                        'name': invoice_line.name,
                        'claim_origine': "none",
                        'invoice_line_id': invoice_line.id,
                        'product_id': invoice_line.product_id.id,
                        'brand_id': invoice_line.brand_id.id,
                        'product_returned_quantity': invoice_line.quantity,
                        'unit_sale_price': invoice_line.price_unit,
                        'location_dest_id': location_dest_id,
                        'warranty_return_partner': record.partner_id and record.partner_id.id or 0,
                        'state': 'draft',
                        'claim_id':claim_id,
                        'warning': 'valid',
                    })
        return {
        'view_type':'form',
        'view_mode':'tree,form',
        'res_model':'crm.claim',
        'view_id':False,
        'type':'ir.actions.act_window',
        'domain':[('id', 'in', lst_claim)],
        'context':{},
      }

account_invoice_claim()