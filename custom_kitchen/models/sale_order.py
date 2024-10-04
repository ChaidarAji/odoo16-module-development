# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def button_send_kitchen(self):
        pos_categ_ids = self.order_line.mapped('product_id').mapped('pos_categ_id')
        channel_ids = self.env['mail.channel'].search([])
        for pos_categ in pos_categ_ids:
            categ_channel_ids = channel_ids.filtered(lambda x: pos_categ.id in x.pos_categ_ids.ids)
            if len(categ_channel_ids)==0:
                raise ValidationError(_("PoS Category %s belum memiliki channel")%(pos_categ.name))
            order_line_categ = self.order_line.filtered(lambda line: line.product_id.pos_categ_id == pos_categ)
            order_list = []
            for line in order_line_categ:
                order_list.append("%s : %s. Note: %s"%(line.product_id.name, int(line.product_uom_qty), line.name))
            product_list_msg = '<br></br>'.join(order_list)+'</div>'
            user_id = self.env.user.id
            message = ('<div class="o_mail_notification"><strong>New order %s :</strong><br></br>') % (self.name)
            message = message+product_list_msg
            for channel_id in categ_channel_ids:
                channel_id.message_post(author_id=user_id,
                                    body=(message),
                                    message_type='comment',
                                    notify_by_email=False,
                                    subtype_xmlid="mail.mt_comment"
                                    )
        return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'type': 'success',
                    'message': 'Sent to Kitchen Success',
                    'sticky': True,
                    }
                }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    name = fields.Text(
        string="Description",
        store=True, readonly=False, required=True, precompute=True)
