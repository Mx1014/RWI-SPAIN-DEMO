# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, exceptions
from odoo.http import request
import datetime
class HRWorkEnrtry(models.Model):
    _inherit = "hr.work.entry"

    def _time_in_checker(self, entry_type_code):

        today_date = datetime.datetime.today()
        clock_in_search = datetime.datetime.combine(today_date, datetime.time.min)
        clock_out_search = datetime.datetime.combine(today_date, datetime.time.max)
        search_args = [
            ('date_start', '>=', clock_in_search.strftime('%Y-%m-%d %H:%M:%S')),
            ('date_stop', '<=', clock_out_search.strftime('%Y-%m-%d %H:%M:%S')),
        ]
        work_entries = self.env['hr.work.entry'].search(search_args)

        employee_with_clock_in_ids = []
        for work_entry in work_entries:
            employee_with_clock_in_ids.append(work_entry.employee_id.id)

        employee_without_clock_in_ids = self.env['hr.employee'].search([('id', 'not in', employee_with_clock_in_ids)])
        OFFSET = 3

        entry_type_record = self.env['hr.work.entry.type'].search([('code', '=', entry_type_code)])
        
        if not entry_type_record or not(entry_type_record.id):
            raise exceptions.ValidationError("Entry type code:\"{0}\" does not exist. ".format(entry_type_code))

        if employee_without_clock_in_ids:
            clock_in_time = datetime.time(hour=8 - OFFSET, minute=0)
            clock_out_time = datetime.time(hour=17 - OFFSET, minute=0)

            clock_in = datetime.datetime.combine(today_date, clock_in_time)
            clock_out = datetime.datetime.combine(today_date, clock_out_time)
            clock_in_delta = clock_out - clock_in
            duration = clock_in_delta.total_seconds() / 3600 #hours
            
            without_contracts = 0
            for index, employee_id in enumerate(employee_without_clock_in_ids):
                contracts = employee_id._get_contracts(today_date, today_date, states=['open', 'pending', 'close'])
                
                if not contracts:
                    without_contracts += 1
                    continue 

                unpaid_leave_create_vals = {
                    'name': '{0}: {1}'.format(entry_type_record.name, employee_id.name),
                    'employee_id': employee_id.id,
                    'date_start': clock_in.strftime('%Y-%m-%d %H:%M:%S'),
                    'date_stop': clock_out.strftime('%Y-%m-%d %H:%M:%S'),
                    'work_entry_type_id': entry_type_record.id,
                    'duration': duration,
                }

                try:
                    create_id = self.env['hr.work.entry'].create(unpaid_leave_create_vals)
                    #print("Created Entry ID: {0} for Employee:{1}".format(create_id, employee_id.id))
                except Exception as e:
                    #print("Error: {0}. Employee ID: {1}.".format(str(e), employee_id.id))
                    #continue to next record if work entry creation fails
                    #example: employee has no contract for the date duration
                    pass
        return True