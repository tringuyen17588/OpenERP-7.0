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
from openerp.osv import fields, osv
from openerp.report import report_sxw


class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    def invoice_print(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'crea8s.account.invoice.fix',
            'datas': datas,
            'nodestroy' : True
    }
account_invoice()

class crea8s_account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw(
    'report.crea8s.account.invoice.fix',
    'account.invoice',
    'addons/crea8s_invoice_report/account_print_invoice.rml',
    parser=crea8s_account_invoice
)