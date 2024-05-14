# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round

import requests
import logging

class DeliverCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('envia', 'Envía')
    ], ondelete={'envia': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})
    envia_usuario = fields.Char('Usuario Envía', groups='base.group_system')
    envia_clave = fields.Char('Clave Envía', groups='base.group_system')
    envia_tipo_envio = fields.Selection([
        ('1', 'Envio Normal')
        ], string='Tipo de Envio', default='1')

    def envia_rate_shipment(self, order):
        return {'success': True, 'price': 0.00, 'error_message': '', 'warning_message': ''}

    def envia_send_shipping(self, pickings):
        shippings = []

        headers = {
            'Content-Type': 'application/json',
        }
        data = {
            'usuario': self.sudo().envia_usuario,
            'password': self.sudo().envia_clave,
        }
        logging.warning(headers)
        logging.warning(data)
        r = requests.post('https://enviacounter.azurewebsites.net/api/login-auto', json=data, headers=headers)
        logging.warning(r.text)
        res = r.json()
        token = res['token']

        if not token:
            return { 'exact_price': 0.00, 'tracking_number': '' }
        
        for p in pickings:
            headers = {
                'Content-Type': 'application/json',
                'x-authorization': token,
            }
            data = {
                'code': p.name,
                'tipoP': self.sudo().envia_tipo_envio,
                'nombreDestinatario': p.partner_id.name,
                'direccionDestinatario': p.partner_id.street or '',
                'telefonoDestinatario': p.partner_id.phone or '',
                'descripcion': p.note or '',
                'direccionMunicipio': p.partner_id.city,
                'direccionZona': p.partner_id.zip,
                'correo': p.partner_id.email,
            }
            logging.warning(headers)
            logging.warning(data)
            r = requests.post('https://enviacounter.azurewebsites.net/api/insert-auto', json=data, headers=headers)
            logging.warning(r.text)
            res = r.json()

            p.envia_id = res['id']
            p.envia_code_envia = res['codeEnvia']
            p.envia_code_cliente = res['codeCliente']
            p.envia_pdf = res['guiaPDF']
            
            shippings = shippings + [{ 'exact_price': 0.00, 'tracking_number': p.envia_code_envia }]

        return shippings