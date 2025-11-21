from odoo import models


class InheritedEstateProperty(models.Model):
    _inherit = ["estate.property"]

    def action_sold(self):
        print("test inherited action_sold")
        return super()
