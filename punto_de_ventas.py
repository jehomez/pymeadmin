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
from articulos_punto_venta import ArticulosVenta
from comunes import punto_coma, coma_punto, es_ve


(CODIGO, FECHA, CLIENTES) = range(3)


class Punto:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('punto_de_venta.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.codigo = builder.get_object('codigo')
        self.articulo = builder.get_object('articulo')
        self.precio = builder.get_object('precio')
        self.cantidad = builder.get_object('cantidad')
        self.cliente_id = builder.get_object('cliente_id')
        self.buscar_cliente = builder.get_object('buscar_cliente')
        self.nuevo_cliente = builder.get_object('nuevo_cliente')
        self.agregar = builder.get_object('agregar')
        self.quitar = builder.get_object('quitar')
        self.totalizar =  builder.get_object('totalizar')
        self.aceptar = builder.get_object('aceptar')

        self.cliente = builder.get_object('cliente')
        fecha = str(date.today())
        self. emision = builder.get_object('emision')
        self.iva = builder.get_object('iva')
        self.total = builder.get_object('total')

        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcolumn0 = builder.get_object('tvcolumn0')
        self.tvcell0 = builder.get_object('tvcell0')
        self.statusbar = builder.get_object('statusbar')

        self.tvcell0.connect( 'edited', self.tvcell0_edited_cb, self.lista )

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre


        self.ventana.show()

    def on_buscar_clicked(self,*args):
        dlg = ArticulosVenta()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.codigo.set_text(dlg.resultado[1])
            self.articulo.set_text(dlg.resultado[2])
            self.precio.set_text(punto_coma(dlg.resultado[5]))
            self.cantidad.set_text(str(punto_coma(dlg.resultado[0])))

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
        resultado = Model().buscar_articulo_punto_venta(self.codigo.get_text())
        cantidad = float(self.cantidad.get_text())
        precio = float(self.precio.get_text())
        total = cantidad * precio
        iva_venta = resultado[3]
        monto_iva = (iva_venta/100) * precio
        new_resultado = list(resultado)
        del new_resultado[0]
        del new_resultado[4]
        del new_resultado[6]
        new_resultado.insert(0, cantidad)
        new_resultado.insert(4, monto_iva)
        new_resultado.append(precio)

        if resultado:
            self.cargar_articulo(new_resultado )

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        articulo = model.get_value(it,1)

        if yesno("¿Desea eliminar el articulo <b>%s</b>?" % articulo, self.padre) == gtk.RESPONSE_YES:
           model.remove(it)

        self.mostrar_totales()

    def cargar_articulo(self, cantidad, tupla):
        self.lista.append([cantidad), tupla[2], punto_coma(tupla[3]), tupla[4], tupla[5], punto_coma(tupla[6])])
        self.tvcell0.set_property('editable', True)
        self.mostrar_totales()

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([punto_coma(tupla[f][0]), tupla[f][1], tupla[f][2], punto_coma(tupla[f][3]), punto_coma(tupla[f][4]), punto_coma(tupla[f][5]), punto_coma(tupla[f][6])])
        self.calcular_total_bruto()
        self.calcular_iva()
        self.mostrar_totales()

    def tvcell0_edited_cb(self, cell, path, new_text, model):
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
        pass

    def on_guardar_clicked(self, *args):
        pass

    def on_aplicar_clicked(self, *args):
        total_factura = self.total.get_text()
        dlg = Totalizar()
        dlg.recibido.grab_focus()
        dlg.total_factura.set_text(total_factura)
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_aceptar_clicked()

    def on_aceptar_clicked(self, *args):
        venta_id = self.venta_id.get_text()
        cliente_id = self.cliente_id.get_text()
        emision = self.emision.get_text()
        bruto = coma_punto(self.bruto.get_text())
        impuestos = coma_punto(self.impuestos.get_text())
        total = coma_punto(self.total.get_text())
        lleno = self.campos_llenos(venta_id, cliente_id, bruto, impuestos, total)
        filas = len(self.lista)
        if lleno == 1:
            insertado = Model().agregar_venta(venta_id, cliente_id, emision, bruto, impuestos, total)
            if filas >= 1:
                for i in self.lista:
                    cantidad = coma_punto(i[0])
                    articulo_id = i[1]
                    precio = coma_punto(i[3])
                    monto_iva_venta = coma_punto(i[5])
                    subtotal = coma_punto(i[6])
                    articulos_insertados = Model().agregar_venta_detalles(venta_id, emision, cantidad, articulo_id, precio, monto_iva_venta, subtotal)
            else:
                info('Debe agregar un articulo para la compra')
                self.agregar.grab_focus()
        else:
            info('Debe seleccionar un proveedor')
            self.buscar_cliente.grab_focus()
        if insertado == 1 and articulos_insertados >= 1:
            self.limpiar_todo()

    def limpiar_todo(self, *args):
        self.lista.clear()
        self.venta_id.set_text('')
        self.cliente_id.set_text('')
        self.cliente.set_text('')
        fecha = date.isoformat(date.today())
        self.emision.set_text(fecha)
        self.bruto.set_text('0,00')
        self.impuestos.set_text('0,00')
        self.total.set_text('0,00')
        self.lista.clear()

    def on_salir_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()


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
        pass


if __name__ == '__main__':
    Punto().main()
