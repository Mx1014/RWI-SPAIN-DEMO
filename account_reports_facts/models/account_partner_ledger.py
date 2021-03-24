# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountPartnerLedger(models.AbstractModel):
    _inherit = "account.partner.ledger"

    filter_show_facts = False

    def _get_columns_name(self, options):
        res = super(AccountPartnerLedger, self)._get_columns_name(options)
        if options.get("show_facts"):
            res.insert(2, {"name": _('JRNL FID')})
            res.insert(7, {"name": _('Category')})
            res.insert(8, {"name": _('Base'), "class": "number"})
            res.insert(9, {"name": _('Tax'), "class": "number"})
        return res

    @api.model
    def _get_partner_ledger_lines(self, options, line_id=None):
        ''' Get lines for the whole report or for a specific line.
        :param options: The report options.
        :return:        A list of lines, each one represented by a dictionary.
        '''
        lines = []
        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        expanded_partner = line_id and self.env['res.partner'].browse(int(line_id[8:]))
        partners_results = self._do_query(options, expanded_partner=expanded_partner)

        total_initial_balance = total_debit = total_credit = total_balance = 0.0
        for partner, results in partners_results:
            is_unfolded = 'partner_%s' % (partner.id if partner else 0) in options['unfolded_lines']

            # res.partner record line.
            partner_sum = results.get('sum', {})
            partner_init_bal = results.get('initial_balance', {})

            initial_balance = partner_init_bal.get('balance', 0.0)
            debit = partner_sum.get('debit', 0.0)
            credit = partner_sum.get('credit', 0.0)
            balance = initial_balance + partner_sum.get('balance', 0.0)

            lines.append(self._get_report_line_partner(options, partner, initial_balance, debit, credit, balance))

            total_initial_balance += initial_balance
            total_debit += debit
            total_credit += credit
            total_balance += balance

            if unfold_all or is_unfolded:
                cumulated_balance = initial_balance

                # account.move.line record lines.
                amls = results.get('lines', [])

                load_more_remaining = len(amls)
                load_more_counter = self._context.get('print_mode') and load_more_remaining or self.MAX_LINES

                for aml in amls:
                    # Don't show more line than load_more_counter.
                    if load_more_counter == 0:
                        break

                    cumulated_init_balance = cumulated_balance
                    cumulated_balance += aml['balance']
                    lines.extend(self._get_report_line_move_line(options, partner, aml, cumulated_init_balance, cumulated_balance))

                    load_more_remaining -= 1
                    load_more_counter -= 1

                if load_more_remaining > 0:
                    # Load more line.
                    lines.append(self._get_report_line_load_more(
                        options,
                        partner,
                        self.MAX_LINES,
                        load_more_remaining,
                        cumulated_balance,
                    ))

        if not line_id:
            # Report total line.
            lines.append(self._get_report_line_total(
                options,
                total_initial_balance,
                total_debit,
                total_credit,
                total_balance
            ))
        return lines
    
    @api.model
    def _get_report_line_partner(self, options, partner, initial_balance, debit, credit, balance):
        res = super(AccountPartnerLedger, self)._get_report_line_partner(options, partner, initial_balance, debit, credit, balance)
        if options.get("show_facts"):
            res["colspan"] += 4
        return res

    @api.model
    def _get_report_line_move_line(self, options, partner, aml, cumulated_init_balance, cumulated_balance):
        final_res = []
        res = super(AccountPartnerLedger, self)._get_report_line_move_line(options, partner, aml, cumulated_init_balance, cumulated_balance)
        if options.get("show_facts"):
            res["columns"].insert(1, {"name": aml["journal_facts_id"]})
            res["columns"].insert(6, {})
            res["columns"].insert(7, {})
            res["columns"].insert(8, {"name": self.format_value(aml["move_amount_tax"], blank_if_zero=True), "class": "number"})
        final_res.append(res)
        if options.get("show_facts") and aml["move_type"] in ["out_invoice", "out_refund", "out_receipt", "in_invoice", "in_refund", "in_receipt"]:
            move = self.env["account.move"].browse(aml["move_id"])
            for line in move.invoice_line_ids:
                final_res.append({
                    "id": line.id,
                    "name": line.name,
                    "level": 8,
                    "colspan": 7,
                    "parent_id": aml["id"],
                    "columns": [
                        {"name": line.product_id.categ_id.complete_name, "class": "nomargin"},
                        {"name": self.format_value(line.price_subtotal), "class": "number nomargin"},
                        {},
                        {},
                        {},
                        {},
                        {}
                    ]
                })
        return final_res
    
    @api.model
    def _load_more_lines(self, options, line_id, offset, load_more_remaining, progress):
        ''' Get lines for an expanded line using the load more.
        :param options: The report options.
        :return:        A list of lines, each one represented by a dictionary.
        '''
        lines = []

        expanded_partner = line_id and self.env['res.partner'].browse(int(line_id[9:]))

        load_more_counter = self.MAX_LINES

        # Fetch the next batch of lines.
        amls_query, amls_params = self._get_query_amls(options, expanded_partner=expanded_partner, offset=offset, limit=load_more_counter)
        self._cr.execute(amls_query, amls_params)
        for aml in self._cr.dictfetchall():
            # Don't show more line than load_more_counter.
            if load_more_counter == 0:
                break

            cumulated_init_balance = progress
            progress += aml['balance']

            # account.move.line record line.
            lines.extend(self._get_report_line_move_line(options, expanded_partner, aml, cumulated_init_balance, progress))

            offset += 1
            load_more_remaining -= 1
            load_more_counter -= 1

        if load_more_remaining > 0:
            # Load more line.
            lines.append(self._get_report_line_load_more(
                options,
                expanded_partner,
                offset,
                load_more_remaining,
                progress,
            ))
        return lines
    
    @api.model
    def _get_query_amls(self, options, expanded_partner=None, offset=None, limit=None):
        query, where_params = super(AccountPartnerLedger, self)._get_query_amls(options, expanded_partner=expanded_partner, offset=offset, limit=limit)
        query = query.replace("AS full_rec_name", """AS full_rec_name,
            journal.facts_id_int AS journal_facts_id,
            account_move_line__move_id.amount_tax AS move_amount_tax,
            account_move_line__move_id.id AS move_id
        """)
        return query, where_params
    
    @api.model
    def _get_report_line_total(self, options, initial_balance, debit, credit, balance):
        res = super(AccountPartnerLedger, self)._get_report_line_total(options, initial_balance, debit, credit, balance)
        if options.get("show_facts"):
            res["colspan"] += 4
        return res
