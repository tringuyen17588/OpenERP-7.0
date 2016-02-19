from report import report_sxw
from report.report_sxw import rml_parse
import random
from osv import fields, osv
import time
import pooler
import datetime
from datetime import timedelta

class crea8s_wzreport_sekai(osv.osv):
   _name = 'crea8s.wzreport.sekai'
   _columns = {
        'job_id': fields.many2one('mrp.production', 'Job Order'),
        'date_from': fields.datetime('Date From'),
        'date_to': fields.datetime('Date To'),
        'type': fields.selection([('1', 'Report 1'), ('2', 'Report 2')], string='Type of Report'),
       }
       
   def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        sekai_line = self.pool.get('crea8s.sekai.line')                
        res = self.read(cr, uid, ids, ['job_id',
                                       'date_from',
                                       'date_to'], context=context)
        res = res and res[0] or {}
        datas['model'] = 'crea8s.wzreport.sekai'
        for x in self.browse(cr, uid, ids):
            if x.type == '1':
                job_br = x.job_id
                line_wc = []
                hr_buget   = 0
                act_buget  = 0
                act_cost   = 0
                cost_buget = 0

                total_hr_buget   = 0
                total_act_buget  = 0
                total_act_cost   = 0
                total_cost_buget = 0
#    Get all Timesheet lines
                for line in job_br.workcenter_lines:
                    sk_l = sekai_line.search(cr, uid, [('production_id', '=', job_br.id),
                                                       ('workcenter_id', '=', line.workcenter_id.id)])
                    if sk_l:
                        act_buget = sum([x.time_comp for x in sekai_line.browse(cr, uid, sk_l)])
                        act_cost =  act_buget * line.workcenter_id.costs_hour
                    total_act_buget  += line.workcenter_id.costs_hour * line.cycle * line.hour
                    total_cost_buget += act_cost
                    line_wc.append({'hr_buget'   : line.cycle * line.hour, 
                                    'cost_buget' : line.workcenter_id.costs_hour * line.cycle * line.hour,
                                    'act_buget'  : act_buget,
                                    'act_cost'   : act_cost,
                                    'activity'   : line.name,
                                    'operation'  : line.workcenter_id.name})
                line_pos = []
                bom_br = job_br.bom_id
                material_cost = 0
                for po in bom_br.po_ids:
                    for po_line in po.order_line:
                        po_info = {'partner_id': po.partner_id.name,
                                   'product': po_line.name,
                                   'qty': po_line.product_qty and po_line.product_qty or 0,
                                   'po_date': po.date_order and time.strftime('%d/%m/%Y',time.strptime(po.date_order, '%Y-%m-%d')) or '',
                                   'po_number': po.name,
                                   'total': po_line.price_subtotal}
                        material_cost += po_line.price_subtotal
                        line_pos.append(po_info)
                res.update({'po'              : line_pos,
                            'check'           : line_wc,
                            'material_cost'   : material_cost,
                            'date_planned'    : job_br.date_planned and time.strftime('%d/%m/%Y',time.strptime(job_br.date_planned, '%Y-%m-%d %H:%M:%S')) or '', 
                            'date_required'   : job_br.date_required and time.strftime('%d/%m/%Y',time.strptime(job_br.date_required, '%Y-%m-%d %H:%M:%S')) or '',
                            'mrp_id'          : job_br.name and job_br.name or '',
                            'product_qty'     : job_br.product_qty and job_br.product_qty or '',
                            'partner_id'      : job_br.partner_id and job_br.partner_id.name or '',
                            'total_act_buget' : total_act_buget,
                            'total_cost_buget': total_cost_buget,
                            'percent'         : (total_cost_buget - total_act_buget) / total_act_buget,
                            'total_wc'        : material_cost + total_act_buget,
                            'total_act'       : material_cost + total_cost_buget,
                            'percent_all'     : (material_cost + total_cost_buget - material_cost - total_act_buget) / (material_cost - total_act_buget)})
                datas['form'] = res
                return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'crea8s_wzreport_report11',
                'datas'         : datas,
                }
            else:
                datas['form'] = res
                return {
                'type'          : 'ir.actions.report.xml',
                'report_name'   : 'crea8s_wzreport_report22',
                'datas'         : datas,
                }
crea8s_wzreport_sekai()

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'time': time,
        })
        self.context = context        