odoo.define('sincro_data.kanban_view_button', function (require){
    "use strict";
    var core = require('web.core');
    var KanbanController = require('web.KanbanController');
    var KanbanView = require('web.KanbanView');

    var includeDict = {
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (['adm.application','adm.reenrollment'].includes(this.modelName)) {
                var your_btn = this.$buttons.find('button.o_kanban_button_export_to_facts');
                your_btn.on('click', this.proxy('o_kanban_button_export_to_facts'));
            }
        },
//        o_kanban_button_export_to_facts: function(event) {
//            event.preventDefault();
//            var self = this;
//            self.do_action({
//                'type': 'ir.actions.act_window',
//                'name': 'Select Students for export to FACTS:',
//                'res_model': 'sincro_data.export_data',
//                'view_type': 'form',
//                'view_mode': 'form',
//                'views': [[false, 'form']],
//                'target': 'new',
//                'flags': {'form': {'action_buttons': true}}
//            });
//        }




//        o_kanban_button_export_to_facts: function(event) {
//            event.preventDefault();
//            var self = this;
//            self.do_action({
//                'type': 'ir.actions.act_window',
//                'name': 'Select Students for export to FACTS:',
//                'res_model': 'sincro_data.export_data_wizard',
//                'view_type': 'tree',
//                'view_mode': 'tree,form',
//                'views': [(False, 'list'), (False, 'form')],
//                'target': 'new'
//            });
//        }
        o_kanban_button_export_to_facts: function(event) {
            event.preventDefault();
            var self = this;
            self.do_action({
                'type': 'ir.actions.act_window',
                'name': 'Select Students for export to FACTS:',
                'res_model': 'sincro_data.export_data',
                'view_type': 'tree',
                'view_mode': 'tree,form',
                'domain': [['item','like','adm.application']],
                'views': [[false, 'list'], [false, 'form']],
                'target': 'current',
            });
        }

//        o_kanban_button_export_to_facts: function(event) {
//            event.preventDefault();
//            var self = this;
//            self.do_action({
//                'type': 'ir.actions.act_window',
//                'name': 'Select Students for export to FACTS:',
//                'res_model': 'adm.application',
//                'view_type': 'tree',
//                'view_mode': 'tree,form',
////                'domain': [['item','like','adm.application']],
//                'views': [[false, 'list'], [false, 'form']],
//                'target': 'new'
//            });
//        }
    };

    KanbanController.include(includeDict);

//
//    var includeDict = {
//        renderButtons: function () {
//            this._super.apply(this, arguments);
////            if (['adm.application','adm.reenrollment'].includes(this.modelName)) {
//            var your_btn = this.$buttons.find('button.o_kanban_button_accepted_export');
//            your_btn.on('click', this.proxy('o_kanban_button_accepted_export'));
////            }
//        },
//
//        o_kanban_button_accepted_export: function(event) {
//            event.preventDefault();
//            var self = this;
//            self.do_action({
//                'type': 'ir.actions.act_window',
//                'name': 'Select Students for export to FACTS:',
//                'res_model': 'sincro_data.export_data',
//                'view_type': 'tree',
//                'view_mode': 'tree,form',
//                'domain': [['item','like','adm.application']],
//                'views': [[false, 'list'], [false, 'form']],
//                'target': 'new'
//            });
//        }
//    };
//
//    KanbanController.include(includeDict);
});