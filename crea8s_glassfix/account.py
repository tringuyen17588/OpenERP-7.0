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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import SUPERUSER_ID
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class account_tax(osv.osv):
    _inherit = "account.tax"
    
    def _compute(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        if not precision:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        res = self._unit_compute(cr, uid, taxes, price_unit, product, partner, quantity)
        total = 0.0
        for r in res:
            if r.get('balance',False):
                r['amount'] = round(r.get('balance', 0.0) * quantity,4) - total
            else:
                r['amount'] = round(r.get('amount', 0.0) * quantity,4)
                total += r['amount']
        return res

    def compute_inv(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.
        Price Unit is a Tax included price

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        if not precision:
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        res = self._unit_compute_inv(cr, uid, taxes, price_unit, product, partner=None)
        total = 0.0
        for r in res:
            if r.get('balance',False):
                r['amount'] = round(r['balance'] * quantity,4) - total
            else:
                r['amount'] = round(r['amount'] * quantity,4)
                total += r['amount']
        return res

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0
            }
            for line in invoice.invoice_line:
                res[invoice.id]['amount_untaxed'] += rounding(line.price_subtotal)
            for line in invoice.tax_line:
                res[invoice.id]['amount_tax'] += rounding(line.amount)
            res[invoice.id]['amount_total'] = rounding(res[invoice.id]['amount_tax']) + rounding(res[invoice.id]['amount_untaxed'])
        return res
    def invoice_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        self.button_reset_taxes(cr, uid, ids, context)
        return True
    _columns = {
        'delivery_id': fields.char('Delivery to', size=128, readonly=True, states={'draft':[('readonly',False)]}),
        'po_no': fields.char('P/0 No.', size=128, readonly=True, states={'draft':[('readonly',False)]}),
        'vehicle': fields.many2one('res.partner', 'Vehicle No', readonly=True, states={'draft':[('readonly',False)]}),
        'term': fields.text('term', readonly=True, states={'draft':[('readonly',False)]}),
        'is_vehicle': fields.boolean('Is Vehicle'),
        'shop_id': fields.many2one('res.partner', 'Shop'),
        'vehicle_no': fields.related('vehicle', 'regis_no', type='char', string='Vehicle No'),
    }
    
    _defaults = {
        'is_vehicle': False,
    }

account_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
