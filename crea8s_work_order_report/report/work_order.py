from report import report_sxw
from report.report_sxw import rml_parse
import random
from osv import fields, osv
import time
import pooler
import datetime
from datetime import timedelta

def _get_line_no_(objLines, line):
    iNo = 0
    for item in objLines: #obj.order_line:
        iNo += 1
        if (item.id == line.id):
            break
    return iNo

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
        })
        self.context = context

class crea8s_workorderpdf(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_workorderpdf, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'divmod': self.divmod1,
            'get_number': _get_line_no_,
        })

    def divmod1(self, num1, num2):
        return divmod(num1, num2)
        
report_sxw.report_sxw('report.crea8s.workorderpdf','mrp.production','addons/mrp/report/workorderpdf.rml',parser=crea8s_workorderpdf,header=False)

class crea8s_workcenter_code(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_workcenter_code, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_activity': self.get_activity,
        })

    def get_activity(self):
        cr  = self.cr
        uid = self.uid
        ids = self.pool.get('crea8s.sekai.activity').search(cr, uid, [], order='sequence')
        return self.pool.get('crea8s.sekai.activity').browse(cr, uid, ids)

report_sxw.report_sxw('report.crea8s.mrp.wc.barcode', 'mrp.workcenter', 'addons/crea8s_work_order_report/report/mrp_wc_barcode.rml',parser=crea8s_workcenter_code,header=False)

class crea8s_sekai_activity(osv.osv):
    _name = 'crea8s.sekai.activity'
    _columns = {
        'name': fields.char('Name', required=True, size=64),
        'sequence': fields.integer('Sequence'),
    }
crea8s_sekai_activity()

class crea8s_sekai_batch(osv.osv):
    _name = 'crea8s.sekai.batch'
    _columns = {
        'date': fields.datetime('Date'),
    }
    _rec_name = 'date'
crea8s_sekai_batch()
import datetime
from datetime import timedelta
class crea8s_sekai_line(osv.osv):
    _name = 'crea8s.sekai.line'
    _order = 'start_date desc, production_id desc, routing_workcenter_id'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_date_between(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            start_date = record.start_date and datetime.datetime(int(record.start_date[:4]), int(record.start_date[5:7]), \
                                          int(record.start_date[8:10]), int(record.start_date[11:13]), \
                                          int(record.start_date[14:16]), int(record.start_date[17:19])) or 0
            end_date = record.end_date and datetime.datetime(int(record.end_date[:4]), int(record.end_date[5:7]), \
                                          int(record.end_date[8:10]), int(record.end_date[11:13]), \
                                          int(record.end_date[14:16]), int(record.end_date[17:19])) or 0
            if end_date and start_date:
                kq = end_date - start_date
                result[record.id] = kq.seconds / 3600.00
            else:
                result[record.id] = 0
            date_re = record.date and record.date or ''
            cr.execute(''' Update crea8s_sekai_line set date_str = '%s' where id = %s'''%(str(date_re),record.id))
        return result

#    def _strdate(self, cr, uid, ids, field_name, arg=None, context=None):
#        result = {}
#        for r in self.browse(cr, uid, ids, context=context):
#            date_re = r.date and r.date or ''
#            cr.execute(''' Update crea8s_sekai_line set date_str = '%s' where id = %s'''%(str(date_re),r.id))
#            result[r.id] = str(date_re)
#        return result

    _columns = {
        'date': fields.date('Date'),
#        'date_str1': fields.function(_strdate, string='Date', type='char', size=256),
        'date_str': fields.char('Date', size=256),
        'scan_stn_id': fields.integer('Scan STN ID'),
        'scan_id': fields.integer('Scan ID'),
        'batch_id': fields.many2one('crea8s.sekai.batch', 'Batch Scan'),
        'production_id': fields.many2one('mrp.production', 'Job Order'),
        'routing_workcenter_id': fields.many2one('mrp.routing.workcenter', 'Routing'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Work Center'),
        'activity_id': fields.many2one('crea8s.sekai.activity', 'Activity'),
        'start_date': fields.datetime('Start Date'),
        'end_date': fields.datetime('End Date'),
        'current_date': fields.date('Date Report'),
        'time_comp':fields.function(_get_date_between, string='Time Taken'),
    }
    _rec_name = 'workcenter_id'

    def send_email_timesheet(self, cr, uid, ids=[], context={}):
        mail = self.pool.get('email.template')
        add = 8
        date_time = datetime.date.today()# -  timedelta(days=1)
        message_obj = self.pool.get('mail.compose.message')
        abc = message_obj.create(cr, uid, {'subject': 'TimeSheet for %s'%str(date_time)})
        vals = self.pool.get('mail.compose.message').generate_email_for_composer(cr, uid, 9, 1612, {'lang': 'en_US', 
'default_body': u'', 
'default_parent_id': False, 
'tz': 'Europe/Brussels', 
'uid': 1, 
'mail_post_autofollow': True, 
'default_composition_mode': 'comment', 
})
        attach_ids = self.pool.get('ir.attachment').create(cr, uid, {
'name': 'Time Sheet '+ str(date_time),
'datas_fname': 'Time Sheet '+ str(date_time) + '.pdf',
'res_model': 'mail.compose.message',
'type':'binary',
'db_datas': vals['attachments'][0][1]
})

        date_time = datetime.date.today()# -  timedelta(days=1)
        vals1 = self.pool.get('mail.compose.message').generate_email_for_composer(cr, uid, 10, 1612, {'lang': 'en_US', 
'default_body': u'', 
'default_parent_id': False, 
'tz': 'Europe/Brussels', 
'uid': 1, 
'mail_post_autofollow': True, 
'default_composition_mode': 'comment', 
})
        attach_ids1 = self.pool.get('ir.attachment').create(cr, uid, {
'name': 'Time Sheet '+ str(date_time),
'datas_fname': 'Time Sheet '+ str(date_time) + '(excel).ods',
'res_model': 'mail.compose.message',
'type':'binary',
'db_datas': vals1['attachments'][0][1]
})

        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,85))
