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
        })
        self.context = context
