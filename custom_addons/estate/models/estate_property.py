from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import date
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'The expected price must be strictly positive.'
    )
    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'The selling price must be positive.'
    )

    _order = "id desc"

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tag")
    property_offer_ids = fields.One2many("estate.property.offer", "property_id", string="Property Offer")

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'), 
            ('south', 'South'), 
            ('east', 'East'), 
            ('west', 'West')
        ]
    )

    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')
        ],
        required=True,
        copy=False,
        default= 'new',
    )

    best_offer = fields.Float(compute="_compute_best_price", string = "Best Offer")
    total_area = fields.Integer(compute="_compute_total_area", string = "Total Area (sqm)")

    @api.depends("property_offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.property_offer_ids:
                record.best_offer = max(record.property_offer_ids.mapped('price'))
            else:
                record.best_offer = 0.0


    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    """
        Add a constraint so that the selling price cannot be lower than 90% of the expected price.
        The selling price is zero until an offer is validated. You will need to fine tune your check to take this into account.
        Always use the float_compare() and float_is_zero() methods from odoo.tools.float_utils when working with floats!
        Ensure the constraint is triggered every time the selling price or the expected price is changed!
    """
    @api.constrains("selling_price", "expected_price")
    def check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2) and \
               float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError("The selling price cannot be lower than 90% of the expected price.")

    def action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled properties cannot be sold")
            record.state = "sold"

        return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be cancelled")
            record.state = "cancelled"

        return True
    

    @api.ondelete(at_uninstall=False)
    def prevent_delete_if_not_new_or_cancelled(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError("Only new and cancelled properties can be deleted.")
            