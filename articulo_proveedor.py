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
import treetohtml
from mensajes import info, yesno
from datetime import date
from proveedores import DlgProveedor
from comunes import punto_coma, coma_punto
from modelo import Model

(CODIGO_PROV, PROVEEDOR, COSTO, EXISTENCIA, FECHA) = range(5)

class ArticulosAsociadosAProveedores:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, articulo_id = None, articulo = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos_Proveedores.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        if articulo is None:
            self.ventana.set_title('Proveedores de: ')
        else:
            self.ventana.set_title('Proveedores de:  '+ articulo)
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.statusbar = builder.get_object('statusbar')
        self.articulo_id = articulo_id

        self.crear_columnas()
        self.on_refrescar_clicked(self.articulo_id)
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_proveedores(self.articulo_id)
        buff = "Total de proveedores registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de proveedores registrados:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO_PROV, "Código del proveedor", str])
        columnas.append ([PROVEEDOR, "Proveedor", str])
        columnas.append ([COSTO, "Costo", str])
        columnas.append ([EXISTENCIA, "Existencia", str])
        columnas.append ([FECHA, "Fecha", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,articulo_id):
        self.cargar_lista(Model().buscar_proveedores_asignados(self.articulo_id))

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0], tupla[f][1], punto_coma(tupla[f][2]), punto_coma(tupla[f][3]),tupla[f][4], tupla[f][5]])

    def on_agregar_clicked(self,*args):
        dlg = DlgArticulo_Proveedor(False, self.articulo_id)
        dlg.editando = False
        fecha = date.today()
        dlg.fecha.select_month(fecha.month-1, fecha.year)
        dlg.fecha.select_day(fecha.day)
        dlg.proveedor_id.grab_focus()
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked(self.articulo_id)

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        proveedor_id = model.get_value(it,1)

        if yesno("¿Desea eliminar el proveedor <b>%s</b>?\nEsta acción no se puede deshacer\n" % proveedor_id) == gtk.RESPONSE_YES:
           Model().eliminar_proveedor_de_articulo(proveedor_id, self.articulo_id)
           model.remove(it)

        self.on_refrescar_clicked(self.articulo_id)

    def on_refrescar_clicked(self, articulo_id):
        self.mostrar_status()
        self.lista_ordenada_por_id(articulo_id)

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Proveedores", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_artiprov(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, t):
        dlg = DlgArticulo_Proveedor(False, self.articulo_id)
        dlg.editando = True
        dlg.codigo.set_text(str(t[0][0]))
        dlg.codigo.set_editable(False)
        dlg.proveedor_id.set_text(t[0][1])
        dlg.proveedor.set_text(t[0][2])
        dlg.costo.set_text(punto_coma(t[0][3]))
        dlg.existencia.set_text(punto_coma(t[0][4]))
        fecha = t[0][5]
        dlg.fecha.select_month(fecha.month-1, fecha.year)
        dlg.fecha.select_day(fecha.day)
        dlg.proveedor_id.grab_focus()

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id(self.articulo)

class DlgArticulo_Proveedor:
    def __init__(self, editando = False, articulo = None):
        builder = gtk.Builder()
        builder.add_from_file("dlgArticulo_Proveedor.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object('codigo')
        self.proveedor_id = builder.get_object("proveedor_id")
        self.proveedor = builder.get_object("proveedor")
        self.costo = builder.get_object("costo")
        self.existencia = builder.get_object('existencia')
        self.fecha = builder.get_object('fecha')
        self.articulo = articulo
        self.dialogo.show()

    def cargar_proveedor(self, t):
        self.proveedor.set_text(t[0][1])

    def on_proveedor_id_changed(self, *args):
        codigo = self.proveedor_id.get_text()
        l = Model().buscar_id_proveedor(codigo)
        if l:
            self.cargar_proveedor(l)
        else:
            self.limpiar()

    def on_buscar_proveedor_clicked(self,*args):
        dlg = DlgBuscarProveedorArticulo()
        response = dlg.dialogo.run()
        self.proveedor_id.set_text(dlg.resultado[0][0])
        self.proveedor.set_text(dlg.resultado[0][1])

    def on_nuevo_proveedor_clicked(self,*args):
        dlg = DlgProveedor()
        dlg.editando = False
        response = dlg.DlgProveedor.run()
        if response == gtk.RESPONSE_OK:
            dlg.DlgArticulo.hide()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        proveedor_id = self.proveedor_id.get_text()
        costo = coma_punto(self.costo.get_text())
        fecha = date.today()
        lleno = self.campos_llenos(proveedor_id, costo, fecha)

        if lleno == 1 and not self.editando:
            Model().agregar_proveedor_a_articulo(proveedor_id, costo, fecha, self.articulo)
            self.on_cancelar_clicked()

        if lleno == 1 and self.editando:
            Model().modificar_proveedor_a_articulo(codigo,proveedor_id, costo, fecha)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, proveedor_id, costo, fecha):
        ok = 0

        if proveedor_id == '':
            info("Debe colocar un proveedor")
            return

        if costo == '':
            info("Debe colocar un costo para el artículo")
            return

        if fecha == '':
            info('Debe seleccionar una fecha para el proveedor')
            return

        if proveedor_id !='' and costo != '' and fecha != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text('')
        self.proveedor_id.set_text('')
        self.proveedor.set_text('')
        self.costo.set_text('0,00')

    def limpiar(self, *args):
        self.proveedor_id.set_text("")
        self.proveedor.set_text("")
        self.costo.set_text('0,00')

class DlgBuscarProveedorArticulo:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Proveedor_Articulo.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.lblValor = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.tree = builder.get_object("tree")
        self.lista = builder.get_object('lista')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.padre = padre
        self.resultado = ''
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().proveedores_ordenados_por_id()
        self.cargar_lista(c)

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1], tupla[f][3]])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Tipo de Proveedor')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 2:
            self.lblValor.set_text('Proveedor')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_proveedor(id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_proveedor(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_tipo_proveedor(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 2:
            self.resultado = Model().buscar_nombre_proveedor(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            info('Debe seleccionar un criterio de búsqueda')
            return

    def on_limpiar_clicked(self, *args):
        self.valor.set_text('')
        self.valor.grab_focus()
        self.lista_ordenada_por_id()

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    ArticulosAsociadosAProveedores().main(  )

