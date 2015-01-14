#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       proveedor.py
#
#       Copyright 2010 Jesús Hómez <jesus@jesus-laptop>
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

import pygtk
import gtk
import os
import treetohtml
from comunes import punto_coma, coma_punto
from modelo import Model

(CODIGO, ARTICULO, COSTO, EXISTENCIA) = range(4)

rDir = os.getcwd()
os.chdir(rDir)

class ArticulosPorProveedor:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, proveedor_id = None, proveedor = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos_Por_Proveedor.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.ventana.set_title('Articulos adquiridos a: '+proveedor)
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.statusbar = builder.get_object('statusbar')
        self.proveedor_id = proveedor_id
        self.proveedor = proveedor
        self.col_data = ''

        self.crear_columnas()
        self.lista_ordenada_por_id(self.proveedor_id)
        self.mostrar_status()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_articulos_asociados_a_proveedor(self.proveedor_id)
        buff = "Total de articulos asociados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de articulos asociados:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", str])
        columnas.append ([ARTICULO, "Artículo", str])
        columnas.append ([COSTO, "Costo", str])
        columnas.append ([EXISTENCIA, "Existencia", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self, proveedor_id):
        self.cargar_lista(Model().articulos_asociados_a_proveedor(proveedor_id))

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][2]),punto_coma(tupla[f][3])])

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Articulos por Proveedor", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

if __name__ == '__main__':
    app = ArticulosPorProveedor()
    app.main()
