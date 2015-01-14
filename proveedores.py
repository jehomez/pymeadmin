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
from modelo import Model
from tipos_proveedores import DlgTipoProveedor
from zonas import DlgZona
from bancos import DlgBanco
from articulos_por_proveedor import ArticulosPorProveedor

(CODIGO, PROVEEDORES, TIPO, ZONA, DIRECCION, TELEFONO, CORREO_ELECTRONICO) = range(7)

class Proveedores:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wProveedores.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.statusbar = builder.get_object('statusbar')
        self.padre = padre
        self.col_data = ''
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.crear_columnas()
        self.on_refrescar_clicked()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('proveedores')
        buff = "Total de proveedores registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de proveedores registrados:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([PROVEEDORES, "Proveedores", str])
        columnas.append ([TIPO, "Tipo", str])
        columnas.append ([ZONA, "Zona", str])
        columnas.append ([DIRECCION, "Dirección", str])
        columnas.append ([TELEFONO, "Teléfono", str])
        columnas.append ([CORREO_ELECTRONICO, "Correo Electrónico", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().proveedores_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],tupla[f][3],tupla[f][5],tupla[f][6],tupla[f][7],tupla[f][8]])

    def on_agregar_clicked(self,*args):
        dlg = DlgProveedor(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        proveedor = model.get_value(it,1)

        if yesno("¿Desea eliminar el proveedor <b>%s</b>?\nEsta acción no se puede deshacer\n" % proveedor, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_proveedor(codigo)
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
            self.resultado = Model().buscar_id_proveedor(self.filtro.get_text())
        else:
            self.resultado = Model().buscar_nombre_proveedor(self.filtro.get_text())
        self.cargar_lista(self.resultado)


    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

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
        l = Model().buscar_id_proveedor(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, t):
        dlg = DlgProveedor(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(t[0][0])
        dlg.codigo.set_editable(False)
        dlg.proveedor.set_text(t[0][1])
        dlg.tipo_id.set_text(t[0][2])
        dlg.tipo.set_text(t[0][3])
        dlg.zona_id.set_text(t[0][4])
        dlg.zona.set_text(t[0][5])
        dlg.direccion.set_text(t[0][6])
        dlg.telefono.set_text(t[0][7])
        dlg.email.set_text(t[0][8])
        dlg.dias.set_text(str(t[0][9]))
        dlg.banco_id.set_text(t[0][10])
        dlg.banco.set_text(t[0][11])
        dlg.titular.set_text(t[0][12])
        dlg.cuenta.set_text(t[0][13])
        dlg.tipo_cuenta.set_text(t[0][14])
        dlg.proveedor.grab_focus()

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgProveedor:
    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgProveedor.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.proveedor = builder.get_object("proveedor")
        self.tipo_id = builder.get_object("tipo_id")
        self.tipo = builder.get_object('tipo')
        self.zona_id = builder.get_object("zona_id")
        self.zona = builder.get_object("zona")
        self.direccion = builder.get_object("direccion")
        self.telefono = builder.get_object("telefono")
        self.email = builder.get_object("email")
        self.dias = builder.get_object('dias')
        self.banco_id = builder.get_object('banco_id')
        self.banco = builder.get_object('banco')
        self.titular = builder.get_object('titular')
        self.cuenta = builder.get_object('cuenta')
        self.tipo_cuenta = builder.get_object('tipo_cuenta')
        self.editando = editando

        self.dialogo.show()

    def cargar_proveedor(self, t):
        self.proveedor.set_text(t[0][1])
        self.tipo_id.set_text(t[0][2])
        self.tipo.set_text(t[0][3])
        self.zona_id.set_text(t[0][4])
        self.zona.set_text(t[0][5])
        self.direccion.set_text(t[0][6])
        self.telefono.set_text(t[0][7])
        self.email.set_text(t[0][8])
        self.dias.set_text(str(t[0][9]))
        self.banco_id.set_text(t[0][10])
        self.banco.set_text(t[0][11])
        self.titular.set_text(t[0][12])
        self.cuenta.set_text(t[0][13])
        self.tipo_cuenta.set_text(t[0][14])

    def on_articulos_clicked(self,*args):
        proveedor_id = self.codigo.get_text()
        proveedor = self.proveedor.get_text()
        if proveedor_id:
            ArticulosPorProveedor(proveedor_id, proveedor)
        else:
            info('Debe colocarle un código al artículo')

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_proveedor(codigo)
        if l:
            self.cargar_proveedor(l)
        else:
            self.limpiar()

    def on_tipo_id_changed(self, *args):
        codigo = self.tipo_id.get_text()
        l = Model().buscar_id_tipo_proveedor(codigo)
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

    def on_banco_id_changed(self, *args):
        codigo = self.banco_id.get_text()
        l = Model().buscar_id_banco(codigo)
        if l:
            self.banco.set_text(l[0][1])
        else:
            self.banco.set_text('')

    def on_buscar_tipo_clicked(self,*args):
        dlg = DlgBuscarTipoProveedor()
        dlg.dialogo.run()
        self.tipo_id.set_text(dlg.resultado[0][0])
        self.tipo.set_text(dlg.resultado[0][1])

    def on_buscar_zona_clicked(self,*args):
        dlg = DlgBuscarZonaProveedor()
        dlg.dialogo.run()
        self.zona_id.set_text(dlg.resultado[0][0])
        self.zona.set_text(dlg.resultado[0][1])

    def on_buscar_banco_clicked(self,*args):
        dlg = DlgBuscarBancoProveedor()
        dlg.dialogo.run()
        self.banco_id.set_text(dlg.resultado[0][0])
        self.banco.set_text(dlg.resultado[0][1])

    def on_nuevo_tipo_clicked(self,*args):
        dlg = DlgTipoProveedor()
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

    def on_nuevo_banco_clicked(self,*args):
        dlg = DlgBanco()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        proveedor = self.proveedor.get_text()
        tipo_id = self.tipo_id.get_text()
        zona_id = self.zona_id.get_text()
        direccion = self.direccion.get_text()
        telefono = self.telefono.get_text()
        email = self.email.get_text()
        dias = self.dias.get_text()
        banco_id = self.banco_id.get_text()
        if not banco_id:
            banco_id = ''
            titular = ''
            cuenta = ''
            tipo_cuenta = ''
        else:
            titular = self.titular.get_text()
            cuenta = self.cuenta.get_text()
            tipo_cuenta = self.tipo_cuenta.get_text()
        lleno = self.campos_llenos(codigo, proveedor, tipo_id, zona_id, telefono)

        if lleno == 1 and not self.editando:
            Model().agregar_proveedor(codigo, proveedor, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta)
            self.limpiar_todo()
            self.codigo.grab_focus()

        if lleno == 1 and self.editando:
            Model().modificar_proveedor(codigo, proveedor, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo, proveedor, tipo_id, zona_id, telefono):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo al proveedor")
            return

        if proveedor == '':
            info("Debe colocar un nombre al proveedor")
            return

        if tipo_id == '':
            info("Debe seleccionar un tipo de proveedor")
            return

        if zona_id == '':
            info('Debe seleccionar una zona para el proveedor')
            return

        if telefono == '':
            info("Debe colocar un telefono al proveedor")
            return

        if codigo != '' and proveedor !='' and tipo_id != '' and zona_id != '' and telefono != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.proveedor.set_text("")
        self.tipo_id.set_text("")
        self.tipo.set_text("")
        self.zona_id.set_text("")
        self.zona.set_text("")
        self.direccion.set_text("")
        self.telefono.set_text("")
        self.email.set_text("")
        self.dias.set_text('0')
        self.banco_id.set_text('')
        self.banco.set_text('')
        self.titular.set_text('')
        self.cuenta.set_text('')
        self.tipo_cuenta.set_text('')

    def limpiar(self, *args):
        self.proveedor.set_text("")
        self.tipo_id.set_text("")
        self.tipo.set_text("")
        self.zona_id.set_text("")
        self.zona.set_text("")
        self.direccion.set_text("")
        self.telefono.set_text("")
        self.email.set_text("")
        self.dias.set_text('0')
        self.banco_id.set_text('')
        self.banco.set_text('')
        self.titular.set_text('')
        self.cuenta.set_text('')
        self.tipo_cuenta.set_text('')


class dlgBuscarProveedor:
    def __init__(self, padre= None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Proveedor.glade")
        builder.connect_signals(self)

        self.dlgBuscarProveedor = builder.get_object("dlgBuscarProveedor")
        self.etiqueta = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.resultado =''
        self.dlgBuscarProveedor.show()

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

            self.etiqueta.set_text('Tipo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 3:

            self.etiqueta.set_text('Zona')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 4:

            self.etiqueta.set_text('Teléfono')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 5:

            self.etiqueta.set_text('Correo electrónico')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_btnBuscar_clicked(self, *args):

        if self.criterio.get_active() == 0:

            self.resultado = Model().buscar_id_proveedor(self.valor.get_text())

        elif self.criterio.get_active() == 1:

            self.resultado = Model().buscar_nombre_proveedor(self.valor.get_text())

        elif self.criterio.get_active() == 2:

            self.resultado = Model().buscar_tipo_proveedor(self.valor.get_text())

        elif self.criterio.get_active() == 3:

            self.resultado = Model().buscar_zona_proveedor(self.valor.get_text())

        elif self.criterio.get_active() == 4:

            self.resultado = Model().buscar_telefono_proveedor(self.valor.get_text())

        elif self.criterio.get_active() == 5:

            self.resultado = Model().buscar_email_proveedor(self.valor.get_text())

    def on_cancelar_clicked(self, *args):
        self.hide()

class DlgBuscarTipoProveedor:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Tipo_Proveedor.glade")
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
        c = Model().tipos_de_proveedores_ordenados_por_id()
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
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_id_tipo_proveedor(codigo)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_tipo(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_tipo(self.valor.get_text())
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

class DlgBuscarZonaProveedor:
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
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_id_zona(codigo)
        self.dialogo.destroy()

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
        self.dialogo.destroy()

class DlgBuscarBancoProveedor:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Banco_Proveedor.glade")
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
        c = Model().bancos_ordenados_por_id()
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
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_id_banco(codigo)
        self.on_dialogo_destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_banco(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_banco(self.valor.get_text())
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
    p = Proveedores()
    p.main()
