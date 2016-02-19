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

import time
from openerp.report import report_sxw
from openerp import pooler
from openerp.osv import fields, osv

def titlize(journal_name):
    words = journal_name.split()
    while words.pop() != 'journal':
        continue
    return ' '.join(words)

class pos_order_reprint(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(pos_order_reprint, self).__init__(cr, uid, name, context=context)

        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        partner = user.company_id.partner_id

        self.localcontext.update({
            'time': time,
            'disc': self.discount,
            'net': self.netamount,
            'get_journal_amt': self._get_journal_amt,
            'get_subtotal': self.get_subtotal,
            'address': partner or False,
            'titlize': titlize
        })

    def netamount(self, order_line_id):
        sql = 'select (qty*price_unit) as net_price from pos_order_line where id = %s'
        self.cr.execute(sql, (order_line_id,))
        res = self.cr.fetchone()
        return res[0]
    
    def get_subtotal(self, order_id):
        sql = 'select (qty*price_unit) as net_price from pos_order_line where order_id = %s'
        self.cr.execute(sql, (order_id,))
        res = self.cr.fetchall()
        return sum([x[0] for x in res])

    def discount(self, order_id):
        sql = 'select discount, price_unit, qty from pos_order_line where order_id = %s '
        self.cr.execute(sql, (order_id,))
        res = self.cr.fetchall()
        dsum = 0
        for line in res:
            if line[0] != 0:
                dsum = dsum +(line[2] * (line[0]*line[1]/100))
        return dsum

    def _get_journal_amt(self, order_id):
        data={}
        sql = """ select aj.name,absl.amount as amt from account_bank_statement as abs
                        LEFT JOIN account_bank_statement_line as absl ON abs.id = absl.statement_id
                        LEFT JOIN account_journal as aj ON aj.id = abs.journal_id
                        WHERE absl.pos_statement_id =%d"""%(order_id)
        self.cr.execute(sql)
        data = self.cr.dictfetchall()
        data_rs = []
        temp = {}
        for xx in data:
            if xx['amt'] < 0:
                xx['name'] = 'Change'
                xx['amt'] = abs(xx['amt'])
                temp = xx
            else:
                data_rs.append(xx)
        data_rs.append(temp)
        
        return data_rs

report_sxw.report_sxw('report.pos.receipt.reprint', 'pos.order', 'addons/crea8s_pos_reprint/report/pos_receipt.rml', parser=pos_order_reprint, header=False)

class pos_receipt(osv.osv_memory):
    _inherit = 'pos.receipt'
    _description = 'Point of sale receipt'

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'pos.receipt.reprint',
            'datas': datas,
        }

pos_receipt()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
