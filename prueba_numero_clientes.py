#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       vendedor.py
#
#       Copyright 2010 Jesús Hómez <jesus@jesus-laptop>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY, WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import gtk
import treetohtml
from mensajes import info
from modelo import Model
from datetime import date, datetime
from articulos_venta import ArticulosVenta
from comunes import punto_coma, coma_punto, es_ve
from clientes import DlgCliente


class NumeroCliente:

    def main(self):
        gtk.main()
        return 0

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('wLista_Numeros.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.tree = builder.get_object("tree")
        self.lista = builder.get_object('lista')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.resultado = ''
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().nro_clientes_ordenados()
        if c:
            self.cargar_lista(c)
        else:
            info('No existen clientes con numero asignado')

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        self.resultado = Model().buscar_nro_cliente(model.get_value(f,0))
        if self.resultado:
            self.dialogo.destroy()

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    NumeroCliente().main()
