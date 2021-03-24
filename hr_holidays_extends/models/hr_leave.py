#-*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HrLeave(models.Model):
    _inherit = "hr.leave"
    
    @api.constrains("date_from", "date_to")
    def _check_request_date_range(self):
        if self.env.user.has_group("hr_holidays.group_hr_holidays_manager"): return
        for leave in self:
            if leave.date_from:
                date_from = fields.Date.context_today(leave, leave.date_from)
                minimum_date_from = leave.holiday_status_id._get_minimum_date_from()
                if minimum_date_from and date_from < minimum_date_from:
                    raise ValidationError("The earliest possible date for requesting this type of time off is %s. " \
                        "To bypass, kindly contact your time off administrator." % minimum_date_from)

                date_to = fields.Date.context_today(leave, leave.date_to)
                maximum_date_to = leave.holiday_status_id._get_maximum_date_to(leave.date_from)
                if maximum_date_to and date_to > maximum_date_to:
                    raise ValidationError("The latest possible date for requesting this type of time off is %s. " \
                        "To bypass, kindly contact your time off administrator." % maximum_date_to)

                restriction = leave.holiday_status_id.consecutive_restriction
                if leave.date_from and leave.date_to and leave.employee_id and restriction:
                    domain = [
                        "!", "|",
                        ("date_to","<",leave.date_from - relativedelta(days=1)),
                        ("date_from",">",leave.date_to + relativedelta(days=1)),
                        ("employee_id","=",leave.employee_id.id),
                        ("state","not in",["cancel","refuse"]),
                        ("id","!=",leave.id),
                    ]
                    message = "This type of time off cannot be taken consecutively with same or other types of time offs."
                    if restriction == "same":
                        domain.append(("holiday_status_id","=",leave.holiday_status_id.id))
                        message = "This type of time off cannot be taken consecutively with the same type of time offs."
                    elif restriction == "other":
                        domain.append(("holiday_status_id","!=",leave.holiday_status_id.id))
                        message = "This type of time off cannot be taken consecutively with other types of time offs."
                    leaves = self.search(domain)
                    if leaves:
                        raise ValidationError(message)