#        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,74))
#        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,211))
#        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,212))
#        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,213))
#        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,214))
#        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,215))
        cr.execute(''' insert into mail_compose_message_ir_attachments_rel values(%s,%s) '''%(abc,attach_ids))
        cr.execute(''' insert into mail_compose_message_ir_attachments_rel values(%s,%s) '''%(abc,attach_ids1))
        cr.commit()
        self.pool.get('mail.compose.message').send_mail(cr, uid, [abc], {'default_model' : 'crea8s.sekai.line','default_res_id': add})
        return 1



    def send_email_timesheet_beta(self, cr, uid, ids=[], context={}):
        mail = self.pool.get('email.template')
        add = 8
        date_time = datetime.date.today()# -  timedelta(days=1)
        message_obj = self.pool.get('mail.compose.message')
        abc = message_obj.create(cr, uid, {'subject': 'TimeSheet for %s (beta)'%str(date_time)})
        vals = self.pool.get('mail.compose.message').generate_email_for_composer(cr, uid, 10, 1612, {'lang': 'en_US', 
'default_body': u'', 
'default_parent_id': False, 
'tz': 'Europe/Brussels', 
'uid': 1, 
'mail_post_autofollow': True, 
'default_composition_mode': 'comment', 
})
        attach_ids = self.pool.get('ir.attachment').create(cr, uid, {
'name': 'Time Sheet '+ str(date_time),
'datas_fname': 'Time Sheet '+ str(date_time) + '(excel).ods',
'res_model': 'mail.compose.message',
'type':'binary',
'db_datas': vals['attachments'][0][1]
})
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,85))
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,74))
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,211))
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,212))
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,213))
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,214))
        cr.execute(''' insert into mail_compose_message_res_partner_rel values(%s,%s) '''%(abc,215))
        cr.execute(''' insert into mail_compose_message_ir_attachments_rel values(%s,%s) '''%(abc,attach_ids))
        cr.commit()
        self.pool.get('mail.compose.message').send_mail(cr, uid, [abc], {'default_model' : 'crea8s.sekai.line','default_res_id': add})
        return 1
crea8s_sekai_line()

class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a purchase order without any purchase order line.'))
            for line in po.order_line:
                if line.state=='draft':
                    todo.append(line.id)
            old_name = po.name
            old_name = old_name.split('RFQ')[0] + 'PO'
            self.write(cr, uid, [po.id], {'name': old_name})
        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id in ids:
            self.write(cr, uid, [id], {'state' : 'confirmed', 'validator' : uid})
        return True

#class mrp_production(osv.osv):
#    _inherit = "mrp.production"
#    _columns = {
#        'sekai_line': fields.many2one('crea8s.sekai.line', 'production_id', 'Sekai Line'),
#    }
#mrp_production()

#class mrp_workcenter(osv.osv):
#    _inherit = "mrp.workcenter"
#    _columns = {
#        'sekai_line': fields.many2one('crea8s.sekai.line', 'workcenter_id', 'Sekai Line'),
#    }
#mrp_workcenter()

