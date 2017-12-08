#aobject with reference: Product Unit of Measure - product.uom] -*- coding: utf-8 -*-

from odoo import models, fields, api

class truck_transfer(models.Model):
    _name = 'truck.transfer'

    product_ide = fields.Many2one('product.product', 'Producto')
    #uom_id = fields.Many2one('product.template', related="product_ide.uom_id")
    quantity = fields.Float('Cantidad')
    #description = fields.Char()
    uom_id = fields.Integer('Unidad de Medida')
    location_id = fields.Many2one('stock.location', 'Ubicación')
    location_dest_id = fields.Many2one('stock.location', 'Ubicación Destino')

    @api.one
    def action_move(self):
        move_picking = self.env['stock.picking'].create({
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'min_date': self.date,
            'owner_id': self.owner_id.id,
            'picking_type_id': self.stock_type.id,
            })

        move_stock = {
            'product_id' : self.product_ide.id,
            'product_uom': self.product_ide.product_tmpl_id.uom_id.id,
            'price_unit': self.product_ide.product_tmpl_id.standard_price,
            'owner_id': self.owner_id.id,
            'name': "Transferencias Internas",
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'picking_type_id': self.stock_type.id,
            'picking_id': move_picking.id,
            }

        if (self.stock_destination) and (self.stock_origin == False):
            move_stock['product_uom_qty'] = float(self.raw_kilos_dest/1000)

        if (self.stock_origin) and (self.stock_destination == False):
            move_stock['product_uom_qty'] = float(self.raw_kilos/1000)

        create_stock_move= self.env['stock.move'].create(move_stock)
        move_picking.action_confirm()
        move_picking.force_assign()
        if (self.stock_destination) and (self.stock_origin == False):
            move_picking.pack_operation_ids.write({'qty_done':self.raw_kilos_dest/1000})
        if (self.stock_origin) and (self.stock_destination == False):
            move_picking.pack_operation_ids.write({'qty_done':self.raw_kilos/1000})
        move_picking.action_done()

        self.stock_picking_id = self.env['stock.picking'].search([('state', 'in', ['done'])], order='date desc', limit=1)
