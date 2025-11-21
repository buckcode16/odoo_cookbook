from odoo import models
from odoo.exceptions import UserError


class InheritedEstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        for record in self:
            partner_id = record.buyer_id.id

            invoice_vals = {"partner_id": partner_id, "move_type": "out_invoice"}

            self.env["account.move"].sudo().create(invoice_vals)

        return super().action_sold()
