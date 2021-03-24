odoo.define("purchase_portal.purchase_request_portal_form", function(require){
    "use strict";
    
    var publicWidget = require("web.public.widget");
    var session = require('web.session');
    
    publicWidget.registry.tpurchaseRequestPortalForm = publicWidget.Widget.extend({
        selector: ".o_purchase_request_portal_form",
        events: {
            "click .o_purchase_request_portal_form_add_line": "_addLine",
            "click .o_purchase_request_portal_form_remove_line": "_removeLine",
            "change .o_purchase_request_portal_form_product_id": "_onchangeProduct",
            "change .o_purchase_request_portal_form_product_qty": "_onchangeQuantity",
            "change .o_purchase_request_portal_form_budget_id": "_onchangeBudget",
        },
    
        start: function () {
            var def = this._super.apply(this, arguments);
            return def
        },
    
        _addLine: function(ev) {
            var orig = ev.target.previousElementSibling.lastElementChild
            var orig_number = parseInt(orig.id.replace("line_",""))
            var new_number = orig_number + 1
    
            var line = orig.cloneNode(true);
            line.id = line.name = "line_" + new_number
            var line_id = line.querySelector("#line_id_" + orig_number)
            line_id.id = line_id.name = "line_id_" + new_number
            line_id.value = 0
            var product_id = line.querySelector("#product_id_" + orig_number)
            product_id.id = product_id.name = "product_id_" + new_number
            product_id.value = ""
            var budget_post_id = line.querySelector("#budget_post_id_" + orig_number)
            budget_post_id.id = budget_post_id.name = "budget_post_id_" + new_number
            budget_post_id.value = ""
            budget_post_id.innerHTML = "<option value>--- Pos. ---</option>"
            var product_qty = line.querySelector("#product_qty_" + orig_number)
            product_qty.id = product_qty.name = "product_qty_" + new_number
            product_qty.value = ""
            var price_unit_text = line.querySelector("#price_unit_text_" + orig_number)
            price_unit_text.id = price_unit_text.name = "price_unit_text_" + new_number
            price_unit_text.innerHTML = "-"
            var price_unit = line.querySelector("#price_unit_" + orig_number)
            price_unit.id = price_unit.name = "price_unit_" + new_number
            price_unit.value = "-"
            var price_subtotal = line.querySelector("#price_subtotal_" + orig_number)
            price_subtotal.id = price_subtotal.name = "price_subtotal_" + new_number
            price_subtotal.innerHTML = "-"
            ev.target.previousElementSibling.append(line)
        },
    
        _removeLine: function(ev) {
            if (ev.target.parentElement.parentElement.parentElement.childElementCount > 1) {
                ev.target.parentElement.parentElement.remove()
            }
        },
    
        _onchangeProduct: function(ev) {
            var self = this
            self.active_product_id = ev.target.name.replace("product_id_", "")
            session.rpc("/purchase_portal/get_product_details", {
                partner_id: this.$el.find("#partner_id")[0].value,
                product_id: ev.target.value,
                budget_id: this.$el.find("#budget_id")[0].value,
            }).then(function (details) {
                self.$el.find("#price_unit_text_" + self.active_product_id)[0].innerHTML = details["price_unit"]
                self.$el.find("#price_unit_" + self.active_product_id)[0].value = details["price_unit"]
                self._updateSubtotal(self.active_product_id)

                var options = "<option value>--- Pos. ---</option>"
                _.forEach(details["budget_posts"], function(post) {
                    options += '<option value="' + post["id"] + '">' + post["name"] + '</option>'
                })
                self.$el.find("#budget_post_id_" + self.active_product_id)[0].value = ""
                self.$el.find("#budget_post_id_" + self.active_product_id)[0].innerHTML = options
            })
        },
    
        _onchangeQuantity: function(ev) {
            this._updateSubtotal(ev.target.name.replace("product_qty_", ""))
        },

        _onchangeBudget: function(ev) {
            var self = this
            var products = self.$el.find(".o_purchase_request_portal_form_product_id")
            _.forEach(products, function(product) {
                self.active_product_id = product.name.replace("product_id_", "")
                session.rpc("/purchase_portal/get_product_details", {
                    partner_id: self.$el.find("#partner_id")[0].value,
                    product_id: product.value,
                    budget_id: self.$el.find("#budget_id")[0].value,
                }).then(function (details) {
                    var options = "<option value>--- Pos. ---</option>"
                    _.forEach(details["budget_posts"], function(post) {
                        options += '<option value="' + post["id"] + '">' + post["name"] + '</option>'
                    })
                    self.$el.find("#budget_post_id_" + self.active_product_id)[0].value = ""
                    self.$el.find("#budget_post_id_" + self.active_product_id)[0].innerHTML = options
                })
            })
        },
    
        _updateSubtotal: function(product_id) {
            var quantity = parseFloat(this.$el.find("#product_qty_" + product_id)[0].value)
            var price_subtotal = parseFloat(this.$el.find("#price_unit_text_" + product_id)[0].innerHTML) * quantity
            if (Number.isNaN(price_subtotal)) {
                price_subtotal = "-"
            }
            this.$el.find("#price_subtotal_" + product_id)[0].innerHTML = price_subtotal
        },
    })
});