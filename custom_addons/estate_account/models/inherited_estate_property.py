from odoo import Command, models
from odoo.exceptions import UserError


class InheritedEstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        for record in self:
            partner_id = record.buyer_id.id

            invoice_vals = {
                "partner_id": partner_id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "commission",
                            "quantity": 1,
                            "price_unit": record.selling_price * 0.06,
                        }
                    ),
                    Command.create(
                        {
                            "name": "administrative fees",
                            "quantity": 1,
                            "price_unit": 100,
                        }
                    ),
                ],
            }

            self.env["account.move"].sudo().create(invoice_vals)

        return super().action_sold()
