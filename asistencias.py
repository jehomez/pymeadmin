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
import treetohtml
from mensajes import info
from modelo import Model
from empleados import DlgEmpleado


(CODIGO, EMPLEADO, ENTRADA, SALIDA, TIEMPO) = range(5)

rDir = os.getcwd()
os.chdir(rDir)

class Asistencias:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wAsistencias.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
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
        registros = Model().contar_registros('asistencias')
        buff = "Total de asistencias registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de asistencias registradas:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([EMPLEADO, "Empleado", str])
        columnas.append ([ENTRADA, "Entrada", str])
        columnas.append ([SALIDA, "Salida", str])
        columnas.append ([TIEMPO, "Tiempo", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().asistencias_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0], tupla[f][1], tupla[f][2], tupla[f][3], tupla[f][4]])

    def on_agregar_clicked(self,*args):
        dlg = DlgAsistencia(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        self.on_refrescar_clicked()
        if response == gtk.RESPONSE_OK:
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
        criterio = self.criterio.get_active()
        if  criterio == 0 or criterio == 1 or criterio == 2:
            self.filtro.set_text('')
            self.filtro.grab_focus()

    def on_filtro_changed(self, *args):

        if self.criterio.get_active() == 0:

            self.resultado = Model().buscar_id_asistencia(self.filtro.get_text())

        elif self.criterio.get_active() == 1:

            self.resultado = Model().buscar_empleado_asistencia(self.filtro.get_text())

        elif self.criterio.get_active() == 2:
            filtro = len(self.filtro.get_text())
            if filtro ==10:
                self.resultado = Model().buscar_dia_asistencia(self.filtro.get_text())
            else:
                self.resultado = ''

        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Asistencias", self.col_data)
        t.show()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_asistencia(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, l):
        dlg = DlgAsistencia(self.frm_padre, False)
        dlg.editando = True
        dlg.empleado_id.set_text(l[0][0])
        dlg.empleado.set_editable(False)
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgAsistencia:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgAsistencia.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.empleado_id = builder.get_object("empleado_id")
        self.empleado = builder.get_object("empleado")
        self.empleado_id.grab_focus()
        self.dialogo.show()

    def on_empleado_id_changed(self, *args):
        codigo = self.empleado_id.get_text()
        l = Model().buscar_id_empleado(codigo)
        if  l:
            self.cargar_empleado(l)
            self.on_guardar_clicked()
        else:
            self.limpiar()

    def cargar_empleado(self, l):
        if l:
            self.empleado_id.set_text(l[0])
            self.empleado.set_text(l[1])

    def on_buscar_empleado_clicked(self, *args):
        dlg = DlgBuscarEmpleadoAsistencia()
        response = dlg.dialogo.run()
        self.empleado_id.set_text(dlg.resultado[0])
        self.empleado.set_text(dlg.resultado[1])

    def on_nuevo_empleado_clicked(self, *args):
        dlg = DlgEmpleado()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_guardar_clicked(self, *args):
        empleado_id = self.empleado_id.get_text()
        empleado = unicode(self.empleado.get_text())

        lleno = self.campos_llenos(empleado_id, empleado)

        if lleno == 1 and not self.editando:
            Model().agregar_asistencia(empleado_id)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, empleado_id, empleado):
        ok = 0

        if empleado_id == '':
            info("Debe colocar un código de empleado")
            return

        if empleado == '':
            info("Debe colocar un nombre empleado")
            return

        if empleado_id != '' and empleado != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.empleado_id.set_text("")
        self.empleado.set_text("")

    def limpiar(self, *args):
        self.empleado.set_text("")


class DlgBuscarEmpleadoAsistencia:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Empleado_Asistencia.glade")
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
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().empleados_ordenados_por_id()
        self.cargar_lista(c)

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][14], tupla[f][1]])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Tipo de empleado')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 2:
            self.lblValor.set_text('Nombre')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        empleado_id = model.get_value(f,0)
        self.resultado = Model().buscar_id_empleado(empleado_id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_para_empleado(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_tipo_para_empleado(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 2:
            self.resultado = Model().buscar_nombre_empleado(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            info('Debe seleccionar un criterio de búsqueda')

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
    z = Asistencias()
    z.main()
