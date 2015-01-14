#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       vendedor.py
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
import treetohtml
from mensajes import info
from modelo import Model
from datetime import date, datetime
from articulos_venta import ArticulosVenta
from comunes import punto_coma, coma_punto, es_ve
from clientes import DlgCliente

(CODIGO, FECHA, CLIENTES) = range(3)

class Ventas:


    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wVentas.glade')
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
        registros = Model().contar_registros('ventas')
        buff = "Total de ventas registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de ventas registradas: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([FECHA, "Fecha", str])
        columnas.append ([CLIENTES, "Clientes", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().ventas_ordenadas_por_id())

    def cargar_una_venta(self, tupla):
        self.lista.clear()
        self.lista.append([tupla[0], tupla[1], tupla[2], tupla[3]])

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1].strftime("%d/%m/%Y"),tupla[f][2], tupla[f][3]])

    def on_agregar_clicked(self,*args):
        dlg = DlgVenta()
        fecha = date.today()
        hoy = fecha.strftime("%d/%m/%Y")
        venta_id = Model().nuevo_venta_id()
        dlg.venta_id.set_text(venta_id)
        dlg.emision.set_text(str(hoy))
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
                self.resultado = Model().buscar_id_venta(self.filtro.get_text())
                if self.resultado:
                    self.cargar_una_venta(self.resultado)

        elif self.criterio.get_active() == 1:
            if len(self.filtro.get_text()) == 10:
                self.resultado = Model().buscar_fecha_venta(self.filtro.get_text())
                if self.resultado:
                    self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 2:
            self.resultado = Model().buscar_cliente_venta(self.filtro.get_text())
            self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Ventas", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_venta(codigo)
        d = Model().buscar_detalles_id_venta(codigo)
        n = Model().buscar_nro_cliente(codigo)
        if l and d:
            estado =  l[7]
            self.mostrar_dialogo_con_datos(l, d, n, estado)

    def mostrar_dialogo_con_datos(self, l, d, n, estado):
        dlg = DlgVenta()
        dlg.buscar_cliente.set_visible(False)
        dlg.nuevo_cliente.set_visible(False)
        dlg.agregar.set_visible(False)
        dlg.quitar.set_visible(False)
        dlg.guardar.set_visible(False)
        if estado == 'Si':
            dlg.totalizar.set_visible(False)
        else:
            dlg.totalizar.set_visible(True)
        if n:
            dlg.nro_cliente.set_text(n[0])
        dlg.venta_id.set_text(l[0])
        dlg.cliente_id.set_text(l[1])
        dlg.cliente.set_text(l[2])
        fecha = l[3]
        hoy = fecha.strftime("%d/%m/%Y")
        dlg.emision.set_text(hoy)
        dlg.bruto.set_text(punto_coma(l[4]))
        dlg.impuestos.set_text(punto_coma(l[5]))
        dlg.total.set_text(punto_coma(l[6]))
        dlg.cargar_detalles(d)
        #~ response = dlg.dialogo.run()
        #~ if response == gtk.RESPONSE_OK:
           #~ self.lista.clear()
           #~ self.lista_ordenada_por_id()


