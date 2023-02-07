# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockRequest(models.Model):
    _inherit = "stock.request"

    def _picking_by_product_categ(self):
        self.ensure_one()
        return self._get_picking_type().transfer_by_product_categ

    def _prepare_picking(self):
        """ Inherit this method to create pickings by category if necessary"""
        move_line_by_product_categ = self._split_move_line_by_product_categ()
        # TODO:Here we have chosen the clarity and the decoupling of the modules to the detriment of the performance, we will overwrite each time the value of move_lines because the stock_request module must not be aware of the existence of this split by category
        picking_dicts = []
        for product_categ, move_lines in move_line_by_product_categ.items():
            picking_dict = super(StockRequest, self)._prepare_picking()
            picking_dict.update(
                {'move_lines': [(0, 0, move_line._prepare_move_line(self.location_id.id, self.location_dest_id.id,
                                                                    company=self.location_id.company_id.id)) for
                                move_line in
                                move_lines],
                 'categ_id': product_categ.id})
            picking_dicts.append(picking_dict)
        return picking_dicts

    def _split_move_line_by_product_categ(self):
        move_line_by_product_categ = {}
        for move_line in self.move_line_ids:
            try:
                move_line_by_product_categ[move_line.product_id.categ_id] |= move_line
            except KeyError:
                move_line_by_product_categ.update({move_line.product_id.categ_id: move_line})
        return move_line_by_product_categ
