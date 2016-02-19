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

import time, datetime
from openerp.report import report_sxw


class crea8s_account_invoice_dotmatrix(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_account_invoice_dotmatrix, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_line': self.get_line,
        })
    def get_line(self, move_line):
        result = []
        stt = 0
        for a in move_line:
            stt += 1
            result.append({'stt': stt, 'data': a})
        return result

report_sxw.report_sxw(
    'report.crea8s.account.invoice.dotmatrix',
    'account.invoice',
    'addons/crea8s_invoice_domatix/account_print_invoice.rml',
    parser=crea8s_account_invoice_dotmatrix, header=False)