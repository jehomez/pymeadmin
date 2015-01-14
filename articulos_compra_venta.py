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


class ArticulosCompraVenta:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos_Compra_Venta.glade')
        builder.connect_signals(self)

        self.wArticulosCompraVenta = builder.get_object('wArticulosCompraVenta')
        self.treeArticulos = builder.get_object('treeArticulos')
        self.lista = builder.get_object('lista_articulos')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")

        self.statusbar = builder.get_object('statusbar')

        self.padre = padre
        if padre is None:
            self.padre = self.wArticulosCompraVenta
        else:
            self.padre = self.padre.frm_padre

        self.lista_ordenada_por_id()
        self.mostrar_status()
        self.wArticulosCompraVenta.show()

    def mostrar_status(self):
        registros = Model().contar_registros('articulos')
        buff = "Total de artículos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de artículos registrados: ')
        self.statusbar.push(context_id,buff)

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().articulos_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
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

    def on_tool_cerrar_clicked(self, *args):
        self.on_wArticulosCompraVenta_destroy()

    def on_wArticulosCompraVenta_destroy(self, *args):
        self.wArticulosCompraVenta.destroy()

    def on_treeArticulos_row_activated(self, *args):
        (model, f) = self.treeArticulos.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_articulo_compra_venta(codigo)

class dlgBuscarGrupoArticulo:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Grupo_Articulo.glade")
        builder.connect_signals(self)

        self.dlgBuscarGrupoArticulo = builder.get_object("dlgBuscarGrupoArticulo")
        self.lblValor = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.treeGrupos = builder.get_object("treeGrupos")
        self.lista = builder.get_object('lista_grupos')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.padre = padre
        self.resultado = ''
        self.dlgBuscarGrupoArticulo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().grupos_ordenados_por_id()
        self.cargar_lista(c)

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Nombre')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_btnBuscar_clicked()

    def on_treeGrupos_row_activated(self, *args):
        (model, f) = self.treeGrupos.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_grupo(id)
        self.dlgBuscarGrupoArticulo.destroy()

    def on_btnBuscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_grupo(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_grupo(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            mensajes.info('Debe seleccionar un criterio de búsqueda')
            return

    def on_btnLimpiar_clicked(self, *args):
        self.valor.set_text('')
        self.valor.grab_focus()
        self.lista_ordenada_por_id()

    def on_btnAceptar_clicked(self, *args):
        pass

    def on_btnSalir_clicked(self, *args):
        self.dlgBuscarGrupoArticulo.destroy()

if __name__ == '__main__':
    a = ArticulosCompraVenta()
    a.main()

