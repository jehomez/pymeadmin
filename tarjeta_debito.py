#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       tarjetas.py
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
from mensajes import info, yesno
import treetohtml
from modelo import Model

(CODIGO, TARJETAS_DE_DEBITO) = range(2)

class TarjetasDeDebito:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wTarjetas_de_Debito.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.statusbar = builder.get_object('statusbar')

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.crear_columnas()
        self.on_refrescar_clicked()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('tarjetas_debito')
        buff = "Total de tarjetas de débito registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de tarjetas de débito registradas:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([TARJETAS_DE_DEBITO, "Tarjetas de Débito", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().tarjetas_de_debito_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_agregar_clicked(self,*args):
        dlg = DlgTarjeta(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        tarjeta = model.get_value(it,1)

        if yesno("¿Desea eliminar la tarjeta de debito <b>%s</b>?\nEsta acción no se puede deshacer\n" % tarjeta, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_tarjeta_de_debito(codigo)
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
            if self.filtro.get_text():
                self.resultado = Model().buscar_id_tarjeta_de_debito(self.filtro.get_text())
                self.cargar_un_despacho(self.resultado)

        elif self.criterio.get_active() == 1:
            if len(self.filtro.get_text()) == 10:
                self.resultado = Model().buscar_nombre_tarjeta_de_debito(self.filtro.get_text())
                self.cargar_lista(self.resultado)


    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Tarjetas de Debito", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        dlg = DlgTarjeta(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(model.get_value(f,0))
        dlg.codigo.set_editable(False)
        dlg.tarjeta.set_text(model.get_value(f,1))
        dlg.tarjeta.grab_focus()
        response = dlg.dlgTarjeta.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()


class DlgTarjeta:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgTarjeta.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.dialogo.set_title('Tarjetas de Débito')
        self.codigo = builder.get_object("codigo")
        self.tarjeta = builder.get_object("tarjeta")
        self.lbltarjeta = builder.get_object("lblTarjeta")
        self.lbltarjeta.set_text('Tarjeta de Débito')
        self.dialogo.show()

    def cargar_tarjeta(self, l):
        self.tarjeta.set_text(l[0][1])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_tarjeta_de_debito(codigo)
        if l:
            self.cargar_tarjeta(l)
        else:
            self.limpiar()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        tarjeta = self.tarjeta.get_text()
        lleno = self.campos_llenos(codigo, tarjeta)

        if lleno == 1 and not self.editando:
            Model().agregar_tarjeta_de_debito(codigo, tarjeta)
            self.limpiar_todo()

        if lleno == 1 and self.editando:
            Model().modificar_tarjeta_de_debito(codigo, tarjeta)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo,nombre):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo a la tarjeta")
            return

        if nombre == '':
            info("Debe colocar un nombre a la tarjeta")
            return

        if codigo != '' and nombre!='':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.tarjeta.set_text("")

    def limpiar(self, *args):
        self.tarjeta.set_text("")

if __name__ == '__main__':
    debito = TarjetasDeDebito()
    debito.main()
