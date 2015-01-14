#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       articulos.py
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
import gtk
import os
import treetohtml
from datetime import date
from mensajes import info, yesno
from modelo import Model
from comunes import punto_coma, coma_punto, caracter_a_logico, logico_a_caracter, calcular_iva_venta, calcular_precio_neto, calcular_precio_venta, calcular_utilidad


(CODIGO, ARTICULO, CANTIDAD) = range(3)

rDir = os.getcwd()
os.chdir(rDir)

class TotalDespachado:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None, fecha = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos_Despachados.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.fecha = fecha
        if fecha is None:
            self.fecha = date.today()
        self.padre = padre
        if padre is None:
            self.padre = self.ventana
        else:
            self.padre = self.padre.frm_padre

        self.crear_columnas()
        self.lista_ordenada_por_id()
        self.ventana.show()

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([ARTICULO, "Articulo", str])
        columnas.append ([CANTIDAD, "Cantidad", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        lista = Model().total_diario_de_articulos_despachados(self.fecha)
        if lista:
            self.cargar_lista(lista)
        else:
            info('No se ha despachado ningún artículo hoy')

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][2])])

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Total Diario de Articulos Despachados", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_articulo(codigo)
        self.mostrar_dialogo_con_datos(l)

if __name__ == '__main__':
    TotalDespachado().main()

