#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       turnos.py
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
from mensajes import info, yesno
import treetohtml
from modelo import Model

(CODIGO, TURNOS) = range(2)

class Turnos:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wTurnos.glade')
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
        registros = Model().contar_registros('turnos')
        buff = "Total de turnos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de turnos registrados:')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([TURNOS, "Turnos", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().turnos_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1], tupla[f][2], tupla[f][3]])

    def on_agregar_clicked(self,*args):
        dlg = DlgTurno(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        turno = model.get_value(it,1)

        if yesno("¿Desea eliminar la turno <b>%s</b>?\nEsta acción no se puede deshacer\n" % turno, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_turno(codigo)
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
                self.resultado = Model().buscar_id_turno(self.filtro.get_text())
                self.cargar_un_despacho(self.resultado)

        elif self.criterio.get_active() == 1:
            if len(self.filtro.get_text()) == 10:
                self.resultado = Model().buscar_nombre_turno(self.filtro.get_text())
                self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Turnos", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_turno(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, t):
        dlg = DlgTurno(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(t[0][0])
        dlg.codigo.set_editable(False)
        dlg.turno.set_text(t[0][1])
        dlg.turno.grab_focus()
        inicio = t[0][2]
        dlg.hora_inicio.set_text(str(inicio.hour))
        dlg.min_inicio.set_text(str(inicio.minute))
        dlg.seg_inicio.set_text(str(inicio.second))
        fin = t[0][3]
        dlg.hora_fin.set_text(str(fin.hour))
        dlg.min_fin.set_text(str(fin.minute))
        dlg.seg_fin.set_text(str(fin.second))

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()


class DlgTurno:

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgTurno.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.turno = builder.get_object("turno")
        self.hora_inicio = builder.get_object("hora_inicio")
        self.min_inicio = builder.get_object("min_inicio")
        self.seg_inicio = builder.get_object("seg_inicio")
        self.hora_fin = builder.get_object("hora_fin")
        self.min_fin = builder.get_object("min_fin")
        self.seg_fin = builder.get_object("seg_fin")
        self.dialogo.show()

    def cargar_turno(self, l):
        self.turno.set_text(l[0][1])
        inicio = l[0][2]
        fin = l[0][3]
        self.hora_inicio.set_text()
        self.min_inicio.set_text()
        self.seg_inicio.set_text()
        self.hora_fin.set_text()
        self.min_fin.set_text()
        self.seg_fin.set_text()

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_turno(codigo)
        if l:
            self.cargar_turno(l)
        else:
            self.limpiar()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        turno = self.turno.get_text()
        inicio = self.hora_inicio.get_text()+':'+self.min_inicio.get_text()+':'+self.seg_inicio.get_text()
        fin = self.hora_fin.get_text()+':'+self.min_fin.get_text()+':'+self.seg_fin.get_text()
        lleno = self.campos_llenos(codigo, inicio, fin, turno)

        if lleno == 1 and not self.editando:
            Model().agregar_turno(codigo, inicio, fin, turno)
            self.limpiar_todo()

        if lleno == 1 and self.editando:
            Model().modificar_turno(codigo, inicio, fin, turno)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo, inicio, fin, turno):
        ok = 0

        if codigo == '':
            info("Debe colocar un codigo al turno")
            return

        if inicio == '':
            info("Debe colocar una hora de inicio al turno")
            return

        if fin == '':
            info("Debe colocar una hora de finalización al turno")
            return

        if turno == '':
            info("Debe colocar una descripción al turno")
            return

        if codigo != '' and inicio != '' and fin != '' and turno != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.turno.set_text("")
        self.hora_inicio.set_text('0')
        self.min_inicio.set_text('0')
        self.seg_inicio.set_text('0')
        self.hora_fin.set_text('0')
        self.min_fin.set_text('0')
        self.seg_fin.set_text('0')

    def limpiar(self, *args):
        self.turno.set_text("")
        self.turno.set_text("")
        self.hora_inicio.set_text('0')
        self.min_inicio.set_text('0')
        self.seg_inicio.set_text('0')
        self.hora_fin.set_text('0')
        self.min_fin.set_text('0')
        self.seg_fin.set_text('0')

if __name__ == '__main__':
    z = Turnos()
    z.main()
