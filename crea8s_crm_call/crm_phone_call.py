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
from openerp.addons.base_status.base_state import base_state
from openerp.tools.translate import _
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time


class crm_phonecall(base_state, osv.osv):
    _inherit = "crm.phonecall"
    
    _columns = {
        'telephone': fields.char('Telephone', size=32),
        'cnt_contact': fields.char('Contact', size=256),
        'email': fields.char('Email / Remarks', size=256),
        'meeting_ids': fields.one2many('crm.meeting', 'phonecall_id', 'Meeting'),
    }
    
crm_phonecall()
