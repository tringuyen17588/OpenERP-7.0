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

class report_invoice_noqty(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(report_invoice_noqty, self).__init__(cr, uid, name, context=context)
        self.number = 0
        self.localcontext.update({
            'time': time,
            'get_number': self.get_number,
        })
    
    def get_number(self):
        self.number += 1
        return self.number

report_sxw.report_sxw('report.account.invoice.noqty', 'account.invoice', 'addons/crea8s_glassfix/report/account_invoice_noqty.rml', parser=report_invoice_noqty)

class account_invoice_fixed(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_invoice_fixed, self).__init__(cr, uid, name, context=context)
        self.number = 0
        self.localcontext.update({
            'time': time, 
            'get_number': self.get_number,
        })

    def get_number(self):
        self.number += 1
        return self.number

report_sxw.report_sxw('report.account.invoice.fixed', 'account.invoice', 'addons/crea8s_glassfix/report/account_invoice_new.rml', parser=account_invoice_fixed)

