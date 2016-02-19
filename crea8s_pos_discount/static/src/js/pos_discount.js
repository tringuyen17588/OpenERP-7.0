
// ##############################################################################
// #    Module : POS Cashiers
// #    Manage cashiers for Point Of Sale
// #    Author : Thierry Godin <thierry@lapinmoutardepommedauphine.com>
// #    Copyright (C) 2013 Thierry Godin 
// #
// #    This program is free software: you can redistribute it and/or modify
// #    it under the terms of the GNU Affero General Public License as
// #    published by the Free Software Foundation, either version 3 of the
// #    License, or (at your option) any later version.
// #
// #    This program is distributed in the hope that it will be useful,
// #    but WITHOUT ANY WARRANTY; without even the implied warranty of
// #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// #    GNU Affero General Public License for more details.
// ##############################################################################

function openerp_pos_fix(instance, module){ //module is instance.point_of_sale
    var module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    _t = instance.web._t;

    globalCashier = null;

    module.partnerCategoriesWidget = module.PosWidget.include({
        template: 'PosWidget',  

		start: function() {
            var self = this;
            return self.pos.ready.done(function() {
                self.build_currency_template();
                self.renderElement();
                
                self.$('.neworder-button').click(function(){
                    self.pos.add_new_order();
                });
                self.$('#discount_fnc').click(function(){
                    //self.pos.get('selectedOrder').getSelectedLine().set_discount(20);
					self.pos.get('selectedOrder').get('orderLines').each(function(orderline){
						orderline.set_discount(self.$('#discount_box').val());
					});
					//alert('Da vo ham nay roi');
                });
                //when a new order is created, add an order button widget
                self.pos.get('orders').bind('add', function(new_order){
                    var new_order_button = new module.OrderButtonWidget(null, {
                        order: new_order,
                        pos: self.pos
                    });
                    new_order_button.appendTo($('#orders'));
                    new_order_button.selectOrder();
                }, self);

                self.pos.get('orders').add(new module.Order({ pos: self.pos }));

                self.build_widgets();

                self.screen_selector.set_default_screen();

                window.screen_selector = self.screen_selector;

                self.pos.barcode_reader.connect();

                instance.webclient.set_content_full_screen(true);

                if (!self.pos.get('pos_session')) {
                    self.screen_selector.show_popup('error', 'Sorry, we could not create a user session');
                }else if(!self.pos.get('pos_config')){
                    self.screen_selector.show_popup('error', 'Sorry, we could not find any PoS Configuration for this session');
                }
            
                instance.web.unblockUI();
                self.$('.loader').animate({opacity:0},1500,'swing',function(){self.$('.loader').hide();});

                self.pos.flush();

            }).fail(function(){   // error when loading models data from the backend
                instance.web.unblockUI();
                return new instance.web.Model("ir.model.data").get_func("search_read")([['name', '=', 'action_pos_session_opening']], ['res_id'])
                    .pipe( _.bind(function(res){
                        return instance.session.rpc('/web/action/load', {'action_id': res[0]['res_id']})
                            .pipe(_.bind(function(result){
                                var action = result.result;
                                this.do_action(action);
                            }, this));
                    }, self));
            });
        },
    });
	
	
};


openerp.point_of_sale = function(instance) {
    instance.point_of_sale = {};
    var module = instance.point_of_sale;
    openerp_pos_db(instance,module);            // import db.js
    openerp_pos_models(instance,module);        // import pos_models.js
    openerp_pos_basewidget(instance,module);    // import pos_basewidget.js
    openerp_pos_keyboard(instance,module);      // import  pos_keyboard_widget.js
    openerp_pos_scrollbar(instance,module);     // import pos_scrollbar_widget.js
    openerp_pos_screens(instance,module);       // import pos_screens.js
    openerp_pos_widgets(instance,module);       // import pos_widgets.js
    openerp_pos_devices(instance,module);       // import pos_devices.js
    openerp_pos_fix(instance,module);       	// import openerp_pos_fix
    instance.web.client_actions.add('pos.ui', 'instance.point_of_sale.PosWidget');
};