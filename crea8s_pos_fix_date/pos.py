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
import datetime
from datetime import timedelta
import calendar

class crea8s_pos_fix_wz(osv.osv_memory):
    _name = "crea8s.pos.fix.wz"
    _columns = {
        'name': fields.datetime('Date'),
    }
    
    def fix_data(self, cr, uid, idds, context={}):
        for record in self.browse(cr, uid, idds):
            print record.name
            date_temp = datetime.datetime(int(record.name[:4]), int(record.name[5:7]), \
                                          int(record.name[8:10]), int(record.name[11:13]), \
                                          int(record.name[14:16]), int(record.name[17:19]))
            for x in range(calendar.monthrange(date_temp.year, date_temp.month)[1]):
                kqq = date_temp + datetime.timedelta(days = x)
                ids1 = self.pool.get('pos.order').search(cr, uid, [('order_date', '=', str(kqq)[:10])])
                for record in self.pool.get('pos.order').browse(cr, uid, ids1):
                    date_or1 = record.type
                    date_or2 = record.date_order
                    temp1 = datetime.datetime(int(date_or2[:4]), int(date_or2[5:7]), int(date_or2[8:10]), int(date_or2[11:13]), int(date_or2[14:16]), int(date_or2[17:19]))
                    temp1 += timedelta(hours=8)
                    date_or2g = str(temp1)[:10] or ''
                    if date_or1[:10] != date_or2g:
                        cr.execute(''' Update pos_order set order_date = '%s' where id = %s '''%(date_or1[:10],record.id))
        return 1
    
crea8s_pos_fix_wz()