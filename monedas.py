#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       monedas.py
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
import treetohtml
from mensajes import info, yesno
from modelo import Model

(CODIGO, MONEDAS) = range(2)

class Monedas:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wMonedas.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.statusbar = builder.get_object('statusbar')
        self.resultado = ''
        self.col_data = ''

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.crear_columnas()
        self.on_refrescar_clicked()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('monedas')
        self.statusbar.push(self.statusbar.get_context_id('Total de monedas registradas:'),"Total de monedas registradas: %s" % registros)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([MONEDAS, "Monedas", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().monedas_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_agregar_clicked(self,*args):
        dlg = DlgMoneda(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        moneda = model.get_value(it,1)

        if yesno("¿Desea eliminar la moneda <b>%s</b>?\nEsta acción no se puede deshacer\n" % moneda, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_moneda(codigo)
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
            self.resultado = Model().buscar_id_moneda(self.filtro.get_text())

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_moneda(self.filtro.get_text())

        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
        self.mostrar_status()
        self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Monedas", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_moneda(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self,l):
        dlg = DlgMoneda(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(l[0][0])
        dlg.codigo.set_editable(False)
        dlg.nombre.set_text(l[0][1])
        dlg.plural.set_text(l[0][2])
        dlg.simbolo.set_text(l[0][3])

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()


class DlgMoneda:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgMoneda.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.nombre = builder.get_object("nombre")
        self.plural = builder.get_object("plural")
        self.simbolo = builder.get_object("simbolo")
        self.editando = editando
        self.padre = padre
        self.dialogo.show()

    def cargar_moneda(self, l):
        self.nombre.set_text(l[0][1])
        self.plural.set_text(l[0][2])
        self.simbolo.set_text(l[0][3])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_moneda(codigo)
        if l:
            self.cargar_moneda(l)
        else:
            self.limpiar()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        nombre = self.nombre.get_text()
        plural = self.plural.get_text()
        simbolo = self.simbolo.get_text()
        lleno = self.campos_llenos(codigo, nombre, plural, simbolo)

        if lleno == 1 and not self.editando:
            Model().agregar_moneda(codigo, nombre, plural, simbolo)
            self.limpiar_todo()

        if lleno == 1 and self.editando:
            Model().modificar_moneda(codigo, nombre, plural, simbolo)
            self.on_btnCancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def campos_llenos(self, codigo, nombre, plural, simbolo):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo a la moneda")
            return

        if nombre == '':
            info("Debe colocar un nombre a la moneda")
            return

        if plural == '':
            info("Debe especificar un plural a la moneda")
            return

        if simbolo == '':
            info("Debe colocar un símbolo a la moneda")
            return


        if codigo != '' and nombre!='':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.nombre.set_text("")
        self.plural.set_text("")
        self.simbolo.set_text("")

    def limpiar(self, *args):
        self.nombre.set_text("")
        self.plural.set_text("")
        self.simbolo.set_text("")

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    moneda = Monedas()
    moneda.main()
