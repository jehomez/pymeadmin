#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       sin título.py
#
#       Copyright 2012 Jesús Hómez <jesus@soneview>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#
from modelo import Model

#Model().conectar()
#Model().borrar_tablas_para_inventario()
#~ Model().crear_tablas_para_inventario(2011,12)
#~ Model().crear_tabla_entradas()
venta_id = Model().venta_id_max()
new_venta_id = Model().nuevo_venta_id()
print venta_id
print new_venta_id

