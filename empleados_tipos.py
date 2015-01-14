#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       tipos.py
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
from mensajes import info, yesno
import treetohtml
from modelo import Model

(CODIGO, TIPOS) = range(2)

rDir = os.getcwd()
os.chdir(rDir)


class TiposEmpleados:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wTipos_Empleados.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista_tipos')
        self.tvcolumn0 = builder.get_object('tvcolumn0')
        self.tvcolumn1 = builder.get_object('tvcolumn1')
        self.statusbar = builder.get_object('statusbar')

        # Se hace buscable por columna
        self.tree.set_search_column(0)
        self.tree.set_search_column(1)

        # Se permite ordenar por columna
        self.tvcolumn0.set_sort_column_id(0)
        self.tvcolumn1.set_sort_column_id(1)

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.crear_columnas()
        self.on_refrescar_clicked()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('empleados_tipos')
        buff = "Total de tipos de empleados registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de tipos de empleados registrados:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([TIPOS, "Tipos", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().tipos_de_empleados_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_agregar_clicked(self,*args):
        dlg = DlgTipoEmpleado(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        tipo = model.get_value(it,1)

        if yesno("¿Desea eliminar el tipo de empleado: <b>%s</b>?\nEsta acción no se puede deshacer\n" % tipo, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_tipo_empleado(codigo)
           model.remove(it)

        self.on_tool_refrescar_clicked()

    def on_buscar_clicked(self,*args):
        dlg = DlgBuscarTipoEmpleado(self.frm_padre)
        response = dlg.dlgBuscarTipoEmpleado.run()
        if response == gtk.RESPONSE_OK:
            tipo = dlg.resultado
            dlg.dlgBuscarTipoEmpleado.hide()
            self.cargar_lista(tipo)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.treeTipos,"Lista de Tipos de Empleados", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        dlg = DlgTipoEmpleado(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(model.get_value(f,0))
        dlg.codigo.set_editable(False)
        dlg.tipo.set_text(model.get_value(f,1))
        dlg.tipo.grab_focus()
        response = dlg.dlgTipoEmpleado.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgTipoEmpleado:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgTipo_Empleado.glade")
        builder.connect_signals(self)
        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.tipo = builder.get_object("tipo")
        self.dialogo.show()

    def cargar_tipo(self, l):
        self.tipo.set_text(l[0][1])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_tipo_empleado(codigo)
        if l:
            self.cargar_tipo(l)
        else:
            self.limpiar()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        tipo = self.tipo.get_text()
        lleno = self.campos_llenos(codigo, tipo)

        if lleno == 1 and not self.editando:
            Model().agregar_tipo_empleado(codigo, tipo)
            self.limpiar_todo()

        if lleno == 1 and self.editando:
            Model().modificar_tipo_empleado(codigo, tipo)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo, tipo):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo al tipo de empleado")
            return

        if tipo == '':
            info("Debe colocar un valor al tipo de empleado")
            return

        if codigo != '' and tipo !='':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.tipo.set_text("")

    def limpiar(self, *args):
        self.tipo.set_text("")

class dlgBuscarTipoEmpleado:
    def __init__(self, padre= None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Tipo_Empleado.glade")
        builder.connect_signals(self)
        self.dlgBuscarTipoEmpleado = builder.get_object("dlgBuscarTipoEmpleado")
        self.etiqueta = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.resultado =''
        self.dlgBuscarTipoEmpleado.show()

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:

            self.etiqueta.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:

            self.etiqueta.set_text('Tipo')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:

            self.resultado = Model().buscar_id_tipo_empleado(self.valor.get_text())

        elif self.criterio.get_active() == 1:

            self.resultado = Model().buscar_tipo_empleado(self.valor.get_text())

    def on_cancelar_clicked(self, *args):
        self.dlgBuscarTipoEmpleado.hide()

if __name__ == '__main__':
    t = TiposEmpleados()
    t.main()
