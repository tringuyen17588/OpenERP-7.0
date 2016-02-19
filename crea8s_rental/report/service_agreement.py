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
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import openerp.addons.decimal_precision as dp
from openerp.report import report_sxw

#   ===================
#    Report picking out
#   ==================

class crea8s_service_agreement_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_service_agreement_report, self).__init__(cr, uid, name, context=context)
        self.flag = 0
        self.localcontext.update({
            'time': time,
            'get_equipment': self.get_equipment,
            'get_equipment_non': self.get_equipment_non,
            'get_software': self.get_software,
            'get_software_non': self.get_software_non,
        })
        
    def get_equipment(self, line):
        result = []
        for x in line:
            if x.type == 'e_fxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<4:
            for a in range(4 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result
    
    def get_equipment_non(self, line):
        result = []
        for x in line:
            if x.type == 'e_nfxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<2:
            for a in range(2 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result

    def get_software(self, line):
        result = []
        for x in line:
            if x.type == 's_fxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<4:
            for a in range(4 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result
    
    def get_software_non(self, line):
        result = []
        for x in line:
            if x.type == 's_nfxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<2:
            for a in range(2 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result
            
report_sxw.report_sxw('report.crea8s_report_service_agreement',
                          'crea8s.service.agreement',
                          'addons/crea8s_crm/report/service_agreement.rml',
                          parser=crea8s_service_agreement_report)
#    For sale order
class crea8s_service_agreement_order_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_service_agreement_order_report, self).__init__(cr, uid, name, context=context)
        self.flag = 0
        self.localcontext.update({
            'time': time,
            'get_equipment': self.get_equipment,
            'get_equipment_non': self.get_equipment_non,
            'get_software': self.get_software,
            'get_software_non': self.get_software_non,
            'get_object': self.get_object,
        })
    
    def get_object(self, obj):
        if not obj:
            raise osv.except_osv('Error !', 'Please create Service Agreement before print it !')
        return obj
    
    def get_equipment(self, line):
        result = []
        for x in line:
            if x.type == 'e_fxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<4:
            for a in range(4 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result
    
    def get_equipment_non(self, line):
        result = []
        for x in line:
            if x.type == 'e_nfxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<2:
            for a in range(2 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result

    def get_software(self, line):
        result = []
        for x in line:
            if x.type == 's_fxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<4:
            for a in range(4 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result
    
    def get_software_non(self, line):
        result = []
        for x in line:
            if x.type == 's_nfxs':
                result.append({'name': x.name and x.name or ' ',
                               'serial': x.Serial and x.Serial or ' ',})
        if len(result)<2:
            for a in range(2 - len(result)):
                result.append({'name': ' ',
                               'serial': ' ',})
        return result
            
report_sxw.report_sxw('report.crea8s_report_service_agreement_order',
                          'sale.order',
                          'addons/crea8s_crm/report/service_agreement_order.rml',
                          parser=crea8s_service_agreement_order_report, header=False)
