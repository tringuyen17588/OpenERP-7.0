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

from openerp.addons.base_status.base_state import base_state
from openerp.addons.base_status.base_stage import base_stage
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import datetime
from datetime import timedelta

class pos_order(osv.osv):
    _inherit = "pos.order"
    _order = "order_date desc, date_order desc"
    strFormatTime = '%Y-%m-%d %H:%M:%S'
    strFormatTimeAMPM = '%Y-%m-%d %H:%M:%S %p'
    def _get_date_order(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            date_or = order.date_order
            if date_or:
                temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
                temp += timedelta(hours=8)
                res[order.id] = str(temp)[:10] or ''
            else:
                #pass
                res[order.id] = ''
            #res[order.id] = order.date_order and order.date_order[:10] or ''
        return res

    def get_hour(self, cr, uid, ids, date_or):
        result = int(date_or[11:13]) + 8
        return result
    
    def _get_shift(self, cr, uid, ids, name, args, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):

            res[order.id] = self.get_time_plus_timezone(order.session_id.start_at, self.strFormatTimeAMPM)
#	    res[order.id] = self.get_time_plus_timezone(order.type, self.strFormatTimeAMPM) 
#            hour = self.get_hour(cr, uid, ids, order.date_order)
#            hour = hour > 24 and hour - 24 or hour
#            if hour >= 7 and hour < 15:
#                res[order.id] = '7am - 3pm'
#            if hour >= 15 and hour < 23:
#                res[order.id] = '3pm - 11pm'
#            if hour >= 23 or hour < 7:
#                res[order.id] = '11pm - 7am'
#            else:
#                pass
        return res    
    
    def check_time(self, cr, uid, ids, context={}):
        for record in self.browse(cr, uid, ids):
            date_or = record.date_order
            temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
            temp += timedelta(hours=8)
            hour = self.get_hour(cr, uid, ids, record.date_order)
            #raise osv.except_osv('warmning!', hour)
            sql = '''ALTER TABLE pos_order DROP COLUMN order_date; 
                     ALTER TABLE pos_order DROP COLUMN type '''
            cr.execute(sql)
            
        return 1
    
    def fix_data(self, cr, uid, idds, context={}):
        ids1 = self.search(cr, uid, [('order_date', 'in', ['2015-01-19'])])
        for record in self.browse(cr, uid, ids1):
            date_or1 = record.type
            date_or2 = record.date_order
            temp1 = datetime.datetime(int(date_or2[:4]), int(date_or2[5:7]), int(date_or2[8:10]), int(date_or2[11:13]), int(date_or2[14:16]), int(date_or2[17:19]))
            temp1 += timedelta(hours=8)
            date_or2g = str(temp1)[:10] or ''
            print date_or1[:10], ' != ', date_or2g
            if date_or1[:10] != date_or2g:
                print  '''Update pos_order set type = '%s' where id = %s '''%(date_or1[:10],record.id)
                cr.execute(''' Update pos_order set order_date = '%s' where id = %s '''%(date_or1[:10],record.id))
                #self.write(cr, uid, [record.id], {'order_date': date_or1})
        return 1
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_paid': 0.0,
                'amount_return':0.0,
                'amount_tax':0.0,
            }
            val1 = val2 = 0.0
            cur = order.pricelist_id.currency_id
            for payment in order.statement_ids:
                res[order.id]['amount_paid'] +=  payment.amount
                res[order.id]['amount_return'] += (payment.amount < 0 and payment.amount or 0)
            for line in order.lines:
                val1 += line.price_subtotal_incl
                val2 += line.price_subtotal
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val1-val2)
            res[order.id]['amount_total'] = cur_obj.round(cr, uid, cur, val1)
        return res
    
    _columns = {
        'type': fields.function(_get_shift, string='shift', type='char', store=True),
        'amount_total': fields.function(_amount_all, string='Total', multi='all', store={
                'pos.order': (lambda self, cr, uid, ids, c={}: ids, ['lines'], 20)}),
        'order_date': fields.function(_get_date_order, string="Order Date", type='char', store={'pos.order': (lambda self, cr, uid, ids, c={}: ids, ['date_order'], 20)}),
    }

    def get_time_plus_timezone(self, date_or, strTimeFormatOutput):
        """
            get_time_plus_timezone, default plus 8 hours.
            :param date_or: string, format '2014-11-05 03:12:58' 
            :param strTimeFormatOutput: string, output time-format  
        """
        if date_or:
            temp = datetime.datetime(int(date_or[:4]), int(date_or[5:7]), int(date_or[8:10]), int(date_or[11:13]), int(date_or[14:16]), int(date_or[17:19]))
            temp += timedelta(hours=8)
            return time.strftime(strTimeFormatOutput, time.strptime(str(temp), self.strFormatTime))
        return ''
pos_order()

