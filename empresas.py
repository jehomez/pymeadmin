#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       empresas.py
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
from mensajes import info, yesno
from modelo import Model

(CODIGO, EMPRESAS) = range(2)

rDir = os.getcwd()
os.chdir(rDir)

class Empresas:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wEmpresas.glade')
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
        registros = Model().contar_registros('empresas')
        buff = "Total de empresas registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de empresas registradas:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([EMPRESAS, "Empresas", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().empresas_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][2]])

    def on_agregar_clicked(self,*args):
        dlg = DlgEmpresa(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        empresa = model.get_value(it,1)

        if yesno("¿Desea eliminar la empresa <b>%s</b>?\nEsta acción no se puede deshacer\n" % empresa, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_empresa(codigo)
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
            self.resultado = Model().buscar_id_empresa(self.filtro.get_text())

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_empresa(self.filtro.get_text())

        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
        self.mostrar_status()
        self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Empresas", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_empresa(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self,l):
        dlg = DlgEmpresa(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(l[0][0])
        dlg.codigo.set_editable(False)
        dlg.rif.set_text(l[0][1])
        dlg.empresa.set_text(l[0][2])
        dlg.direccion.set_text(l[0][3])
        dlg.telefonos.set_text(l[0][4])
        dlg.fax.set_text(l[0][5])
        dlg.email.set_text(l[0][6])
        dlg.web.set_text(l[0][7])
        dlg.contacto.set_text(l[0][8])

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            self.on_tool_refrescar_clicked()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()


class DlgEmpresa:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgEmpresa.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.rif = builder.get_object("rif")
        self.empresa = builder.get_object("empresa")
        self.direccion = builder.get_object("direccion")
        self.telefonos = builder.get_object("telefonos")
        self.fax = builder.get_object("fax")
        self.email = builder.get_object("email")
        self.web = builder.get_object("web")
        self.contacto = builder.get_object('contacto')
        self.editando = editando
        self.padre = padre
        self.dialogo.show()

    def cargar_empresa(self, l):
        self.rif.set_text(l[0][1])
        self.empresa.set_text(l[0][2])
        self.direccion.set_text(l[0][3])
        self.telefonos.set_text(l[0][4])
        self.fax.set_text(l[0][5])
        self.email.set_text(l[0][6])
        self.web.set_text(l[0][7])
        self.contacto.set_text(l[0][8])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_empresa(codigo)
        if l:
            self.cargar_empresa(l)
        else:
            self.limpiar()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        rif = self.rif.get_text()
        empresa = self.empresa.get_text()
        direccion = self.direccion.get_text()
        telefonos = self.telefonos.get_text()
        fax = self.fax.get_text()
        email = self.email.get_text()
        web = self.web.get_text()
        contacto = self.contacto.get_text()
        lleno = self.campos_llenos(codigo, rif, empresa, direccion, telefonos)

        if lleno == 1 and not self.editando:
            Model().agregar_empresa(codigo, rif, empresa, direccion, telefonos, fax, email, web, contacto)
            self.limpiar_todo()
            self.codigo.grab_focus()

        if lleno == 1 and self.editando:
            Model().modificar_empresa(codigo, rif, empresa, direccion, telefonos, fax, email, web, contacto)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def campos_llenos(self, codigo, rif, empresa, direccion, telefonos):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo a la empresa")
            return

        if rif == '':
            info("Debe colocar un rif a la empresa")
            return

        if empresa == '':
            info("Debe colocar un nombre a la empresa")
            return

        if direccion == '':
            info("Debe colocarle una dirección a la empresa")
            return

        if telefonos == '':
            info("Debe colocar un teléfono a la empresa")
            return

        if codigo != '' and rif!='' and empresa != '' and direccion != '' and telefonos != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text('')
        self.rif.set_text('')
        self.empresa.set_text('')
        self.direccion.set_text('')
        self.telefonos.set_text('')
        self.fax.set_text('')
        self.email.set_text('')
        self.web.set_text('')
        self.contacto.set_text('')

    def limpiar(self, *args):
        self.rif.set_text('')
        self.empresa.set_text('')
        self.direccion.set_text('')
        self.telefonos.set_text('')
        self.fax.set_text('')
        self.email.set_text('')
        self.web.set_text('')
        self.contacto.set_text('')

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    e = Empresas()
    e.main()
