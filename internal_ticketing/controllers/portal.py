# -*- coding: utf-8 -*-

from collections import OrderedDict

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR, AND

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values["internal_ticket_team_ids"] = request.env["helpdesk.team"].sudo().search([
            "|", ("company_id","=",False),
                 ("company_id","=",request.env.user.company_id.id),
        ]).sorted("name")
        values["internal_ticket_count"] = request.env["helpdesk.ticket"].sudo().search_count([("partner_id","=",request.env.user.partner_id.id)])
        values["user"] = request.env.user
        return values

    def _internal_ticket_get_page_view_values(self, internal_ticket, access_token, **kwargs):
        values = {
            "internal_ticket": internal_ticket,
            "user": request.env.user,
            "internal_ticket_team_ids": request.env["helpdesk.team"].sudo().search([
                "|", ("company_id","=",False),
                     ("company_id","=",request.env.user.company_id.id),
            ]).sorted("name"),
        }
        res = self._get_page_view_values(internal_ticket, access_token, values, "my_internal_tickets_history", True, **kwargs)
        if res.get("prev_record"):
            res["prev_record"] = res["prev_record"] and res["prev_record"].replace("/ticket/","/internal_ticket/")
        if res.get("next_record"):
            res["next_record"] = res["next_record"] and res["next_record"].replace("/ticket/","/internal_ticket/")
        return res

    @http.route(["/my/internal_ticket/", "/my/internal_ticket/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_internal_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in="id", **kw):
        values = self._prepare_portal_layout_values()
        ticket_obj = request.env["helpdesk.ticket"]
        domain = []

        archive_groups = self._get_archive_groups("helpdesk.ticket", domain)
        if date_begin and date_end:
            domain += [("create_date",">",date_begin),("create_date","<=",date_end)]
        searchbar_sortings = {
            "newest": {"label": _("Newest"), "order": "create_date desc"},
            "oldest": {"label": _("Oldest"), "order": "create_date asc"},
        }
        if not sortby:
            sortby = "newest"
        order = searchbar_sortings[sortby]["order"]

        default_domain = [("partner_id","=",request.env.user.partner_id.id)]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": default_domain},
            "open": {"label": _("Open"), "domain": ['&',("stage_id.is_close","=",False),('closed_by_partner','=',False)] + default_domain},
            "closed": {"label": _("Closed"), "domain": ['|',("stage_id.is_close","=",True),('closed_by_partner','=',True)] + default_domain},
        }
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]['domain']

        searchbar_inputs = {
            "id": {"input": "id", "label": _("Search in Ticket #")},
            "name": {"input": "name", "label": _("Search in Subject")},
            "team_id": {"input": "team_id", "label": _("Search in Type")},
        }
        if search and search_in:
            search_domain = []
            if search_in == "id":
                search_domain = OR([search_domain, [("id","ilike",search)]])
            if search_in == "name":
                search_domain = OR([search_domain, [("name","ilike",search)]])
            elif search_in == "team_id":
                search_domain = OR([search_domain, [("team_id","ilike",search)]])
            domain += search_domain

        internal_ticket_count = ticket_obj.sudo().search_count(domain)
        pager = portal_pager(
            url="/my/internal_ticket",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=internal_ticket_count,
            page=page,
            step=self._items_per_page
        )

        internal_tickets = ticket_obj.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])
        request.session["my_internal_tickets_history"] = internal_tickets.ids[:100]

        values.update({
            "date": date_begin,
            "date_end": date_end,
            "internal_tickets": internal_tickets,
            "page_name": "internal_ticket",
            "archive_groups": archive_groups,
            "default_url": "/my/internal_ticket",
            "pager": pager,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
            "filterby": filterby,
            "searchbar_inputs": searchbar_inputs,
            "search_in": search_in,
            "search": search,
        })
        return request.render("internal_ticketing.portal_my_internal_tickets", values)

    @http.route(["/my/internal_ticket/<int:ticket_id>"], type="http", auth="user", website="True")
    def portal_my_internal_ticket(self, ticket_id=None, access_token=None, **kw):
        internal_ticket = request.env["helpdesk.ticket"].browse(ticket_id)
        values = self._internal_ticket_get_page_view_values(internal_ticket, access_token, **kw)
        return request.render("internal_ticketing.portal_my_internal_ticket", values)

    @http.route(["/my/internal_ticket/create"], type="http", auth="user", website="True")
    def portal_my_internal_ticket_create(self, access_token=None, **kw):
        internal_ticket = request.env["helpdesk.ticket"]
        values = self._internal_ticket_get_page_view_values(internal_ticket, access_token, **kw)
        values["create_internal_ticket"] = True
        return request.render("internal_ticketing.portal_my_internal_ticket", values)
    
    @http.route(["/my/internal_ticket/save"], type="http", auth="user", methods=["POST"], website="True")
    def portal_my_internal_ticket_save(self, access_token=None, **kw):
        vals = dict(kw)
        vals["team_id"] = int(kw.get("team_id"))
        vals["partner_id"] = request.env.user.partner_id.id
        res = request.env["helpdesk.ticket"].sudo().create(vals)
        return request.redirect("/my/internal_ticket/" + str(res.id))

    @http.route(["/my/internal_ticket/<int:ticket_id>/close"], type="http", auth="user", website="True")
    def portal_my_internal_ticket_close(self, ticket_id=None, access_token=None, **kw):
        internal_ticket = request.env["helpdesk.ticket"].browse(ticket_id).sudo()
        values = self._internal_ticket_get_page_view_values(internal_ticket, access_token, **kw)
        if not internal_ticket.closed_by_partner:
            closing_stage = internal_ticket.team_id._get_closing_stage()
            if internal_ticket.stage_id != closing_stage:
                internal_ticket.write({"stage_id": closing_stage[0].id, "closed_by_partner": True})
            else:
                internal_ticket.write({"closed_by_partner": True})
        return request.redirect("/my/internal_ticket/" + str(ticket_id))