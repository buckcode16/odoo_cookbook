from odoo import fields, models
from datetime import date
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.users", string="Buyer")
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    property_tag_ids = fields.Many2many("estate.property.tag", string="Property Tag")

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
            ('New', 'New'),
            ('Offer Received', 'Offer Received'),
            ('Offer Accepted', 'Offer Accepted'),
            ('Sold', 'Sold'),
            ('Cancelled', 'Cancelled')
        ],
        required=True,
        copy=False,
        default='New'
    )