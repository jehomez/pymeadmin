#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       bancos.py
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
from mensajes import info
from modelo import Model
from empleados import DlgEmpleado


(ITEM, DESCRIPCION, SALIDAS, SALIDAS_BS ) = range(4)

rDir = os.getcwd()
os.chdir(rDir)

class LibroDeVentas:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wLibro_Compras.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.razon_social = builder.get_object('razon_social')
        self.rif = builder.get_object('rif')
        self.tree = builder.get_object('treeview')
        self.lista = builder.get_object('lista')

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.crear_columnas()
        self.lista_ordenada_por_id()
        self.razon_social.set_text('Panadería y Pastelería La Criollita')
        self.rif.set_text('J-30026088-7')
        self.ventana.show()

    def crear_columnas(self):
        columnas = []
        columnas.append ([ITEM, "Item de inventario", str])
        columnas.append ([DESCRIPCION, "Descripción", str])
        columnas.append ([SALIDAS, "Salidas", str])
        columnas.append ([SALIDAS_BS, "Salidas Bs.", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        listado = Model().libro_de_ventas('2011-01-01', '2011-01-31')
        if listado:
            self.cargar_lista(listado)
        else:
            info('No hay datos que cargar')

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0], tupla[f][1], tupla[f][2], tupla[f][3]])

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Libro de Ventas", self.col_data)
        t.show()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

if __name__ == '__main__':
    z = LibroDeVentas()
    z.main()