class DlgVenta:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('dlgVenta.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.venta_id = builder.get_object('venta_id')
        self.nro_cliente = builder.get_object('nro_cliente')
        self.cliente_id = builder.get_object('cliente_id')
        self.buscar_cliente = builder.get_object('buscar_cliente')
        self.nuevo_cliente = builder.get_object('nuevo_cliente')
        self.agregar = builder.get_object('agregar')
        self.quitar = builder.get_object('quitar')
        self.totalizar =  builder.get_object('totalizar')
        self.guardar = builder.get_object('guardar')
        self.abrir = builder.get_object('abrir')

        self.cliente = builder.get_object('cliente')
        fecha = str(date.today())
        self. emision = builder.get_object('emision')
        self.bruto = builder.get_object('bruto')
        self.impuestos = builder.get_object('impuestos')
        self.total = builder.get_object('total')

        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcolumn2 = builder.get_object('tvcolumn2')
        self.tvcell2 = builder.get_object('tvcell2')
        self.statusbar = builder.get_object('statusbar')

        self.tvcell2.connect( 'edited', self.tvcell2_edited_cb, self.lista )

        self.padre = padre
        if padre is None:
            self.frm_padre = self.dialogo
        else:
            self.frm_padre = self.padre.frm_padre

        self.dialogo.show()

    def cargar_numero(self, nro_cliente, nro_factura):
        self.nro_cliente.set_text(nro_cliente)
        l = Model().buscar_id_venta(nro_factura)
        d = Model().buscar_detalles_id_venta(nro_factura)
        if l and d:
            estado =  l[7]
            self.mostrar_factura_por_numero_de_cliente(l, d, estado)

    def mostrar_factura_por_numero_de_cliente(self, l, d, estado):
        self.buscar_cliente.set_visible(False)
        self.nuevo_cliente.set_visible(False)
        self.agregar.set_visible(False)
        self.quitar.set_visible(False)
        self.guardar.set_visible(False)
        if estado == 'Si':
            self.totalizar.set_visible(False)
        else:
            self.totalizar.set_visible(True)
        self.venta_id.set_text(l[0])
        self.cliente_id.set_text(l[1])
        self.cliente.set_text(l[2])
        self.emision.set_text(str(l[3]))
        self.bruto.set_text(punto_coma(l[4]))
        self.impuestos.set_text(punto_coma(l[5]))
        self.total.set_text(punto_coma(l[6]))
        self.cargar_detalles(d)
        #~ response = dlg.dialogo.run()
        #~ if response == gtk.RESPONSE_OK:
           #~ self.lista.clear()
           #~ self.lista_ordenada_por_id()

    def cargar_cliente(self, l):
        if l:
            self.cliente_id.set_text(l[0][0])
            self.cliente.set_text(l[0][1])

    def on_buscar_cliente_clicked(self, *args):
        dlg = DlgBuscarClienteVenta()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_cliente(dlg.resultado)

    def on_nuevo_cliente_clicked(self, *args):
        dlg = DlgCliente()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_agregar_clicked(self,*args):
        dlg = ArticulosVenta()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_articulo(dlg.resultado)

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        articulo = model.get_value(it,1)

        if yesno("¿Desea eliminar el articulo <b>%s</b>?" % articulo, self.padre) == gtk.RESPONSE_YES:
           model.remove(it)

        self.mostrar_totales()

    def cargar_articulo(self, tupla):
        self.lista.append([punto_coma(tupla[0]), tupla[1], tupla[2], punto_coma(tupla[3]), tupla[4], tupla[5], punto_coma(tupla[6])])
        self.tvcell2.set_property('editable', True)
        self.mostrar_totales()

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([punto_coma(tupla[f][0]), tupla[f][1], tupla[f][2], punto_coma(tupla[f][3]), punto_coma(tupla[f][4]), punto_coma(tupla[f][5]), punto_coma(tupla[f][6])])
        self.calcular_total_bruto()
        self.calcular_iva()
        self.mostrar_totales()

    def tvcell2_edited_cb(self, cell, path, new_text, model):
        model[path][0] = new_text
        nuevo_monto_neto = coma_punto(model[path][0]) * coma_punto(model[path][3])
        model[path][6] = punto_coma('%.2f' % nuevo_monto_neto)
        nuevo_iva = coma_punto(model[path][4])/100 * coma_punto(model[path][6])
        model[path][5] = punto_coma('%.2f' % nuevo_iva)
        self.mostrar_totales()
        return

    def calcular_total_bruto(self):
        total = 0
        try:
            for i in self.lista:
                total += coma_punto(i[6])
        except:
            total = 0
        return total

    def calcular_iva(self, *args):
        impuestos = 0
        try:
            for i in self.lista:
                impuestos += coma_punto(i[5])
        except:
            impuestos = 0
        return impuestos

    def mostrar_totales(self, *args):
        try:
            bruto =  self.calcular_total_bruto()
            impuestos = self.calcular_iva()
            total = bruto + impuestos
            self.bruto.set_text(punto_coma('%.2f' % bruto))
            self.impuestos.set_text(punto_coma('%.2f' % impuestos))
            self.total.set_text(punto_coma('%.2f' % total))
        except:
            self.bruto.set_text('0,00')
            self.impuestos.set_text('0,00')
            self.total.set_text('0,00')

    def campos_llenos(self, venta_id, cliente_id, bruto, impuestos, total):
        ok = 0

        if venta_id == '':
            info("Debe colocar un codigo a la compra")
            return

        if cliente_id == '':
            info("Debe seleccionar un proveedor")
            return

        if bruto == '':
            info('Debe existir un monto bruto')
            return

        if impuestos == '':
            info("Debe existir un monto de los impuestos")
            return

        if total == '':
            info("Debe colocar articulos")
            return

        if venta_id != '' and cliente_id !='' and bruto != '' and impuestos != '' and total != '':
            ok = 1
        else:
            ok = 0

        return ok

    def on_abrir_clicked(self, *args):
        dlg = NumeroCliente()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_numero(dlg.resultado[0], dlg.resultado[1])

    def on_guardar_clicked(self, *args):
        venta_id = self.venta_id.get_text()
        nro_cliente = str(self.nro_cliente.get_text())
        cliente_id = self.cliente_id.get_text()
        emision = str(self.emision.get_text())
        bruto = coma_punto(self.bruto.get_text())
        impuestos = coma_punto(self.impuestos.get_text())
        total = coma_punto(self.total.get_text())
        lleno = self.campos_llenos(venta_id, cliente_id, bruto, impuestos, total)
        filas = len(self.lista)
        if lleno == 1:
            insertado = Model().agregar_venta(venta_id, cliente_id, emision, bruto, impuestos, total)
            Model().insertar_nro_cliente(nro_cliente, venta_id)
            if filas >= 1:
                for i in self.lista:
                    cantidad = coma_punto(i[0])
                    articulo_id = i[1]
                    precio = coma_punto(i[3])
                    monto_iva_venta = coma_punto(i[5])
                    subtotal = coma_punto(i[6])
                    articulos_insertados = Model().agregar_venta_detalles(venta_id, cantidad, articulo_id, precio, monto_iva_venta, subtotal)
#~ #~
        if insertado == 1 and articulos_insertados == filas:
            info('Factura en transito guardada')
            self.limpiar_todo()

    def on_totalizar_clicked(self, *args):
        venta_id = self.venta_id.get_text()
        cliente_id = self.cliente_id.get_text()
        bruto = coma_punto(self.bruto.get_text())
        impuestos = coma_punto(self.impuestos.get_text())
        total = coma_punto(self.total.get_text())
        total_factura = self.total.get_text()
        lleno = self.campos_llenos(venta_id, cliente_id, bruto, impuestos, total)
        filas = len(self.lista)
        venta = Model().buscar_id_venta(venta_id)
        estado = venta[7]
        if estado == 'No':
            dlg = Totalizar()
            dlg.recibido.grab_focus()
            dlg.total_factura.set_text(total_factura)
            response = dlg.dialogo.run()
            if response == gtk.RESPONSE_OK:
               self.procesar(lleno, venta_id)
               dlg.on_cancelar_clicked()
        else:
            info('Esta factura ya fue procesada')

    def procesar(self, lleno, venta_id):
        emision = self.emision.get_text()
        filas = len(self.lista)
        if lleno == 1:
            responsable = 'Expendio'
            concepto = 'Venta'
            tipo_movimiento = 'Salida'
            operacion_id = '02'
            costo = 0.00
            mov = Model().agregar_movimiento(emision, responsable, concepto, tipo_movimiento, operacion_id, venta_id, 'FACTURA')
            Model().procesar_venta(venta_id)
            for i in self.lista:
                cantidad = coma_punto(i[0])
                articulo_id = i[1]
                precio = coma_punto(i[3])
                monto_iva_venta = coma_punto(i[5])
                subtotal = coma_punto(i[6])
                Model().agregar_movimiento_detalles(int(mov[0]), 'Salida', cantidad, articulo_id, costo)
        self.limpiar_todo()
        Model().eliminar_nro_cliente(venta_id)

    def limpiar_todo(self, *args):
        self.lista.clear()
        self.venta_id.set_text('')
        self.nro_cliente.set_text('')
        self.cliente_id.set_text('')
        self.cliente.set_text('')
        fecha = str(date.today())
        self.emision.set_text('')
        self.bruto.set_text('0,00')
        self.impuestos.set_text('0,00')
        self.total.set_text('0,00')

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_imprimir_clicked(self, *args):
        pass

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()


class NumeroCliente:
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('wLista_Numeros.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.tree = builder.get_object("tree")
        self.lista = builder.get_object('lista')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.resultado = ''
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().nro_clientes_ordenados()
        if c:
            self.cargar_lista(c)
        else:
            info('No existen clientes con numero asignado')

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        self.resultado = Model().buscar_nro_cliente(model.get_value(f,0))
        if self.resultado:
            self.dialogo.destroy()

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()


class DlgBuscarClienteVenta:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wLista_Clientes.glade")
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
        self.criterio.set_active(0)
        self.valor.grab_focus()

    def lista_ordenada_por_id(self,*args):
        c = Model().clientes_ordenados_por_id()
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
        self.resultado = Model().buscar_id_cliente(model.get_value(f,0))
        if self.resultado:
            self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_cliente(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_cliente(self.valor.get_text())
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


class Totalizar():

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('dlgTotalizar.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.total_factura = builder.get_object('total_factura')
        self.recibido = builder.get_object('recibido')
        self.vuelto = builder.get_object('vuelto')
        self.dialogo.show()

    def on_recibido_value_changed(self, *args):
        total = coma_punto(self.total_factura.get_text())
        recibido = coma_punto(self.recibido.get_text())
        vuelto = recibido - total
        self.vuelto.set_text(punto_coma('%.2f' % vuelto))

    def on_aceptar_clicked(self, *args):
        pass

    def on_cancelar_clicked(self, *args):
        self.dialogo.destroy()


if __name__ == '__main__':
    Ventas().main()
