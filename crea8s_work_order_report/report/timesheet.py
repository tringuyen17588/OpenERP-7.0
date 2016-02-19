from report import report_sxw
from report.report_sxw import rml_parse
import random
from osv import fields, osv
import time
import pooler
import datetime
from datetime import timedelta

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
            'get_mrp': self.get_mrp,
            'mrp_date': self.get_result_joborder,
            'get_date': self.get_date,
        })
        self.context = context
        self.a = datetime.date.today() - timedelta(days=4)

    def get_num_list(self, number):
	start = 0
	end = 0
	result = []
	for x in range(0, (number / 3) + 1):
		end += 3
		result.append([start, end])
		start += 3
	return result

    def convert_date(self, date_con):
        if not date_con:
            return ''
        a = datetime.datetime(int(date_con[:4]), int(date_con[5:7]), int(date_con[8:10]), int(date_con[11:13]), int(date_con[14:16]), int(date_con[17:19]))
        a += timedelta(hours=8)
        return a

    def get_date(self, current_date):
        #self.a = current_date
        return self.a

    def get_mrp(self):
        cr  = self.cr
        uid = self.uid
        a = self.a
        result1 = []
        start_date = a
        end_date = a
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date))])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
        lst_duration = []
        lst_start = []
        lst_end = []
        lst_wcid = [y.workcenter_id and str(y.workcenter_id.name) or ' ' for y in lst_line]
        lst_wcid = list(set(lst_wcid))
        lst_wcid.sort()
        return lst_wcid

    def get_mrp1(self):
        cr  = self.cr
        uid = self.uid
        a = self.a
        result1 = []
        start_date = a 
        end_date = a 
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('start_date', '!=', False)])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
        lst_duration = []
        lst_start = []
        lst_end = []
        lst_wcid = [y.workcenter_id and str(y.workcenter_id.name) or ' ' for y in lst_line]
        lst_wcid = list(set(lst_wcid))
        lst_wcid.sort()
        for kk in lst_wcid:
            result1.append(['Time Start', 'Time End', kk])
        return result1

    def mrp_date(self, hour, x):
        lst_wcid = self.get_mrp()
        cr  = self.cr
        uid = self.uid
        a = self.a
        result = []
        start_date = a
        end_date = a
        if 1 < 2: #for x in lst_wcid:
            result1 = []
            ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '!=', False),
                                                                  ('workcenter_id.name', 'like', x)])
            if ids:
                lst_lines = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
                temp_min = 0
                temp_hour = 0
                for lst_line in lst_lines:
                    date_start = lst_line.start_date and self.convert_date(lst_line.start_date) or ''
                    date_end = lst_line.end_date and self.convert_date(lst_line.end_date) or ''
                    if date_start:
                        if date_start.hour == hour:
                            if date_start.minute - temp_min <= 1 and date_start.hour == temp_hour:
                                continue
# Time Start
                            result1.append('%s%s%s'%((date_start.hour < 10 and date_start.hour >= 0) and '0%s'%str(date_start.hour) or str(date_start.hour) \
, ':' \
, (date_start.minute < 10 and date_start.minute >= 0) and '0%s'%str(date_start.minute) or str(date_start.minute)))

# Time End
                            if date_end: 
                                result1.append('%s%s%s'%((date_end.hour < 10 and date_end.hour >= 0) and '0%s'%str(date_end.hour) or str(date_end.hour) \
, ':' \
, (date_end.minute < 10 and date_end.minute >= 0) and '0%s'%str(date_end.minute) or str(date_end.minute)))
                            else: 
                                result1.append('-')
# Job Order
                            result1.append('Job Order %s'%str(lst_line.production_id.name))
                    else:
                        pass
                    temp_min = date_start.minute
                    temp_hour = date_start.hour
            else:
                pass
            result = result1
        return result

    def get_result_joborder(self):
        result = []
        for x in self.get_mrp1():
            result1 = []
            result.append([' ', ' ', ' '])
            result.append(x)
            tmp1 = x[len(x) - 1]
            if tmp1:
                for b in range(0,24):
                    tmp = self.mrp_date(b, tmp1)
                    if tmp:
                        result1.append(tmp)
                    tam = self.get_activity_dtl(b, tmp1)
                    if tam:
                        if len(tam) > 3:
                            for kk in self.get_num_list(len(tam)):
                                if tam[kk[0]:kk[1]]:
                                    result1.append(tam[kk[0]:kk[1]])
                        elif len(tam) > 0:
                            result1.append(self.get_activity_dtl(b, tmp1))
                result1.sort()
                result += result1
        
            
        return result

    def get_activity_dtl(self, hour, wct_id):
        cr  = self.cr
        uid = self.uid
        a = self.a
        result = []
        result1 = []
        start_date = a
        end_date   = a
        if 1<2:#for wct_id in self.get_wct():
            ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '=', False),
                                                                  ('routing_workcenter_id', '=', False), ('workcenter_id.name', 'like', wct_id)])
            lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
            lst_act_name = [y.activity_id for y in lst_line]
            lst_act_name = list(set(lst_act_name))
#    Get list activities of this work center
            lst_tmp = []
            result1 = []
            for act_info in lst_act_name:

                temp_min = 0
                temp_hour = 0
                for k in lst_line:
                    if k.activity_id == act_info:
                        date_start = k.start_date and self.convert_date(k.start_date) or ''
                        date_end = k.end_date and self.convert_date(k.end_date) or ''
                        if date_start:
                            if date_start.hour == hour:
                                if date_start.minute - temp_min <= 1 and date_start.hour == temp_hour:
                                    continue
# Time Start
                                result1.append('%s%s%s'%((date_start.hour < 10 and date_start.hour >= 0) and '0%s'%str(date_start.hour) or str(date_start.hour) \
, ':' \
, (date_start.minute < 10 and date_start.minute >= 0) and '0%s'%str(date_start.minute) or str(date_start.minute)))
# Time End
                                if date_end:
                                    result1.append('%s%s%s'%((date_end.hour < 10 and date_end.hour >= 0) and '0%s'%str(date_end.hour) or str(date_end.hour) \
, ':' \
, (date_end.minute < 10 and date_end.minute >= 0) and '0%s'%str(date_end.minute) or str(date_end.minute)))
                                else:
                                    result1.append('-')
# Activities
                                result1.append(act_info.name)
                        temp_min = date_start.minute
                        temp_hour = date_start.hour
        return result1