odoo.define('adm.reenrollment.kanban_view_button', require => {
    "use strict";

    require('web.core');
    const KanbanController = require('web.KanbanController');

    KanbanController.include({

        events: _.extend({}, KanbanController.prototype.events, {
            'click button.o_kanban_button_create_reenrollment': '_onClick',
        }),

        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName === 'adm.reenrollment') {
                const $createReenrollmentPackage = this.$buttons.find('button.o_kanban_button_create_reenrollment_packages');
                $createReenrollmentPackage.on('click', event => {
                    event.preventDefault();
                    this.do_action({
                        'type': 'ir.actions.act_window',
                        'name': 'Create reenrollment package',
                        'res_model': 'create.reenrollment.package',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'views': [[false, 'form']],
                        'target': 'new'
                    });
                });


                const $createReenrollmentRecords = this.$buttons.find('button.o_kanban_button_create_reenrollment_records');
                $createReenrollmentRecords.on('click', event => {
                    event.preventDefault();
                    this.do_action({
                        'type': 'ir.actions.act_window',
                        'name': 'Create reenrollment records',
                        'res_model': 'create.reenrollment.records',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'views': [[false, 'form']],
                        'target': 'new'
                    });
                });
            }
        },
    });
});