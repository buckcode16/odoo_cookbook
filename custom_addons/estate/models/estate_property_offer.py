from datetime import date

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    _check_price = models.Constraint(
        "CHECK(price > 0)", "The offer price must be strictly positive."
    )

    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
        ],
        copy=False,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
    )
    property_id = fields.Many2one(
        "estate.property", string="Property", required=True, ondelete="cascade"
    )

    property_type_id = fields.Many2one(
        related="property_id.property_type_id", string="Property Type", store=True
    )

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline", inverse="_inverse_date_deadline"
    )

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            base_date = (
                record.create_date.date() if record.create_date else date.today()
            )
            record.date_deadline = base_date + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            base_date = (
                record.create_date.date() if record.create_date else date.today()
            )
            delta = record.date_deadline - base_date
            record.validity = delta.days

    def action_accept(self):
        for record in self:
            if record.property_id.state in ("offer_accepted", "sold"):
                raise UserError("An offer has already been accepted for this property.")
            record.status = "accepted"

            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = "offer_accepted"
        return True

    def action_reject(self):
        for record in self:
            record.status = "rejected"
            record.property_id.state = "offer_received"
        return True

    @api.model
    def create(self, vals_list):
        for vals in vals_list:
            property_record = self.env["estate.property"].browse(vals["property_id"])

            existing_offers = property_record.property_offer_ids

            if existing_offers:
                max_existing_price = max(existing_offers.mapped("price"))

                if vals["price"] < max_existing_price:
                    raise UserError(
                        "The current offer amount must be greater than or equal to an existing offer."
                    )

            property_record.state = "offer_received"

        return super().create(vals_list)
