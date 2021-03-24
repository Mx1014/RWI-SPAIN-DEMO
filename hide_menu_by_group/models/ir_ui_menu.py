# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    hide_groups_id = fields.Many2many(string="Hide For",
        comodel_name="res.groups",
        relation="ir_ui_menu_hide_group_rel")

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        """ Return the ids of the menu items visible to the user. """
        # retrieve all menus, and determine which ones are visible
        context = {'ir.ui.menu.full_list': True}
        menus = self.with_context(context).search([])

        groups = self.env.user.groups_id
        if not debug:
            groups = groups - self.env.ref('base.group_no_one')
        # first discard all menus with groups the user does not have
        menus = menus.filtered(
            lambda menu: not menu.groups_id or menu.groups_id & groups)
        
        # discard those that should be hidden for the group
        menus = menus.filtered(
            lambda menu: not (menu.hide_groups_id & groups))
        
        # apply menu visibility limits if any
        show_only_menus = groups.mapped('limit_menu_access')
        if show_only_menus:
            for menu in show_only_menus:
                child_menus = self.with_context(context).search([('id','child_of',show_only_menus.ids)])
            menus = menus & child_menus

        # take apart menus that have an action
        action_menus = menus.filtered(lambda m: m.action and m.action.exists())
        folder_menus = menus - action_menus
        visible = self.browse()

        # process action menus, check whether their action is allowed
        access = self.env['ir.model.access']
        MODEL_GETTER = {
            'ir.actions.act_window': lambda action: action.res_model,
            'ir.actions.report': lambda action: action.model,
            'ir.actions.server': lambda action: action.model_id.model,
        }
        for menu in action_menus:
            get_model = MODEL_GETTER.get(menu.action._name)
            if not get_model or not get_model(menu.action) or \
                    access.check(get_model(menu.action), 'read', False):
                # make menu visible, and its folder ancestors, too
                visible += menu
                menu = menu.parent_id
                while menu and menu in folder_menus and menu not in visible:
                    visible += menu
                    menu = menu.parent_id

        return set(visible.ids)