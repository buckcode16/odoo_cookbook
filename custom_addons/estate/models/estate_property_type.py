from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The property type name must be unique.'
    )

    _order = "sequence, name"

    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    sequence = fields.Integer('Sequence', default=1, help="Used to property types.")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id", string="Property offers")
    offer_count = fields.Integer(compute="_compute_offer_count", string = "Offer counts")
    
    name = fields.Char(required=True)

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)