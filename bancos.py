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
from mensajes import info, yesno
import treetohtml
from modelo import Model
from comunes import logico_a_caracter, caracter_a_logico

(CODIGO, BANCOS) = range(2)

rDir = os.getcwd()
os.chdir(rDir)

class Bancos:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wBancos.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.statusbar = builder.get_object('statusbar')
        self.resultado = ''
        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre
        self.crear_columnas()
        self.on_refrescar_clicked()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('bancos')
        buff = "Total de bancos registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de bancos registradas:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([BANCOS, "Bancos", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().bancos_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_agregar_clicked(self,*args):
        dlg = DlgBanco(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        banco = model.get_value(it,1)

        if yesno("¿Desea eliminar el banco <b>%s</b>?\nEsta acción no se puede deshacer\n" % banco, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_banco(codigo)
           model.remove(it)

        self.on_refrescar_clicked()

    def on_buscar_clicked(self,*args):
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
        self.filtro.set_text('')
        self.filtro.grab_focus()

    def on_filtro_changed(self, *args):
        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_banco(self.filtro.get_text())
        else:
            self.resultado = Model().buscar_nombre_banco(self.filtro.get_text())
        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Bancos", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_banco(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, l):
        dlg = DlgBanco(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(l[0][0])
        dlg.codigo.set_editable(False)
        dlg.banco.set_text(l[0][1])
        dlg.suspendido.set_active(caracter_a_logico(l[0][2]))
        dlg.banco.grab_focus()
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()


class DlgBanco:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgBanco.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.banco = builder.get_object("banco")
        self.suspendido = builder.get_object('suspendido')
        self.dialogo.show()

    def cargar_banco(self, l):
        self.banco.set_text(l[0][1])
        self.suspendido.set_active(caracter_a_logico(l[0][2]))

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_banco(codigo)
        if l:
            self.cargar_banco(l)
        else:
            self.limpiar()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        banco = self.banco.get_text()
        suspendido = logico_a_caracter(self.suspendido.get_active())
        lleno = self.campos_llenos(codigo, banco)

        if lleno == 1 and not self.editando:
            Model().agregar_banco(codigo, banco, suspendido)
            self.limpiar_todo()
            self.codigo.grab_focus()

        if lleno == 1 and self.editando:
            Model().modificar_banco(codigo, banco, suspendido)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo, nombre):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo al banco")
            return

        if nombre == '':
            info("Debe colocar un nombre al banco")
            return

        if codigo != '' and nombre!='':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.banco.set_text("")
        self.suspendido.set_active(False)

    def limpiar(self, *args):
        self.banco.set_text("")
        self.suspendido.set_active(False)


class dlgBuscarBanco:
    def __init__(self, padre= None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Banco.glade")
        builder.connect_signals(self)
        self.dlgBuscarBanco = builder.get_object("dlgBuscarBanco")
        self.etiqueta = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.resultado =''
        self.dlgBuscarBanco.show()

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:

            self.etiqueta.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:

            self.etiqueta.set_text('Nombre')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 2:

            self.etiqueta.set_text('Suspendido')
            self.valor.set_text('si')
            self.on_btnBuscar_clicked()

    def on_btnBuscar_clicked(self, *args):

        if self.criterio.get_active() == 0:

            self.resultado = Model().buscar_id_banco(self.valor.get_text())

        elif self.criterio.get_active() == 1:

            self.resultado = Model().buscar_nombre_banco(self.valor.get_text())

        elif self.criterio.get_active() == 2:

            self.resultado = Model().buscar_bancos_suspendidos()

    def on_btnCancelar_clicked(self, *args):
        self.dlgBuscarBanco.hide()

if __name__ == '__main__':
    z = Bancos()
    z.main()
