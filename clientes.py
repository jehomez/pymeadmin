#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       cliente.py
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
from tipos_clientes import DlgTipoCliente
from zonas import DlgZona

(CODIGO, CLIENTES, TIPO, ZONA, DIRECCION, TELEFONO, CORREO_ELECTRONICO) = range(7)

rDir = os.getcwd()
os.chdir(rDir)


class Clientes:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wClientes.glade')
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
        registros = Model().contar_registros('clientes')
        buff = "Total de clientes registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de clientes registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([CLIENTES, "Clientes", str])
        columnas.append ([TIPO, "Tipo", str])
        columnas.append ([ZONA, "ZONA", str])
        columnas.append ([DIRECCION, "Dirección", str])
        columnas.append ([TELEFONO, "Teléfono", str])
        columnas.append ([CORREO_ELECTRONICO, "Correo Electrónico", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().clientes_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],tupla[f][3],tupla[f][5],tupla[f][6],tupla[f][7],tupla[f][8]])

    def on_agregar_clicked(self,*args):
        dlg = DlgCliente(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.treeClientes.get_selection().get_selected()
        codigo = model.get_value(it,0)
        cliente = model.get_value(it,1)

        if yesno("¿Desea eliminar el cliente <b>%s</b>?\nEsta acción no se puede deshacer\n" % cliente, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_cliente(codigo)
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
            self.resultado = Model().buscar_id_cliente(self.filtro.get_text())
        else:
            self.resultado = Model().buscar_nombre_cliente(self.filtro.get_text())
        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_treeClientes_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.treeClientes,"Lista de Clientes", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_cliente(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, t):
        dlg = DlgCliente(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(t[0][0])
        dlg.codigo.set_editable(False)
        dlg.cliente.set_text(t[0][1])
        dlg.tipo_id.set_text(t[0][2])
        dlg.tipo.set_text(t[0][3])
        dlg.zona_id.set_text(t[0][4])
        dlg.zona.set_text(t[0][5])
        dlg.direccion.set_text(t[0][6])
        dlg.telefono.set_text(t[0][7])
        dlg.email.set_text(t[0][8])
        dlg.cliente.grab_focus()

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgCliente:
    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgCliente.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.cliente = builder.get_object("cliente")
        self.tipo_id = builder.get_object("tipo_id")
        self.tipo = builder.get_object('tipo')
        self.zona_id = builder.get_object("zona_id")
        self.zona = builder.get_object("zona")
        self.direccion = builder.get_object("direccion")
        self.telefono = builder.get_object("telefono")
        self.email = builder.get_object("email")
        self.dialogo.show()

    def cargar_cliente(self, t):
        self.cliente.set_text(t[0][1])
        self.tipo_id.set_text(t[0][2])
        self.tipo.set_text(t[0][3])
        self.zona_id.set_text(t[0][4])
        self.zona.set_text(t[0][5])
        self.direccion.set_text(t[0][6])
        self.telefono.set_text(t[0][7])
        self.email.set_text(t[0][8])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_cliente(codigo)
        if l:
            self.cargar_cliente(l)
        else:
            self.limpiar()

    def on_tipo_id_changed(self, *args):
        codigo = self.tipo_id.get_text()
        l = Model().buscar_id_tipo_cliente(codigo)
        if l:
            self.tipo.set_text(l[0][1])
        else:
            self.tipo.set_text('')

    def on_zona_id_changed(self, *args):
        codigo = self.zona_id.get_text()
        l = Model().buscar_id_zona(codigo)
        if l:
            self.zona.set_text(l[0][1])
        else:
            self.zona.set_text('')

    def on_buscar_tipo_clicked(self,*args):
        dlg = DlgBuscarTipoCliente()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.tipo_id.set_text(dlg.resultado[0][0])
            self.tipo.set_text(dlg.resultado[0][1])

    def on_buscar_zona_clicked(self,*args):
        dlg = DlgBuscarZonaCliente()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.zona_id.set_text(dlg.resultado[0][0])
            self.zona.set_text(dlg.resultado[0][1])

    def on_nuevo_tipo_clicked(self,*args):
        dlg = DlgTipoCliente()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_nueva_zona_clicked(self,*args):
        dlg = DlgZona()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        cliente = self.cliente.get_text()
        tipo_id = self.tipo_id.get_text()
        zona_id = self.zona_id.get_text()
        direccion = self.direccion.get_text()
        telefono = self.telefono.get_text()
        email = self.email.get_text()
        lleno = self.campos_llenos(codigo, cliente, tipo_id, zona_id, telefono)

        if lleno == 1 and not self.editando:
            Model().agregar_cliente(codigo, cliente, tipo_id, zona_id, direccion, telefono, email)
            self.limpiar_todo()

        if lleno == 1 and self.editando:
            Model().modificar_cliente(codigo, cliente, tipo_id, zona_id, direccion, telefono, email)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo, cliente, tipo_id, zona_id, telefono):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo al cliente")
            return

        if cliente == '':
            info("Debe colocar un nombre al cliente")
            return

        if tipo_id == '':
            info("Debe seleccionar un tipo de cliente")
            return

        if zona_id == '':
            info('Debe seleccionar una zona para el cliente')
            return

        if telefono == '':
            info("Debe colocar un telefono al cliente")
            return

        if codigo != '' and cliente !='' and tipo_id != '' and zona_id != '' and telefono != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.cliente.set_text("")
        self.tipo_id.set_text("")
        self.tipo.set_text("")
        self.zona_id.set_text("")
        self.zona.set_text("")
        self.direccion.set_text("")
        self.telefono.set_text("")
        self.email.set_text("")

    def limpiar(self, *args):
        self.cliente.set_text("")
        self.tipo_id.set_text("")
        self.tipo.set_text("")
        self.zona_id.set_text("")
        self.zona.set_text("")
        self.direccion.set_text("")
        self.telefono.set_text("")
        self.email.set_text("")


class DlgBuscarTipoCliente:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Tipo_Cliente_Para_Cliente.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo' )
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
        c = Model().tipos_de_clientes_ordenados_por_id()
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

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_tipo_cliente(id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_tipo_cliente(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_tipo_cliente(self.valor.get_text())
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
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

class DlgBuscarZonaCliente:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Zona_Proveedor.glade")
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
        c = Model().zonas_ordenadas_por_id()
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
        self.on_buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        dialogo = model.get_value(f,0)
        self.resultado = Model().buscar_id_zona(dialogo)
        self.on_dialogo_destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_zona(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_zona(self.valor.get_text())
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
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    p = Clientes()
    p.main()
