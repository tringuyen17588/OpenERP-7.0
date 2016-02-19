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

class crea8s_account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw(
    'report.account.invoice.crea8s_derick',
    'account.invoice',
    'addons/crea8s_derick/report/account_print_invoice.rml',
    parser=crea8s_account_invoice, header=False
)

class crea8s_account_invoice1(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_account_invoice1, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })
report_sxw.report_sxw(
    'report.account.invoice.crea8s_derick1',
    'account.invoice',
    'addons/crea8s_derick/report/account_print_invoice1.rml',
    parser=crea8s_account_invoice1, header=False
)