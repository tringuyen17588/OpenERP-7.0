# -*- coding: UTF-8 -*-
'''
    sale

    :copyright: (c) 2014-2015 by PhongND
    :license: AGPLv3, see LICENSE for more details
'''
from openerp.osv import osv, fields
# from openerp.tools.translate import _
import time
import datetime
from datetime import timedelta
from datetime import datetime

#for logging 
import logging
_logger = logging.getLogger(__name__)

class sale_order(osv.Model):
    """ Sale Order
    """
    _inherit = 'sale.order'
    def _crea8s_product_margin_percent(self, cursor, user, ids, field_name, arg, context=None):
        """
        Margin on lines = SP@ * (100 - %discount) - CP@
        Profit Margin % on lines = (SP@ * (100 - %discount) - CP@) / SP@ 
        Profit Margin % TOTAL = sum all lines. 
        
        @author: PhongND 20141204
        """
         
        result = {}
        for sale in self.browse(cursor, user, ids, context=context):
            result[sale.id] = 0.0
            for line in sale.order_line:
                result[sale.id] += line.crea8s_profit_margin_percent or 0.0
        return result
        
    _columns = {
        'crea8s_profit_margin_percent': fields.function(_crea8s_product_margin_percent, string='Profit Margin (%)', \
        help="It gives profitability in Percent by calculating the % difference between the Sale Price and the Cost Price.", store=True),
        'crea8s_vec_valid_till': fields.date('Valid Till'),
        'crea8s_vec_shipment_terms': fields.char('Shipment Terms', size=128),
        'crea8s_vec_lead_time': fields.char('Lead Time', size=128),
        'crea8s_vec_project_id': fields.many2one('crea8s.vec.project', 'Project ID'),
        'crea8s_vec_project_ref': fields.related('crea8s_vec_project_id', 'ref', type='char', \
                                                 relation='crea8s.vec.project', string='Project Ref', store=True),
        'crea8s_vec_project_name': fields.related('crea8s_vec_project_id', 'name', type='char', \
                                                  relation='crea8s.vec.project', string='Project Name', store=False),
        'crea8s_vec_ob_ref': fields.char('OB Ref', size=128),
        'crea8s_vec_type_of_proposal': fields.many2one('crea8s.vec.type.of.proposal', 'Type of Proposal'),
        'crea8s_vec_type_of_proposal_package': fields.many2one('crea8s.vec.type.of.proposal.package', 'Type of Proposal Package'),
        'crea8s_vec_project_site': fields.many2one('res.country', 'Project Site'),
        'crea8s_vec_name_of_end_user': fields.char('Name of End User', size=30),
        'crea8s_vec_proposal_sales_rep': fields.many2one('hr.employee', 'Proposal/Sales Rep'),
        
    }
    
    def write(
        self, cursor, user, ids, sale_data, context=None
    ):
        """
        Find or Create sale using sale data

        :param cursor: Database cursor
        :param user: ID of current user
        :param ids: array ID of saving Sale
        :param sale_data: Order Data from sale
        :param context: Application context
        :returns: 
        """
        
        # only change OrderDate if SO in draft state
        boAllowUpdate = True
        print 'gia tri cap nhat  ==  ', sale_data
        if (sale_data.has_key('date_order')):
            boAllowUpdate = False
        else:
            for intID in ids: # loop a list.
                objSale = self.browse(cursor, user, intID, context=context)
                if (objSale.state != 'draft' ):
                    boAllowUpdate = False 
        if (boAllowUpdate):
            sale_data['date_order'] =  datetime.utcnow() # + timedelta(days=1) #  ... time.strptime(strDate, '%Y-%m-%d').strftime('%d-%m-%Y')
        return super(sale_order, self).write(cursor, user, ids, sale_data, context=context)
        
sale_order()
    
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"

    _columns = {
        'crea8s_profit_margin_percent': fields.float(string='Profit Margin (%)', readonly=True, states={'draft': [('readonly', False)]}),
        'crea8s_vec_product_title': fields.char('Product Title', size=128),
        
    }

    def onchange_profit_unit_price(
        self, cursor, user, ids, change_type, price_unit, purchase_price, crea8s_profit_margin_percent, discount, context=None
    ):
        reValue = {}
        
        if (change_type == 1): #change crea8s_profit_margin_percent => update...
            if crea8s_profit_margin_percent >= 100.0:
                crea8s_profit_margin_percent = 0
                reValue.update({'crea8s_profit_margin_percent': 0.0})
            reValue.update({'price_unit': self.calculate_price_unit( cursor, user, ids, price_unit, \
                    purchase_price, crea8s_profit_margin_percent, discount, context)})
            
        else: # change: price_unit => update...
            reValue.update({'crea8s_profit_margin_percent': self.calculate_margin_percent( cursor, user, ids, price_unit, \
                    purchase_price, crea8s_profit_margin_percent, discount, context)})
        
        _logger.info('onchange_profit_unit_price: change_type=' + str(change_type)) 
        return {'value': reValue}
    
    def calculate_margin_percent(self, cursor, user, ids, price_unit, purchase_price, crea8s_profit_margin_percent, discount, context=None):
        """
        Rules:
        + Margin on lines = SP@ * (100 - %discount) - CP@
        + Profit Margin % on lines = (SP@ * (100 - %discount) - CP@) / SP@ 
        + Profit Margin % TOTAL = sum all lines. 
        
        @author: PhongND 20141209
        """
        reAmount = 0.0
        sale_price_final = (price_unit*(100.0-discount)/100.0)
        
        if sale_price_final == 0:
            reAmount = 0.0
        else:
            reAmount = round((sale_price_final - (purchase_price))* 100.0 /sale_price_final, 2) 
        return reAmount
    
    
    def calculate_price_unit(self, cursor, user, ids, price_unit, purchase_price, crea8s_profit_margin_percent, discount, context=None):
        """
        Rules:
        + Margin on lines = SP@ * (100 - %discount) - CP@
        + Profit Margin % on lines = (SP@ * (100 - %discount) - CP@) / SP@ 
        + Profit Margin % TOTAL = sum all lines. 
        
        @author: PhongND 20141209
        """
        sale_price_final = 0.0
            
        if crea8s_profit_margin_percent < 100.0:
            sale_price_final = purchase_price / (1.0 - crea8s_profit_margin_percent/100.0)
            
        price_unit = round(sale_price_final * 100.00 / (100.0-discount), 2)  # phongnd 20141211 - must-have round 
        
        return price_unit

sale_order_line()