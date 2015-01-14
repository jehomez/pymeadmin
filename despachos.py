# -*- coding: utf-8 -*-
#
#       compras.py
#
#       Copyright 2010 Jesús Hómez <jesus@jesus-laptop>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY, WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import gtk
import os
from datetime import date, datetime
from decimal import Decimal
from mensajes import info, yesno
import treetohtml
from modelo import Model
from empleados import DlgEmpleado
from asistencias import DlgBuscarEmpleadoAsistencia
from articulos_a_despachar import ArticulosADespachar
from comunes import punto_coma, coma_punto

rDir = os.getcwd()
os.chdir(rDir)


(CODIGO, FECHA, EMPLEADO) = range(3)

(ARTICULO_ID, ARTICULO, UNIDAD, CANTIDAD, COSTO, SUBTOTAL, IVA_COMPRA, MONTO_IVA, TOTAL) = range(9)

class Despachos:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wDespachos.glade')
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
        registros = Model().contar_registros('despachos')
        buff = "Total de despachos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de despachos registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([FECHA, "Fecha", str])
        columnas.append ([EMPLEADO, "Empleado", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().despachos_ordenados_por_id())

    def cargar_un_despacho(self, tupla):
        self.lista.clear()
        self.lista.append([tupla[0],tupla[1],tupla[3]])

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],tupla[f][3]])

    def on_agregar_clicked(self,*args):
        dlg = DlgDespacho()
        fechahora = datetime.now()
        dlg.emision.set_text(str(fechahora))
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
            if self.filtro.get_text():
                self.resultado = Model().buscar_id_despacho(int(self.filtro.get_text()))
                self.cargar_un_despacho(self.resultado)

        elif self.criterio.get_active() == 1:
            if len(self.filtro.get_text()) == 10:
                self.resultado = Model().buscar_fecha_despacho(self.filtro.get_text())
                self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 2:
            self.resultado = Model().buscar_empleado_despacho(self.filtro.get_text())
            self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Despachos", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = int(model.get_value(f,0))
        l = Model().buscar_id_despacho(codigo)
        d = Model().buscar_detalles_id_despacho(codigo)
        self.mostrar_dialogo_con_datos(l, d)

    def mostrar_dialogo_con_datos(self, l, d):
        dlg = DlgDespacho()
        dlg.buscar_empleado.set_visible(False)
        dlg.nuevo_empleado.set_visible(False)
        dlg.agregar.set_visible(False)
        dlg.quitar.set_visible(False)
        dlg.aceptar.set_visible(False)
        dlg.despacho_id.set_text(str(l[0]))
        dlg.emision.set_text(str(l[1]))
        dlg.empleado_id.set_text(l[2])
        dlg.empleado.set_text(l[3])
        dlg.bruto.set_text(punto_coma(l[4]))
        dlg.impuestos.set_text(punto_coma(l[5]))
        dlg.total.set_text(punto_coma(l[6]))
        dlg.cargar_detalles(d)
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()


