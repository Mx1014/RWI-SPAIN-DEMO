# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime, time
from dateutil import parser
from pytz import timezone, UTC

from odoo import fields, http, _, SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        values["purchase_request_count"] = request.env["purchase.order"].search_count(
            ["|",("create_uid","=",request.env.user.id),("is_workflow_stage_user","=",True)])
        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        return values

    def _purchase_request_get_page_view_values(self, purchase_request, access_token, **kwargs):
        values = {
            "purchase_request": purchase_request,
            "vendors": request.env["res.partner"].sudo().search([]),
            "products": request.env["product.product"].sudo().search([("purchase_ok","=",True)]),
            "budgets": request.env.user.purchase_budget_ids,
            "budget_posts": purchase_request.order_line.mapped("budget_post_id"),
        }
        if purchase_request.order_line.mapped("product_id"):
            values["products"] |= purchase_request.order_line.mapped("product_id")
        res = self._get_page_view_values(purchase_request, access_token, values, "my_purchase_requests_history", True, **kwargs)
        if res.get("prev_record"):
            res["prev_record"] = res["prev_record"] and res["prev_record"].replace("/purchase/","/purchase_request/")
        if res.get("next_record"):
            res["next_record"] = res["next_record"] and res["next_record"].replace("/purchase/","/purchase_request/")
        return res

    @http.route(["/my/purchase_request/", "/my/purchase_request/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_purchase_requet(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in="name", **kw):
        values = self._prepare_portal_layout_values()
        purchase_request_obj = request.env["purchase.order"]
        domain = []

        archive_groups = self._get_archive_groups("purchase.order", domain)
        if date_begin and date_end:
            domain += [("create_date",">",date_begin),("create_date","<=",date_end)]
    
        searchbar_sortings = {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "name": {"label": _("Name"), "order": "name"},
        }
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        default_domain = ["|",("create_uid","=",request.env.user.id),("is_workflow_stage_user","=",True)]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": default_domain},
            "rfq": {"label": _("RFQ"), "domain": [("state","in",["draft","sent"])] + default_domain},
            "to_approve": {"label": _("To Approve"), "domain": [("state","in",["to approve"])] + default_domain},
            "confirmed": {"label": _("Confirmed"), "domain": [("state","in",["purchase","done"])] + default_domain},
            "cancel": {"label": _("Cancelled"), "domain": [("state","in",["cancel"])] + default_domain},
        }
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]['domain']

        searchbar_inputs = {
            "name": {"input": "name", "label": _("Search in Order #")},
            "partner_id": {"input": "partner_id", "label": _("Search in Vendor")},
            "workflow_stage_id": {"input": "workflow_stage_id", "label": _("Search in Stage")},
        }
        if search and search_in:
            search_domain = []
            if search_in in "name":
                search_domain = OR([search_domain, [("name","ilike",search)]])
            elif search_in == "partner_id":
                partner_ids = request.env["res.partner"].sudo().search([("name","ilike",search)]).ids
                search_domain = OR([search_domain, [("partner_id","in",partner_ids)]])
            elif search_in == "workflow_stage_id":
                stage_ids = request.env["workflow.stage"].sudo().search([("name","ilike",search)]).ids
                search_domain = OR([search_domain, [("workflow_stage_id","in",stage_ids)]])
            domain += search_domain

        purchase_request_count = purchase_request_obj.search_count(domain)
        pager = portal_pager(
            url="/my/purchase_request",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=purchase_request_count,
            page=page,
            step=self._items_per_page
        )

        purchase_requests = purchase_request_obj.search(domain, order=order, limit=self._items_per_page, offset=pager["offset"])
        request.session["my_purchase_requests_history"] = purchase_requests.ids[:100]

        values.update({
            "date": date_begin,
            "date_end": date_end,
            "purchase_requests": purchase_requests,
            "page_name": "purchase_request",
            "archive_groups": archive_groups,
            "default_url": "/my/purchase_request",
            "pager": pager,
            "searchbar_sortings": searchbar_sortings,
            "sortby": sortby,
            "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
            "filterby": filterby,
            "searchbar_inputs": searchbar_inputs,
            "search_in": search_in,
            "search": search,
        })
        return request.render("purchase_portal.portal_my_purchase_requests", values)
    
    @http.route(["/my/purchase_request/<int:purchase_request_id>"], type="http", auth="user", website="True")
    def portal_my_purchase_request(self, purchase_request_id=None, access_token=None, **kw):
        purchase_request = request.env["purchase.order"].browse(purchase_request_id)
        values = self._purchase_request_get_page_view_values(purchase_request, access_token, **kw)
        values["readonly"] = True
        return request.render("purchase_portal.portal_my_purchase_request", values)
    
    @http.route(["/my/purchase_request/<int:purchase_request_id>/edit"], type="http", auth="user", website="True")
    def portal_my_purchase_request_edit(self, purchase_request_id=None, access_token=None, **kw):
        purchase_request = request.env["purchase.order"].browse(purchase_request_id)
        values = self._purchase_request_get_page_view_values(purchase_request, access_token, **kw)
        return request.render("purchase_portal.portal_my_purchase_request", values)
    
    @http.route(["/my/purchase_request/create"], type="http", auth="user", website="True")
    def portal_my_purchase_request_create(self, access_token=None, **kw):
        purchase_request = request.env["purchase.order"]
        values = self._purchase_request_get_page_view_values(purchase_request, access_token, **kw)
        values["create_purchase_request"] = True
        return request.render("purchase_portal.portal_my_purchase_request", values)
    
    @http.route(["/my/purchase_request/<int:purchase_request_id>/cancel"], type="http", auth="user", website="True")
    def portal_my_purchase_request_cancel(self, purchase_request_id=None, access_token=None, **kw):
        purchase_request = request.env["purchase.order"].browse(purchase_request_id)
        purchase_request.sudo().button_cancel()
        return request.redirect("/my/purchase_request/" + str(purchase_request.id))

    @http.route(["/my/purchase_request/<int:purchase_request_id>/prev_stage"], type="http", auth="user", website="True")
    def portal_my_purchase_request_prev_stage(self, purchase_request_id=None, access_token=None, **kw):
        purchase_request = request.env["purchase.order"].browse(purchase_request_id)
        purchase_request.sudo().action_prev_workflow_stage()
        return request.redirect("/my/purchase_request")

    @http.route(["/my/purchase_request/<int:purchase_request_id>/next_stage"], type="http", auth="user", website="True")
    def portal_my_purchase_request_next_stage(self, purchase_request_id=None, access_token=None, **kw):
        purchase_request = request.env["purchase.order"].browse(purchase_request_id)
        purchase_request.sudo().action_next_workflow_stage()
        return request.redirect("/my/purchase_request/")

    @http.route(["/my/purchase_request/save"], type="http", auth="user", methods=["POST"], website="True")
    def portal_my_purchase_request_save(self, access_token=None, **kw):
        order_line = []
        line_ids = []
        partner_id = int(kw["partner_id"])
        partner = request.env["res.partner"].sudo().browse(partner_id)
        purchase_line_obj = request.env["purchase.order.line"]
        vals = {
            "partner_id": partner_id,
            "budget_id": kw["budget_id"] and int(kw["budget_id"]) or False,
        }

        if not kw.get("id"): # create
            vals["date_order"] = datetime.now()
            res_obj = request.env["purchase.order"].sudo()
            res = res_obj.create(dict(vals))
            vals.pop("partner_id")
        else:
            res = request.env["purchase.order"].browse(int(kw.get("id"))).sudo()

        for key, value  in kw.items():
            if "product_id_" in key:
                number = key.replace("product_id_", "")
                product_id = int(kw.get(key))
                product = request.env["product.product"].sudo().browse(product_id)
                seller = product._select_seller(partner_id=partner)
                budget_post_id = kw.get("budget_post_id_" + number) and int(kw["budget_post_id_" + number]) or False
                product_qty = float(kw.get("product_qty_" + number))
                price_unit = float(kw.get("price_unit_" + number))
                line_id = int(kw.get("line_id_" + number))
                uom_id = product.uom_po_id.id
                date_planned = purchase_line_obj._get_date_planned(seller, res) 
                if line_id:
                    line_ids.append(line_id)
                    line_vals = (1, line_id, {
                        "product_id": product_id,
                        "name": product.display_name,
                        "budget_post_id": budget_post_id,
                        "product_qty": product_qty,
                        "price_unit": price_unit,
                        "product_uom": uom_id,
                        "date_planned": date_planned,
                    })
                else:
                    line_vals = (0, 0, {
                        "product_id": product_id,
                        "name": product.display_name,
                        "budget_post_id": budget_post_id,
                        "product_qty": product_qty,
                        "price_unit": price_unit,
                        "product_uom": uom_id,
                        "date_planned": date_planned,
                    })
                order_line.append(line_vals)
        vals["order_line"] = order_line

        if kw.get("id"): # edit
            deleted_line_ids = set(res.order_line.ids) - set(line_ids)
            for line_id in deleted_line_ids:
                vals["order_line"].append((2, line_id))

        res.write(vals)
        return request.redirect("/my/purchase_request/" + str(res.id))

    @http.route(["/purchase_portal/get_product_details"], type="json", auth="user")
    def portal_my_purchase_request_get_product_details(self, partner_id, product_id, budget_id):
        vals = {
            "price_unit": "-",
            "budget_posts": [],
        }
        if product_id:
            product = request.env["product.product"].sudo().browse(int(product_id))
            partner = partner_id and request.env["res.partner"].sudo().browse(int(partner_id)) or request.env["res.partner"]
            seller = product._select_seller(partner_id=partner)
            taxes_obj = request.env["account.tax"]
            price_unit = taxes_obj._fix_tax_included_price(seller.price, product.supplier_taxes_id, taxes_obj) if seller else 0.0
            vals["price_unit"] = price_unit
            if budget_id:
                account = product.product_tmpl_id.get_product_accounts()["expense"]
                budget = request.env["crossovered.budget"].browse(int(budget_id)).sudo()
                budget_posts = budget.crossovered_budget_line.filtered(lambda x: x.general_budget_id).mapped("general_budget_id")
                budget_posts = budget_posts.filtered(lambda x: account in x.account_ids)
                vals["budget_posts"] = budget_posts.read(["id", "name"])
        return vals
