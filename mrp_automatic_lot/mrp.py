# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv

class mrp_production(osv.osv):
    _inherit = "mrp.production"

    def action_confirm(self, cr, uid, ids, context=None):
        res= super(mrp_production,self).action_confirm(cr, uid, ids, context=context)
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, ids[0], context=context)
        if not production.product_id.transfer_lot:
            for produce_product in production.move_created_ids:
                prod_lot_id = stock_mov_obj._create_lot(cr, uid, [produce_product.id], produce_product.product_id.id, prefix=False)
                if production.product_id.transfer_lot_date:
                    lot_obj = self.pool.get('stock.production.lot')
                    lot = None
                    for consume_product in production.move_lines:
                        if consume_product.prodlot_id:
                            lot = consume_product.prodlot_id

                            break
                    if lot:

                        values = {
                            'life_date': lot.life_date,
                            'use_date': lot.use_date,
                        }

                        lot_obj.write(cr, uid, prod_lot_id, values, context)

                produce_product.write({'prodlot_id': prod_lot_id})
        else:
            prod_lot_id = None
            for consume_product in production.move_lines:
                if consume_product.prodlot_id:
                    lot_obj = self.pool.get('stock.production.lot')
                    domain = [
                        ('product_id', '=', production.product_id.id),
                        ('name', '=', consume_product.prodlot_id.name),
                        ('language', '=', consume_product.prodlot_id.language.id),
                    ]
                    exist_lot_ids = lot_obj.search(cr, uid, domain, context=context)
                    if exist_lot_ids:
                        prod_lot_id = exist_lot_ids[0]
                    else:
                        prod_lot_id = lot_obj.copy(cr, uid, consume_product.prodlot_id.id,
                                                   {'product_id': production.product_id.id,
                                                    'name': consume_product.prodlot_id.name,
                                                    'language': consume_product.prodlot_id.language.id})
            if prod_lot_id:
                for produce_product in production.move_created_ids:
                    produce_product.write({'prodlot_id': prod_lot_id})

        return res

    # def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
    #     stock_mov_obj = self.pool.get('stock.move')
    #     production = self.browse(cr, uid, production_id, context=context)
    #     if production_mode == 'consume_produce':
    #         for produce_product in production.move_created_ids:
    #             prod_lot_id = stock_mov_obj._create_lot(cr, uid, [produce_product.id], produce_product.product_id.id, prefix=False)
    #             produce_product.write({'prodlot_id': prod_lot_id})
    #
    #     return super(mrp_production,self).action_produce(cr, uid, production_id, production_qty, production_mode, context=context)


mrp_production()