class DlgDespacho:

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('dlgDespachos.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.despacho_id = builder.get_object('despacho_id')
        self.empleado_id = builder.get_object('empleado_id')
        self.empleado = builder.get_object('empleado')
        self.buscar_empleado = builder.get_object('buscar_empleado')
        self.nuevo_empleado = builder.get_object('nuevo_empleado')
        self.agregar = builder.get_object('agregar')
        self.quitar = builder.get_object('quitar')
        self.aceptar = builder.get_object('aceptar')
        self.emision = builder.get_object('emision')
        self.bruto = builder.get_object('bruto')
        self.impuestos = builder.get_object('impuestos')
        self.total = builder.get_object('total')

        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcell3 = builder.get_object('tvcell3')

        self.tvcell3.connect('edited', self.tvcell3_edited_cb, self.lista)

        self.padre = padre
        if padre is None:
            self.frm_padre = self.dialogo
        else:
            self.frm_padre = self.padre.frm_padre

        self.bruto.set_text('0,00')
        self.impuestos.set_text('0,00')
        self.total.set_text('0,00')
        self.crear_columnas()
        self.dialogo.show()

    def on_buscar_empleado_clicked(self, *args):
        dlg = DlgBuscarEmpleadoAsistencia()
        dlg.criterio.set_active(2)
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.empleado_id.set_text(dlg.resultado[0])
            self.empleado.set_text(dlg.resultado[1])

    def on_nuevo_empleado_clicked(self, *args):
        dlg = DlgEmpleado()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_agregar_clicked(self,*args):
        dlg = ArticulosADespachar()
        dlg.dialogo.set_title('Lista de Articulos para despachar')
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_articulo(dlg.resultado)

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        articulo = model.get_value(it,1)

        if yesno("¿Desea eliminar el articulo <b>%s</b>?" % articulo, self.padre) == gtk.RESPONSE_YES:
           model.remove(it)

    def cargar_articulo(self, tupla):
        self.lista.append([tupla[0], tupla[1], tupla[2], punto_coma(tupla[3]), punto_coma(tupla[4]), punto_coma(tupla[5]), punto_coma(tupla[6]), punto_coma(tupla[7]), punto_coma(tupla[8])])
        self.tvcell3.set_property('editable', True)
        self.mostrar_totales()

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0], tupla[f][1], tupla[f][2], punto_coma(tupla[f][3]), punto_coma(tupla[f][4]), punto_coma(tupla[f][5]), punto_coma(tupla[f][6]), punto_coma(tupla[f][7]), punto_coma(tupla[f][8])])

    def tvcell3_edited_cb(self, cell, path, new_text, model):
        model[path][3] = new_text
        subtotal = coma_punto(model[path][3]) * coma_punto(model[path][4])
        model[path][5] = punto_coma('%.2f' % subtotal)
        nuevo_iva = coma_punto(model[path][5])/100 * coma_punto(model[path][6])
        model[path][7] = punto_coma('%.2f' % nuevo_iva)
        nuevo_total = subtotal + nuevo_iva
        model[path][8] = punto_coma('%.2f' % nuevo_total)
        (model, f) = self.tree.get_selection().get_selected()
        cantidad = Decimal(model.get_value(f,3))
        articulo_id = model.get_value(f,0)
        status = Model().verificar_existencia_detallada(articulo_id, cantidad, 'Salida')
        if status == 1:
            self.mostrar_totales()

    def calcular_total_bruto(self):
        total = 0
        try:
            for i in self.lista:
                total += coma_punto(i[5])
        except:
            total =  0
        return total

    def calcular_iva(self, *args):
        impuestos = 0
        try:
            for i in self.lista:
                impuestos += coma_punto(i[7])
        except:
            impuestos =  0
        return impuestos

    def mostrar_totales(self, *args):
        try:
            bruto =  self.calcular_total_bruto()
            iva = self.calcular_iva()
            total = bruto + iva
            self.bruto.set_text(punto_coma('%.2f' % bruto))
            self.impuestos.set_text(punto_coma('%.2f' % iva))
            self.total.set_text(punto_coma('%.2f' % total))
        except:
            self.bruto.set_text('0,00')
            self.impuestos.set_text('0,00')
            self.total.set_text('0,00')

    def campos_llenos(self, empleado_id):
        ok = 0

        if empleado_id == '':
            info("Debe seleccionar un empleado")
            return

        if empleado_id != '':
            ok = 1
        else:
            ok = 0

        return ok

    def crear_columnas(self):
        columnas = []
        columnas.append ([ARTICULO_ID, "Codigo", str])
        columnas.append ([ARTICULO, "Articulo", str])
        columnas.append ([UNIDAD, "Unidad", str])
        columnas.append ([CANTIDAD, "Cantidad", str])
        columnas.append ([COSTO, "Costo Unitario", str])
        columnas.append ([SUBTOTAL, "Subtotal", str])
        columnas.append ([IVA_COMPRA, "% I. V. A. Compra", str])
        columnas.append ([MONTO_IVA, "Monto IVA", str])
        columnas.append ([TOTAL, "Subtotal", str])
        self.col_data = [x[0] for x in columnas]

    def on_imprimir_clicked(self, *args):
        t = treetohtml.TreeToHTML(self.tree,"", self.col_data)
        t.show()

    def on_aceptar_clicked(self, *args):
        empleado_id = self.empleado_id.get_text()
        emision = self.emision.get_text()
        bruto = coma_punto(self.bruto.get_text())
        impuestos = coma_punto(self.impuestos.get_text())
        total = coma_punto(self.total.get_text())
        lleno = self.campos_llenos(empleado_id)
        filas = len(self.lista)
        if lleno == 1:
            despacho = Model().agregar_despacho(empleado_id, emision, bruto, impuestos, total)
            emision = str(date.today())
            responsable = 'Encargado del deposito'
            concepto = 'Despacho de Materia Prima'
            tipo_movimiento = 'Salida'
            operacion_id = '02'
            lista = Model().agregar_movimiento(emision, responsable, concepto, tipo_movimiento, operacion_id, despacho[0], 'DESPACHO')
            mov_id = lista[0]
            if filas >= 1:
                filas_insertadas = 0
                for i in self.lista:
                    despacho_id = int(despacho[0])
                    cantidad = coma_punto(i[3])
                    articulo_id = i[0]
                    total_neto = coma_punto(i[8])
                    status = Model().verificar_existencia_simple(articulo_id, cantidad, 'Salida')
                    if status == 1 and despacho_id:
                        fila_insertada = Model().agregar_despacho_detalles(despacho_id, cantidad, articulo_id, total_neto)
                        filas_insertadas += fila_insertada
                        if mov_id:
                            Model().agregar_movimiento_detalles(mov_id, 'Salida', cantidad, articulo_id, Decimal('0.00'))
                        else:
                            info('mod_id invalida')
            else:
                info('Debe agregar un articulo para despachar')
                self.agregar.grab_focus()
        else:
            info('Debe seleccionar un empleado')
            self.buscar_empleado.grab_focus()

        if despacho_id and filas_insertadas == filas:
            self.limpiar_todo()

    def limpiar_todo(self, *args):
        self.empleado_id.set_text('')
        self.empleado.set_text('')
        fecha = date.isoformat(date.today())
        self.emision.set_text(fecha)
        self.bruto.set_text('0,00')
        self.impuestos.set_text('0,00')
        self.total.set_text('0,00')
        self.lista.clear()

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    Despachos().main()
