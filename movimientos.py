#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       movimiento.py
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
from datetime import date
from articulos import DlgArticulo
from asistencias import DlgBuscarEmpleadoAsistencia
from comunes import coma_punto, mov_int_to_str, mov_str_to_int, punto_coma
from mensajes import info, yesno
from modelo import Model
from operaciones import DlgOperacion


(CODIGO, FECHA, TIPO_DE_MOVIMIENTO, RESPONSABLE) = range(4)

class Movimientos:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wMovimientos.glade')
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
        registros = Model().contar_registros('movimientos')
        buff = "Total de movimientos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de movimientos registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([FECHA, "Fecha", str])
        columnas.append ([TIPO_DE_MOVIMIENTO, "Tipo de Movimiento", str])
        columnas.append ([RESPONSABLE, "Responsable", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().movimientos_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],tupla[f][4],tupla[f][6],tupla[f][2]])

    def on_agregar_clicked(self,*args):
        dlg = DlgMovimiento(self.frm_padre, False)
        dlg.editando = False
        emision = date.today()
        dlg.fecha.set_text(str(emision))
        response = dlg.dialogo.run()
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
        self.filtro.set_text('')
        self.filtro.grab_focus()

    def on_filtro_changed(self, *args):
        if self.criterio.get_active() == 0:

            self.resultado = Model().buscar_id_movimiento(int(self.filtro.get_text()))

        elif self.criterio.get_active() == 1:

            self.resultado = Model().buscar_fecha_movimiento(self.filtro.get_text())

        elif self.criterio.get_active() == 2:

            self.resultado = Model().buscar_tipo_movimiento(self.filtro.get_text())

        elif self.criterio.get_active() == 3:

            self.resultado = Model().buscar_responsable_movimiento(self.filtro.get_text())

        elif self.criterio.get_active() == 4:

            self.resultado = Model().buscar_articulo_movimiento(self.filtro.get_text())

        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.treeMovimientos,"Lista de Movimientos", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = int(model.get_value(f,0))
        l = Model().buscar_id_movimiento(codigo)
        d = Model().buscar_id_movimiento_detalles(codigo)
        self.mostrar_dialogo_con_datos(l, d)

    def mostrar_dialogo_con_datos(self, l, d):
        dlg = DlgMovimiento(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(str(l[0][0]))
        dlg.codigo.set_editable(False)
        dlg.fecha.set_text(str(l[0][1]))
        dlg.responsable.set_text(l[0][2])
        dlg.concepto.set_text(l[0][3])
        dlg.movimiento.set_active(mov_str_to_int(l[0][4]))
        dlg.operacion_id.set_text(l[0][5])
        dlg.operacion.set_text(l[0][6])
        dlg.cargar_detalles(d)
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgMovimiento:

    def __init__(self, padre = None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgMovimiento.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.fecha = builder.get_object("fecha")
        self.responsable = builder.get_object('responsable')
        self.concepto = builder.get_object('concepto')
        self.movimiento = builder.get_object('movimiento')
        self.operacion_id = builder.get_object('operacion_id')
        self.operacion = builder.get_object('operacion')
        self.tree = builder.get_object('treeview')
        self.lista = builder.get_object('lista')
        self.tvcell0 = builder.get_object('tvcell0')
        self.tvcell3 = builder.get_object('tvcell3')

        self.tvcell0.connect('edited', self.tvcell0_edited_cb, self.lista)
        self.tvcell3.connect('edited', self.tvcell3_edited_cb, self.lista)
        self.dialogo.show()

    def cargar_movimiento(self, l):
        self.codigo.set_text(l[0][0])
        self.fecha.set_text(str(l[0][1]))
        self.responsable.set_text(l[0][2])
        self.concepto.set_text(l[0][3])
        self.movimiento.set_active(mov_str_to_int(l[0][4]))
        self.operacion_id.set_text(l[0][5])
        self.operacion.set_text(l[0][6])


    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_movimiento(codigo)
        if l:
            self.cargar_movimiento(l)
        else:
            self.limpiar()

    def on_buscar_operacion_clicked(self, *args):
        dlg = DlgBuscarOperacionMovimiento()
        dlg.dialogo.run()
        if dlg.resultado:
            self.operacion_id.set_text(dlg.resultado[0][0])
            self.operacion.set_text(dlg.resultado[0][1])

    def on_nueva_operacion_clicked(self, *args):
        dlg = DlgOperacion()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_buscar_articulo_clicked(self, *args):
        dlg = DlgBuscarArticuloMovimiento()
        response = dlg.dialogo.run()
        l = dlg.resultado
        if l:
            self.articulo_id.set_text(l[0][0])
            self.articulo.set_text(l[0][1])

    def on_nuevo_articulo_clicked(self, *args):
        dlg = DlgArticulo()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dlgArticulo.hide()

    def on_operacion_id_changed(self, *args):
        codigo = self.operacion_id.get_text()
        l = Model().buscar_id_operacion(codigo)
        if l:
            self.operacion.set_text(l[0][1])
        else:
            self.operacion.set_text('')

    def on_articulo_id_changed(self, *args):
        codigo = self.articulo_id.get_text()
        movimiento = self.movimiento.get_active()
        l = Model().buscar_id_articulo(codigo)
        if l:
            self.articulo.set_text(l[0][1])
            if l[0][16] == 0 and movimiento == 1:
                mensaje = 'El Articulo ' + l[0][1] + ' no posee existencia'
                info(mensaje)

    def on_agregar_clicked(self, *args):
        dlg = DlgBuscarArticuloMovimiento()
        dlg.dialogo.set_title('Lista de Articulos')
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_articulo(dlg.resultado)

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        articulo = model.get_value(it,1)

        if yesno("¿Desea eliminar el articulo <b>%s</b>?" % articulo, None) == gtk.RESPONSE_YES:
           model.remove(it)

    def cargar_articulo(self, tupla):
        self.lista.append([punto_coma(tupla[0]), tupla[1], tupla[2], punto_coma(tupla[3])])
        self.tvcell0.set_property('editable', True)
        self.tvcell3.set_property('editable', True)

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([punto_coma(tupla[f][0]), tupla[f][1], tupla[f][2], punto_coma(tupla[f][3])])

    def tvcell0_edited_cb(self, cell, path, new_text, model):
        model[path][0] = punto_coma(new_text)
        return

    def tvcell3_edited_cb(self, cell, path, new_text, model):
        model[path][3] = punto_coma(new_text)
        return

    def on_guardar_clicked(self, *args):
        fecha = str(date.today())
        responsable = self.responsable.get_text()
        concepto = self.concepto.get_text()
        movimiento = mov_int_to_str(int(self.movimiento.get_active()))
        operacion_id = self.operacion_id.get_text()
        lleno = self.campos_llenos(responsable, concepto, movimiento, operacion_id)
        filas = len(self.lista)
        tipo_doc = 'AJUSTE'
        documento = 'XXX'

        if lleno == 1 and not self.editando:
            lista = Model().agregar_movimiento( fecha, responsable, concepto, movimiento, operacion_id, documento, tipo_doc)
            mov_id = int(lista[0])
            Model().actualizar_movimiento(mov_id)
            if filas >= 1:
                filas_insertadas = 0
                for i in self.lista:
                    cantidad = coma_punto(i[0])
                    articulo_id = i[1]
                    costo = coma_punto(i[3])
                    fila_insertada = Model().agregar_movimiento_detalles(mov_id, movimiento, cantidad, articulo_id, costo)
                    filas_insertadas += fila_insertada

            if mov_id and filas_insertadas == filas:
                self.limpiar_todo()
                self.limpiar_todo()
                self.responsable.grab_focus()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, responsable, concepto, movimiento, operacion_id):
        ok = 0

        if responsable == '':
            info("Debe colocar un responsable del movimiento")
            return

        if concepto == '':
            info("Debe colocar un concepto al movimiento")
            return

        if movimiento == '':
            info("Debe seleccionar un tipo de movimiento")
            return

        if operacion_id == '':
            info("Debe seleccionar un tipo de operación")
            return

        if responsable != '' and concepto != '' and operacion_id != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text('')
        self.responsable.set_text('')
        self.concepto.set_text('')
        self.movimiento.set_active(-1)
        self.operacion_id.set_text('')
        self.lista.clear()

    def limpiar(self, *args):
        self.responsable.set_text('')
        self.concepto.set_text('')
        self.movimiento.set_active(-1)
        self.operacion_id.set_text('')


class DlgBuscarOperacionMovimiento:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Operacion_Movimiento.glade")
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
        self.cargar_lista(Model().operaciones_ordenadas_por_id())

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
        self.resultado = Model().buscar_id_operacion(codigo)
        if self.resultado:
            self.on_dialogo_destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_operacion(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_operacion(self.valor.get_text())
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

class DlgBuscarArticuloMovimiento:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Articulo_Movimiento.glade")
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
        self.cargar_lista(Model().articulos_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1], punto_coma(tupla[f][18])])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Nombre')

        self.valor.set_text('')
        self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_articulo_para_movimiento(codigo)
        if self.resultado:
            self.on_dialogo_destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_articulo(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_articulo(self.valor.get_text())
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
    d = Movimientos()
    d.main()
