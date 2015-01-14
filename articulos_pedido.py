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
import pygtk
import gtk
import os
import treetohtml
from mensajes import info, yesno
from modelo import Model
from comunes import punto_coma, coma_punto, caracter_a_logico, logico_a_caracter, calcular_iva_venta, calcular_precio_neto, calcular_precio_venta, calcular_utilidad

rDir = os.getcwd()
os.chdir(rDir)

class ArticulosPedido:
    def main(self):
        gtk.main()
        return 0

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos_Compra.glade')
        builder.connect_signals(self)

        self.dlgArticulosCompra = builder.get_object('dlgArticulosCompra')
        self.treeArticulos = builder.get_object('treeArticulos')
        self.lista = builder.get_object('lista_articulos')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.resultado = ''

        self.statusbar = builder.get_object('statusbar')

        self.lista_ordenada_por_id()
        self.dlgArticulosCompra.show()

    def mostrar_status(self, filas):
        buff = "Total de artículos como materia prima registrados: %s" % filas
        context_id = self.statusbar.get_context_id('Total de artículos como materia prima registrados: ')
        self.statusbar.push(context_id,buff)

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().solo_materia_prima())

    def cargar_lista(self, tupla):
        self.lista.clear()
        filas = len(tupla)
        self.mostrar_status(filas)
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][16]),punto_coma(tupla[f][11]),punto_coma(tupla[f][15])])

    def on_tool_buscar_clicked(self,*args):
        self.filtro.set_text('')
        criterio = self.criterio.get_visible()
        buscar = self.buscar.get_visible()
        filtro = self.filtro.get_visible()

        if filtro == False and buscar == False and criterio == False:
            self.buscar.set_visible(True)
            self.criterio.set_visible(True)
            self.filtro.set_visible(True)
            self.criterio.grab_focus()
        else:
            self.buscar.set_visible(False)
            self.criterio.set_visible(False)
            self.filtro.set_visible(False)

    def on_criterio_changed(self, *args):
        criterio = self.criterio.get_active()
        if  criterio == 0 or criterio == 1:
            self.filtro.set_text('')
            self.filtro.grab_focus()

    def on_filtro_changed(self, *args):
        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_articulo(self.filtro.get_text())

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_articulo(self.filtro.get_text())

        self.cargar_lista(self.resultado)

    def on_tool_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_btnAceptar_clicked(self, *args):
        pass

    def on_btnSalir_clicked(self, *args):
        self.dlgArticulosCompra.hide()

    def on_treeArticulos_row_activated(self, *args):
        (model, f) = self.treeArticulos.get_selection().get_selected()
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_articulo_pedido(codigo)
        self.dlgArticulosCompra.destroy()

