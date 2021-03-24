# -*- coding: utf-8 -*-

import pytz
from collections import OrderedDict
from dateutil import parser

from odoo import fields, http, _, SUPERUSER_ID
from odoo.exceptions import MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        appproved_employee_ids = request.env["hr.employee"].sudo().search([("leave_manager_id","=",request.env.uid)]).ids
        values["time_off_count"] = request.env["hr.leave"].search_count([
            '|',("user_id","=",request.env.uid),("employee_id","in",appproved_employee_ids)])
        values["user"] = request.env.user
        values["time_off_types"] = request.env["hr.leave.type"].sudo().search([
            '&',('virtual_remaining_leaves','>',0),
                '|',('allocation_type','in',['fixed_allocation','no']),
                    '&',('allocation_type','=','fixed'),
                        ('max_leaves','>','0')])
        return values
    
    def _time_off_get_page_view_values(self, time_off, access_token, **kwargs):
        values = {
            "time_off": time_off,
            "user": request.env.user,
            "time_off_types": request.env["hr.leave.type"].sudo().search([
                '&',('virtual_remaining_leaves','>',0),
                '|',('allocation_type','in',['fixed_allocation','no']),
                    '&',('allocation_type','=','fixed'),
                        ('max_leaves','>','0')]),
            "request_date_from_period_options": request.env["hr.leave"].fields_get()["request_date_from_period"]["selection"],
            "request_hour_from_options": request.env["hr.leave"].fields_get()["request_hour_from"]["selection"],
            "request_hour_to_options": request.env["hr.leave"].fields_get()["request_hour_to"]["selection"],
        }
        values["time_off_types"] |= time_off.holiday_status_id
        return self._get_page_view_values(time_off, access_token, values, "my_time_offs_history", True, **kwargs)
    
    @http.route(["/my/time_off/", "/my/time_off/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_time_offs(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in="name", **kw):
        values = self._prepare_portal_layout_values()
        leave_obj = request.env["hr.leave"]
        domain = []

        archive_groups = self._get_archive_groups("hr.leave", domain)
        if date_begin and date_end:
            domain += [("create_date",">",date_begin),("create_date","<=",date_end)]

        searchbar_sortings = {
            "newest": {"label": _("Newest"), "order": "create_date desc"},
            "oldest": {"label": _("Oldest"), "order": "create_date asc"},
        }
        if not sortby:
            sortby = "newest"
        order = searchbar_sortings[sortby]["order"]
        
        appproved_employee_ids = request.env["hr.employee"].sudo().search([("leave_manager_id","=",request.env.uid)]).ids
        default_domain = ['|',("user_id","=",request.env.uid),("employee_id","in",appproved_employee_ids)]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": default_domain},
            "draft": {"label": _("To Submit"), "domain": [("state","=","draft"),('pullback_comment','=',False)] + default_domain},
            "pullback": {"label": _("Pullback"), "domain": [("state","=","draft"),('pullback_comment','!=',False)] + default_domain},
            "cancel": {"label": _("Cancelled"), "domain": [("state","=","cancel")] + default_domain},
            "confirm": {"label": _("To Approve"), "domain": [("state","=","confirm")] + default_domain},
            "refuse": {"label": _("Rejected"), "domain": [("state","=","refuse")] + default_domain},
            "validate1": {"label": _("Second Approval"), "domain": [("state","=","validate1")] + default_domain},
            "validate": {"label": _("Approved"), "domain": [("state","=","validate")] + default_domain},
        }
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]['domain']

        searchbar_inputs = {
            "name": {"input": "name", "label": _("Search in Description")},
            "holiday_status_id": {"input": "holiday_status_id", "label": _("Search in Type")},
        }
        if search and search_in:
            search_domain = []
            if search_in == "name":
                search_domain = OR([search_domain, [("name","ilike",search)]])
            elif search_in == "holiday_status_id":
                search_domain = OR([search_domain, [("holiday_status_id","ilike",search)]])
            domain += search_domain

        time_off_count = leave_obj.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/time_off",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=time_off_count,
            page=page,
            step=self._items_per_page
        )

        time_offs = leave_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])
        request.session["my_time_offs_history"] = time_offs.ids[:100]

        values.update({
            "date": date_begin,
            "date_end": date_end,
            "time_offs": time_offs,
            "page_name": "time_off",
            "archive_groups": archive_groups,
            "default_url": "/my/time_off",
            "pager": pager,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
            "filterby": filterby,
            "searchbar_inputs": searchbar_inputs,
            "search_in": search_in,
            "search": search,
        })
        return request.render("hr_holidays_portal.portal_my_time_offs", values)
    
    @http.route(["/my/time_off/<int:time_off_id>"], type="http", auth="user", website="True")
    def portal_my_time_off(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        values = self._time_off_get_page_view_values(time_off, access_token, **kw)
        values["readonly"] = True
        return request.render("hr_holidays_portal.portal_my_time_off", values)
    
    @http.route(["/my/time_off/<int:time_off_id>/edit"], type="http", auth="user", website="True")
    def portal_my_time_off_edit(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        values = self._time_off_get_page_view_values(time_off, access_token, **kw)
        return request.render("hr_holidays_portal.portal_my_time_off", values)
    
    @http.route(["/my/time_off/<int:time_off_id>/delete"], type="http", auth="user", website="True")
    def portal_my_time_off_delete(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        time_off.unlink()
        return request.redirect("/my/time_off/")
    
    @http.route(["/my/time_off/<int:time_off_id>/draft"], type="http", auth="user", website="True")
    def portal_my_time_off_draft(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        time_off.sudo().action_draft()
        return request.redirect("/my/time_off/" + str(time_off.id))
    
    @http.route(["/my/time_off/<int:time_off_id>/confirm"], type="http", auth="user", website="True")
    def portal_my_time_off_confirm(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        time_off.sudo().action_confirm()
        return request.redirect("/my/time_off/" + str(time_off.id))
    
    @http.route(["/my/time_off/<int:time_off_id>/approve"], type="http", auth="user", website="True")
    def portal_my_time_off_approve(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        time_off.sudo().action_approve()
        return request.redirect("/my/time_off/" + str(time_off.id))
    
    @http.route(["/my/time_off/<int:time_off_id>/refuse"], type="http", auth="user", website="True")
    def portal_my_time_off_refuse(self, time_off_id=None, access_token=None, **kw):
        time_off = request.env["hr.leave"].browse(time_off_id)
        time_off.sudo().action_refuse()
        return request.redirect("/my/time_off/" + str(time_off.id))

    @http.route(["/my/time_off/create"], type="http", auth="user", website="True")
    def portal_my_time_off_create(self, access_token=None, **kw):
        time_off = request.env["hr.leave"]
        values = self._time_off_get_page_view_values(time_off, access_token, **kw)
        values["create_time_off"] = True
        return request.render("hr_holidays_portal.portal_my_time_off", values)
    
    @http.route(["/my/time_off/pullback"], type="http", auth="user", website="True")
    def portal_my_time_off_pullback(self, access_token=None, **kw):
        comment = kw.get("pullback_comment")
        if not comment:
            raise MissingError("Pullback Comment must not be empty. Press back to edit.")
        res = request.env["hr.leave"].browse(int(kw.get("id"))).sudo()
        res.pullback_comment = comment
        res.sudo().action_draft()
        if res.employee_id.user_id:
            res.message_post(
                body=_('Your %s planned on %s has been pulled back' % (res.holiday_status_id.display_name, res.date_from)),
                partner_ids=res.employee_id.user_id.partner_id.ids)
        return request.redirect("/my/time_off/" + str(res.id))

    @http.route(["/my/time_off/save"], type="http", auth="user", website="True")
    def portal_my_time_off_save(self, access_token=None, **kw):
        vals = {
            "holiday_status_id": int(kw.get("holiday_status_id")),
            "name": kw.get("name"),
            "request_date_from": kw.get("request_date_from"),
            "request_date_to": kw.get("request_date_to") or False,
            "request_date_from_period": kw.get("request_date_from_period"),
            "request_hour_from": kw.get("request_hour_from"),
            "request_hour_to": kw.get("request_hour_to"),
            "request_unit_half": kw.get("request_unit_half"),
            "request_unit_hours": kw.get("request_unit_hours"),
        }
        if kw.get("id"): # edit
            res = request.env["hr.leave"].browse(int(kw.get("id"))).sudo()
            res_new = res.new(values=vals, origin=res)
            res_new._onchange_request_parameters()
            res.write(res._convert_to_write(res_new._cache))
        else: # create
            vals["employee_id"] = request.env["hr.employee"].sudo().search([("user_id","=",request.env.uid)], limit=1).id
            res_obj = request.env["hr.leave"].sudo()
            res_new = res_obj.new(vals)
            res_new._onchange_request_parameters()
            res = res_obj.create(res_obj._convert_to_write(res_new._cache))
        return request.redirect("/my/time_off/" + str(res.id))

    @http.route(["/hr_holidays_portal/get_request_unit"], type="json", auth="user")
    def get_time_off_type_request_unit(self, type_id):
        return type_id and request.env["hr.leave.type"].browse(int(type_id)).sudo().request_unit or "day"

    @http.route(["/hr_holidays_portal/get_minimum_date_from"], type="json", auth="user")
    def get_time_off_type_minimum_date_to(self, type_id):
        return type_id and request.env["hr.leave.type"].browse(int(type_id)).sudo()._get_minimum_date_from() or False

    @http.route(["/hr_holidays_portal/get_maximum_date_to"], type="json", auth="user")
    def get_time_off_type_maximum_date_to(self, type_id, date_from):
        return type_id and date_from and request.env["hr.leave.type"].browse(int(type_id)).sudo()._get_maximum_date_to(date_from) or False