class crea8s_timesheet_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crea8s_timesheet_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_all_line': self.get_activity,
            'get_activity_detail': self.get_activity_detail,
            'get_mrp': self.get_mrp,
            'get_wct': self.get_wct,
            'get_activity': self.get_activity,
            'get_date': self.get_date,
            'get_time': self.get_time,
        })

    def get_time(self, hour):
        if not hour:
            return '00:00'
        h = divmod(hour,1)
        h1 = ''
        m1 = ''
        m = 0
        if h[1] > 0:
            m = h[1] * 60
            m = divmod(m,1)[0]
        h = round(h[0],0)
        if m < 10 and m > 0:
            m1 = '0%s'%str(m)[:len(str(m))-2]
        elif m > 10:
            m1 = str(m)[:len(str(m))-2]
        else:
            m1 = '00'
        if h < 10 and h > 0:
            h1 = '0%s'%str(h)[:len(str(h))-2]
        elif h > 10:
            h1 = str(h)[:len(str(h))-2]
        else:
            h1 = '00'
        return h1 + ':' + m1

    def convert_date(self, date_con):
        if not date_con:
            return ''
        a = datetime.datetime(int(date_con[:4]), int(date_con[5:7]), int(date_con[8:10]), int(date_con[11:13]), int(date_con[14:16]), int(date_con[17:19]))
        a += timedelta(hours=8)
        return str(a)

    def get_date(self):
        return datetime.date.today()# - timedelta(days=1)

    def get_mrp(self):
        cr  = self.cr
        uid = self.uid
        a = datetime.date.today()
        result1 = []
        start_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 0,0,0)
        end_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 16,59,59)
        #start_date -= timedelta(hours=8)
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '!=', False)])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
        lst_mrp = [a.production_id for a in lst_line]
        lst_mrp = list(set(lst_mrp))
        return lst_mrp

    def get_total_detail(self, mrp_id, routing):
        cr  = self.cr
        uid = self.uid
        a = datetime.date.today()
        result1 = []
        start_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 0,0,0)
        end_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 16,59,59)
        #start_date -= timedelta(hours=8)
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '!=', False)])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)        
        lst_routing = 0
        for x in lst_line:
            if x.routing_workcenter_id and x.production_id == mrp_id and x.routing_workcenter_id.name == routing:
                lst_routing += x.time_comp
        return lst_routing

    def get_activity_detail(self, mrp_id):
        cr  = self.cr
        uid = self.uid
        a = datetime.date.today()
        result1 = []
        start_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 0,0,0)
        end_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 16,59,59)
        #start_date -= timedelta(hours=8)
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '!=', False)], order='production_id, routing_workcenter_id')
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)        
        lst_routing = ''
        lst_wct = [x.routing_workcenter_id.name for x in lst_line]
        lst_wct = list(set(lst_wct))
        lst_duration = []
        lst_start = []
        lst_end = []
        lst_routing = [y.routing_workcenter_id for y in lst_line if y.routing_workcenter_id and y.production_id == mrp_id] 
        lst_routing = list(set(lst_routing))
        for k in lst_routing:
            for x in lst_line:
                if x.routing_workcenter_id == k and x.production_id == mrp_id:
                    result1.append({'act' : x.routing_workcenter_id.name,
                                'tcop': x.time_comp,
                                'wct': x.workcenter_id.name,
                                'start': self.convert_date(x.start_date),
                                'end': self.convert_date(x.end_date)})
            result1.append({'act' : '', 'tcop': self.get_total_detail(mrp_id,k.name), 'wct': '', 'start':'', 'end': 'Total'})
        return result1

    def get_wct(self):
        cr  = self.cr
        uid = self.uid
        a = datetime.date.today()
        result1 = []
        start_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 0,0,0)
        end_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 16,59,59)
        #start_date -= timedelta(hours=8)
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '=', False),
                                                                  ('routing_workcenter_id', '=', False)])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
        lst_wct = [a.workcenter_id for a in lst_line]
        lst_wct = list(set(lst_wct))
        return lst_wct

    def get_total_activity(self, wct_id, act):
        cr  = self.cr
        uid = self.uid
        a = datetime.date.today()
        result1 = []
        start_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 0,0,0)
        end_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 16,59,59)
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '=', False),
                                                                  ('routing_workcenter_id', '=', False)])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
        result = sum([x.time_comp for x in lst_line if x.activity_id == act and x.workcenter_id == wct_id])
        return result

    def get_activity(self, wct_id):
        cr  = self.cr
        uid = self.uid
        a = datetime.date.today()
        result1 = []
        start_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 0,0,0)
        end_date = a #- timedelta(days=1)#datetime.datetime(a.year, a.month, a.day - 1, 16,59,59)
        #start_date -= timedelta(hours=8)
        ids = self.pool.get('crea8s.sekai.line').search(cr, uid, [('date', '>=', str(start_date)),
                                                                  ('date', '<=', str(end_date)),
                                                                  ('production_id', '=', False),
                                                                  ('routing_workcenter_id', '=', False)])
        lst_line = self.pool.get('crea8s.sekai.line').browse(cr, uid, ids)
        lst_tmp_mrp  = []
        lst_activity = [y.activity_id for y in lst_line if y.activity_id and y.workcenter_id == wct_id]
        lst_activity = list(set(lst_activity))
        lst_duration = []
        for z in lst_activity:
            for x in lst_line:
                if x.activity_id == z and x.workcenter_id == wct_id:
                    result1.append({'act' : x.activity_id.name,
                                'tcop': x.time_comp,
                                'start_date': self.convert_date(x.start_date),
                                'end_date':   self.convert_date(x.end_date),
                })
            result1.append({'act' : '',
                                'tcop': self.get_total_activity(wct_id, z),
                                'start_date': '',
                                'end_date':   'Total',
                })
        return result1

report_sxw.report_sxw('report.crea8s.timesheet.report', 'crea8s.sekai.line', 'addons/crea8s_work_order_report/report/timesheetpdf.rml',parser=crea8s_timesheet_report,header=False)