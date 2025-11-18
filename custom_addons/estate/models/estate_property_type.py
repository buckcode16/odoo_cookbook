from odoo import fields, models

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
    
    name = fields.Char(required=True)