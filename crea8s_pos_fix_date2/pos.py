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

class crea8s_pos_fix_wz1(osv.osv_memory):
    _name = "crea8s.pos.fix.wz1"
    _columns = {
        'name': fields.datetime('Date'),
    }
    
    def fix_data(self, cr, uid, idds, context={}):
        for record in self.browse(cr, uid, idds):
            date_temp = datetime.datetime(int(record.name[:4]), int(record.name[5:7]), \
                                          int(record.name[8:10]), int(record.name[11:13]), \
                                          int(record.name[14:16]), int(record.name[17:19]))
            for x in range(calendar.monthrange(date_temp.year, date_temp.month)[1]):
                kqq = date_temp + datetime.timedelta(days = x)
                ids1 = self.pool.get('pos.order').search(cr, uid, [('order_date', '=',  str(kqq)[5:7] + '/' + str(kqq)[8:10] + '/' + str(kqq)[:4])])
                for record in self.pool.get('pos.order').browse(cr, uid, ids1):
                    date_or2 = record.order_date
                    if '/' in date_or2:
                        tt = date_or2.split('/')
                        kq = tt[2] + tt[0] + tt[1]
                        cr.execute(''' Update pos_order set order_date = '%s' where id = %s '''%(kq,record.id))
        return 1
    
crea8s_pos_fix_wz1()