odoo.define("hr_holidays_portal.time_off_portal_form", function(require){
    "use strict";

var publicWidget = require("web.public.widget");
var session = require('web.session');

publicWidget.registry.timeOffPortalForm = publicWidget.Widget.extend({
    selector: ".o_time_off_portal_form",
    events: {
        "change .o_time_off_portal_onchange": "_adaptForm",
        "change #holiday_status_id": "_onchangeHolidayStatus",
        "change #request_date_from": "_onchangeRequestDateFrom",
    },

    start: function () {
        var def = this._super.apply(this, arguments);
        this._adaptForm()
        self = this
        session.rpc("/hr_holidays_portal/get_minimum_date_from", {
            type_id: this.$el.find("#holiday_status_id")[0].value,
        }).then(function (date) {
            var date_from = self.$el.find("#request_date_from")[0]
            var date_to = self.$el.find("#request_date_to")[0]
            if (date) {
                date_from.setAttribute("min", date);
                date_to.setAttribute("min", date);
            }
            else {
                date_from.removeAttribute("min");
                date_to.removeAttribute("min");
            }
        })
        return def
    },

    _adaptForm: function(ev) {
        var self = this
        if (ev && ev.target.id == "request_unit_half" && ev.target.checked) {
            this._setValue("request_unit_hours", false);
        }
        else if (ev && ev.target.id == "request_unit_hours" && ev.target.checked) {
            this._setValue("request_unit_half", false);
        }
        else if (ev && ev.target.id == "holiday_status_id") {
            this._setValue("request_unit_hours", false);
            this._setValue("request_unit_half", false);
        }
        session.rpc("/hr_holidays_portal/get_request_unit", {
            type_id: this.$el.find("#holiday_status_id")[0].value,
        }).then(function (unit) {
            self._hideField("request_date_to", function() {
                if (self._getValue("request_unit_half") == true || self._getValue("request_unit_hours") == true) {return true;}
            })
            self._hideField("request_unit_half", function() {
                if (unit == "day") {return true;}
            })
            self._hideField("request_unit_hours", function() {
                if (unit != "hour") {return true;}
            })
            self._hideField("request_date_from_period", function() {
                if (self._getValue("request_unit_half") == false) {return true;}
            })
            self._hideField("request_hour_from", function() {
                if (self._getValue("request_unit_hours") == false) {return true;}
            })
            self._hideField("request_hour_to", function() {
                if (self._getValue("request_unit_hours") == false) {return true;}
            })
        })
    },

    _onchangeHolidayStatus: function(ev) {
        var self = this
        session.rpc("/hr_holidays_portal/get_minimum_date_from", {
            type_id: this.$el.find("#holiday_status_id")[0].value,
        }).then(function (date) {
            var date_from = self.$el.find("#request_date_from")[0]
            var date_to = self.$el.find("#request_date_to")[0]
            date_from.value = ""
            date_to.value = ""
            if (date) {
                date_from.setAttribute("min", date);
                date_to.setAttribute("min", date);
            }
            else {
                date_from.removeAttribute("min");
                date_to.removeAttribute("min");
            }
        })
    },

    _onchangeRequestDateFrom: function(ev) {
        var self = this
        session.rpc("/hr_holidays_portal/get_maximum_date_to", {
            type_id: this.$el.find("#holiday_status_id")[0].value,
            date_from: this.$el.find("#request_date_from")[0].value,
        }).then(function (date) {
            var date_from_value = self.$el.find("#request_date_from")[0].value
            var date_to = self.$el.find("#request_date_to")[0]
            date_to.value = ""
            if (date_from_value) {
                date_to.setAttribute("min", date_from_value);
            }
            else {
                date_to.removeAttribute("min");
            }
            if (date) {
                date_to.setAttribute("max", date);
            }
            else {
                date_to.removeAttribute("max");
            }
        })
    },

    _hideField: function(id, hide) {
        var input = this.$el.find("#" + id)[0];
        var label = input.labels[0];
        input.parentElement.hidden = hide();
        label.parentElement.hidden = hide();
    },

    _getValue(id) {
        var input = this.$el.find("#" + id)[0]
        var type =  input.type;
        if (type == "checkbox") {
            return input.checked;
        }
        return input.value;
    },

    _setValue(id, value) {
        var input = this.$el.find("#" + id)[0]
        var type =  input.type;
        if (type == "checkbox") {
            input.checked = value;
        }
        else {
            input.value = value;
        }
    },
})
    
});