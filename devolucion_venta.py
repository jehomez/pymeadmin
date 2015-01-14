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

class Devoluciones:


    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wDevoluciones.glade')
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
            self.lista.append([tupla[f][0],tupla[f][1],tupla[f][2], tupla[f][3]])

    def on_agregar_clicked(self,*args):
        dlg = DlgVenta()
        fecha = date.today()
        dlg.emision.set_text(str(fecha))
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
        if estado == 'si':
            dlg.totalizar.set_visible(False)
        else:
            dlg.totalizar.set_visible(True)
        if n:
            dlg.nro_cliente.set_text(n[0])
        dlg.venta_id.set_text(l[0])
        dlg.cliente_id.set_text(l[1])
        dlg.cliente.set_text(l[2])
        dlg.emision.set_text(str(l[3]))
        dlg.bruto.set_text(punto_coma(l[4]))
        dlg.impuestos.set_text(punto_coma(l[5]))
        dlg.total.set_text(punto_coma(l[6]))
        dlg.cargar_detalles(d)
        #~ response = dlg.dialogo.run()
        #~ if response == gtk.RESPONSE_OK:
           #~ self.lista.clear()
           #~ self.lista_ordenada_por_id()


class DlgDevolucion:
    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('dlgCompra.glade')
        #builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.compra_id = builder.get_object('compra_id')
        self.proveedor_id = builder.get_object('proveedor_id')
        self.proveedor = builder.get_object('proveedor')
        self.rif = builder.get_object('rif')
        self.dias = builder.get_object('dias')
        self.orden = builder.get_object('orden')
        self.deposito_id = builder.get_object('deposito_id')
        self.deposito = builder.get_object('deposito')
        self.emision = builder.get_object('emision')
        fecha = date.isoformat(date.today())
        self.emision.set_text(fecha)
        self.vence = builder.get_object('vence')
        self.bruto = builder.get_object('bruto')
        self.impuestos = builder.get_object('impuestos')
        self.total = builder.get_object('total')

        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcolumn0 = builder.get_object('tvcolumn0')
        self.tvcell0 = builder.get_object('tvcell0')
        self.tvcell3 = builder.get_object('tvcell3')
        self.statusbar = builder.get_object('statusbar')

        self.buscar_proveedor = builder.get_object('buscar_proveedor')
        self.buscar_deposito = builder.get_object('buscar_deposito')
        self.nuevo_proveedor = builder.get_object('nuevo_proveedor')
        self.agregar = builder.get_object('agregar')
        self.quitar = builder.get_object('quitar')
        self.aceptar = builder.get_object('aceptar')
        self.salir = builder.get_object('salir')

        self.dialogo.connect("destroy", self.on_dialogo_destroy)
        self.tvcell0.connect( 'edited', self.on_tvcell0_edited_cb, self.lista )
        self.tvcell3.connect( 'edited', self.on_tvcell3_edited_cb, self.lista )
        self.buscar_proveedor.connect ("clicked", self.on_buscar_proveedor_clicked)
        self.buscar_deposito.connect ("clicked", self.on_buscar_deposito_clicked)
        self.nuevo_proveedor.connect ("clicked", self.on_nuevo_proveedor_clicked)
        self.agregar.connect ("clicked", self.on_agregar_clicked)
        self.quitar.connect ("clicked", self.on_quitar_clicked)
        self.aceptar.connect ("clicked", self.on_aceptar_clicked)
        self.salir.connect ("clicked", self.on_salir_clicked)

        self.padre = padre
        if padre is None:
            self.frm_padre = self.dialogo
        else:
            self.frm_padre = self.padre.frm_padre

        self.dialogo.show()

    def on_buscar_proveedor_clicked(self, *args):
        dlg = DlgBuscarProveedorCompra()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_proveedor(dlg.resultado)

    def cargar_proveedor(self, l):
        self.proveedor_id.set_text(l[0][0])
        self.proveedor.set_text(l[0][1])
        self.rif.set_text(l[0][0])
        self.dias.set_text(str(l[0][9]))
        vence = date.today() + timedelta(l[0][9])
        self.vence.set_text(str(vence))

    def on_buscar_deposito_clicked(self, *args):
        dlg = DlgBuscarDepositoArticulo()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.deposito_id.set_text(dlg.resultado[0][0])
            self.deposito.set_text(dlg.resultado[0][1])

    def on_nuevo_proveedor_clicked(self, *args):
        dlg = DlgProveedor()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_agregar_clicked(self,*args):
        dlg = ArticulosCompra()
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
        self.lista.append([punto_coma(tupla[0]), tupla[1], tupla[2], punto_coma(tupla[3]), punto_coma(tupla[4]), punto_coma(tupla[5]), punto_coma(tupla[6])])
        self.tvcell0.set_property('editable', True)
        self.tvcell3.set_property('editable', True)
        self.mostrar_totales()

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([punto_coma(tupla[f][0]), tupla[f][1], tupla[f][2], punto_coma(tupla[f][3]), punto_coma(tupla[f][4]), punto_coma(tupla[f][5]), punto_coma(tupla[f][6])])
        self.calcular_total_bruto()
        self.calcular_iva()
        self.mostrar_totales()

    def on_tvcell0_edited_cb(self, cell, path, new_text, model):
        model[path][0] = new_text
        nuevo_monto_neto = coma_punto(model[path][0]) * coma_punto(model[path][3])
        model[path][6] = punto_coma(nuevo_monto_neto)
        nuevo_iva = coma_punto(model[path][4])/100 * coma_punto(model[path][6])
        model[path][5] = punto_coma(nuevo_iva)
        self.mostrar_totales()
        return

    def on_tvcell3_edited_cb(self, cell, path, new_text, model):
        model[path][3] = new_text
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

    def campos_llenos(self, compra_id, proveedor_id, bruto, impuestos, total):
        ok = 0

        if compra_id == '':
            info("Debe colocar un codigo a la compra")
            return

        if proveedor_id == '':
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

        if compra_id != '' and proveedor_id !='' and bruto != '' and impuestos != '' and total != '':
            ok = 1
        else:
            ok = 0

        return ok

    def on_aceptar_clicked(self, *args):
        compra_id = self.compra_id.get_text()
        proveedor_id = self.proveedor_id.get_text()
        orden = self.orden.get_text()
        deposito_id = self.deposito_id.get_text()
        emision = self.emision.get_text()
        vence = self.vence.get_text()
        bruto = coma_punto(self.bruto.get_text())
        impuestos = coma_punto(self.impuestos.get_text())
        total = coma_punto(self.total.get_text())
        lleno = self.campos_llenos(compra_id, proveedor_id, bruto, impuestos, total)
        filas = len(self.lista)
        if lleno == 1:
            insertado = Model().agregar_compra(compra_id, proveedor_id, orden, deposito_id, emision, vence, bruto, impuestos, total)
            emision = str(date.today())
            responsable = 'Encargado del deposito'
            concepto = 'Compra a Proveedor'
            tipo_movimiento = 'Entrada'
            operacion_id = '01'
            mov = Model().agregar_movimiento(emision, responsable, concepto, tipo_movimiento, operacion_id, compra_id, 'COMPRA')
            if filas >= 1:
                for i in self.lista:
                    cantidad = coma_punto(i[0])
                    articulo_id = i[1]
                    costo = coma_punto(i[3])
                    monto_iva = coma_punto(i[5])
                    total_neto = coma_punto(i[6])
                    articulo_insertado = Model().agregar_compra_detalles(compra_id, emision, cantidad, articulo_id, costo, monto_iva, total_neto)
                    Model().agregar_movimiento_detalles(int(mov[0]), 'Entrada', cantidad, articulo_id, total_neto)
                    filas_insertadas += articulo_insertado
            else:
                info('Debe agregar un articulo para la compra')
                self.agregar.grab_focus()
        else:
            info('Debe seleccionar un proveedor')
            self.buscar_proveedor.grab_focus()
        if insertado == 1 and filas_insertadas == fias:
            self.limpiar_todo()

    def limpiar_todo(self, *args):
        self.compra_id.set_text('')
        self.proveedor_id.set_text('')
        self.proveedor.set_text('')
        self.rif.set_text('')
        self.dias.set_text('')
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
