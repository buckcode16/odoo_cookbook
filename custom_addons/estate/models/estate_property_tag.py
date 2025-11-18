from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    _check_name = models.Constraint(
        'UNIQUE(name)',
        'The property tag name must be unique.'
    )
    
    _order = "name"

    name = fields.Char(required=True)
