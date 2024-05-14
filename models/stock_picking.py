# -*- encoding: utf-8 -*-

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    envia_id = fields.Char("Envía ID", copy=False)
    envia_code_envia = fields.Char("Envía Code", copy=False)
    envia_code_cliente = fields.Char("Envía Code Cliente", copy=False)
    envia_pdf = fields.Binary("Envía PDF", copy=False)
    envia_pdf_name = fields.Char('Nombre Envía FEL', default='guia.pdf', size=32)