# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockRequest(models.Model):
    _inherit = "stock.request"

    transfer_by_product_categ = fields.Boolean(compute='_compute_transfer_by_product_categ')
    categ_id = fields.Many2one('product.category', 'Product Category',states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},)


    @api.onchange('categ_id')
    def on_change_categ_id(self):
        self.move_line_ids = False

    @api.depends('location_id')
    def _compute_transfer_by_product_categ(self):
        # TODO: we have to check if we should select the appropriate internal type here relying on the warehouse
        internal_type = self.env.ref('stock.picking_type_internal')
        for each in self:
            each.transfer_by_product_categ = internal_type.transfer_by_product_categ


    def _prepare_picking(self):
        res = super(StockRequest,self)._prepare_picking()
        if self.transfer_by_product_categ and self.categ_id:
            res.update({'categ_id':self.categ_id.id})
        return res

class StockRequestLine(models.Model):
    _inherit = "stock.request.line"

    transfer_by_product_categ = fields.Boolean(related='request_id.transfer_by_product_categ')

    @api.onchange('transfer_by_product_categ')
    def _onchange_transfer_by_product_categ(self):
        if self.transfer_by_product_categ and self.request_id.categ_id:
            return {'domain':{'product_id':[('categ_id','=',self.request_id.categ_id.id)]}}
        elif self.transfer_by_product_categ and not self.request_id.categ_id:
            return {'domain':{'product_id':[('id','=',-1)]}}