#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       articulos.py
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
import printInventario
from datetime import date
from mensajes import info, yesno
from depositos import DlgDeposito
from articulo_proveedor import ArticulosAsociadosAProveedores
from grupos import DlgGrupo
from modelo import Model
from comunes import punto_coma, coma_punto, caracter_a_logico, logico_a_caracter, calcular_iva_venta, calcular_precio_neto, calcular_precio_venta, calcular_utilidad


(CODIGO, ARTICULO, EXISTENCIA, PRECIO) = range(4)

(CODIGO, ARTICULO, EXISTENCIA, PRECIO, TOTAL) = range(5)

rDir = os.getcwd()
os.chdir(rDir)

class Articulos:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos.glade')
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
            self.padre = self.ventana
        else:
            self.padre = self.padre.frm_padre

        self.crear_columnas()
        self.lista_ordenada_por_id()
        self.mostrar_status()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('articulos')
        buff = "Total de artículos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de artículos registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([ARTICULO, "Articulo", str])
        columnas.append ([EXISTENCIA, "Existencia", str])
        columnas.append ([PRECIO, "Precio de Venta", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().articulos_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][18]),punto_coma(tupla[f][17])])

    def on_agregar_clicked(self,*args):
        dlg = DlgArticulo(self.padre, False)
        dlg.iva_compra.set_text('12,00')
        dlg.iva_venta.set_text('12,00')
        dlg.usa_existencia.set_active(True)
        dlg.foto.set_from_file('')
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        articulo = model.get_value(it,1)

        if yesno("¿Desea eliminar el articulo <b>%s</b>?\nEsta acción no se puede deshacer\n" % articulo, self.padre) == gtk.RESPONSE_YES:
           Model().eliminar_articulo(codigo)
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
            self.resultado = Model().buscar_id_articulo(self.filtro.get_text())

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_articulo(self.filtro.get_text())

        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Articulos", self.col_data)
        t.show()

    def on_inventario_clicked(self, *args):
        InventarioValorizado()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_articulo(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, t):
        dlg = DlgArticulo(self.padre, False)
        dlg.editando = True
        dlg.codigo.set_text(t[0][0])
        dlg.codigo.set_editable(False)
        dlg.articulo.set_text(t[0][1])
        dlg.articulo.grab_focus()
        dlg.grupo_id.set_text(t[0][2])
        dlg.grupo.set_text(t[0][3])
        dlg.deposito_id.set_text(t[0][4])
        dlg.deposito.set_text(t[0][5])
        dlg.marca.set_text(t[0][6])
        dlg.descripcion.set_text(t[0][7])
        dlg.unidad.set_text(t[0][8])
        dlg.iva_compra.set_text(punto_coma(t[0][9]))
        dlg.iva_venta.set_text(punto_coma(t[0][10]))
        dlg.costo_anterior.set_text(punto_coma(t[0][11]))
        dlg.costo_promedio.set_text(punto_coma(t[0][12]))
        dlg.costo_actual.set_text(punto_coma(t[0][13]))
        dlg.utilidad.set_text(punto_coma(t[0][14]))
        dlg.precio_neto.set_text(punto_coma(t[0][15]))
        dlg.monto_iva_venta.set_text(punto_coma(t[0][16]))
        dlg.precio_venta.set_text(punto_coma(t[0][17]))
        dlg.existencia.set_text(punto_coma(t[0][18]))
        dlg.existencia_min.set_text(punto_coma(t[0][19]))
        dlg.existencia_max.set_text(punto_coma(t[0][20]))
        dlg.usa_existencia.set_active(caracter_a_logico(t[0][21]))
        dlg.exento_iva.set_active(caracter_a_logico(t[0][22]))
        dlg.uso_interno.set_active(caracter_a_logico(t[0][23]))
        dlg.produccion.set_active(caracter_a_logico(t[0][24]))
        dlg.foto.set_from_file(unicode(t[0][25]))

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgArticulo:
    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgArticulo2.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.articulo = builder.get_object("articulo")
        self.grupo_id = builder.get_object("grupo_id")
        self.grupo = builder.get_object('grupo')
        self.deposito_id = builder.get_object("deposito_id")
        self.deposito = builder.get_object("deposito")
        self.marca = builder.get_object('marca')
        self.descripcion = builder.get_object('descripcion')
        self.iva = builder.get_object('iva')
        self.iva_venta = builder.get_object('iva_venta')
        self.iva_compra = builder.get_object('iva_compra')
        self.costo_anterior = builder.get_object('costo_anterior')
        self.costo_promedio = builder.get_object('costo_promedio')
        self.costo_actual = builder.get_object('costo_actual')
        self.utilidad = builder.get_object('utilidad')
        self.precio_neto = builder.get_object('precio_neto')
        self.monto_iva_venta = builder.get_object('monto_iva_venta')
        self.precio_venta = builder.get_object('precio_venta')
        self.existencia = builder.get_object("existencia")
        self.existencia_min = builder.get_object("existencia_min")
        self.existencia_max = builder.get_object("existencia_max")
        self.usa_existencia = builder.get_object("usa_existencia")
        self.exento_iva = builder.get_object("exento_iva")
        self.uso_interno = builder.get_object("uso_interno")
        self.produccion = builder.get_object('produccion')
        self.unidad = builder.get_object('unidad')
        self.ajuste_iva_venta = builder.get_object('ajuste_iva_venta')
        self.ajuste_iva_compra = builder.get_object('ajuste_iva_compra')
        self.ajuste_min = builder.get_object('ajuste_min')
        self.ajuste_max = builder.get_object('ajuste_max')
        self.filechooserbutton = builder.get_object('filechooserbutton')
        self.foto = builder.get_object('foto')
        self.ruta = ''
        self.padre = padre

        self.dialogo.show()

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        if len(codigo) >= 11:
            l = Model().buscar_id_articulo(codigo)
            self.cargar_articulo(l)
        else:
            self.limpiar()

    def cargar_articulo(self, t):
        self.codigo.set_text(t[0][0])
        self.codigo.set_editable(False)
        self.articulo.set_text(t[0][1])
        self.articulo.grab_focus()
        self.grupo_id.set_text(t[0][2])
        self.grupo.set_text(t[0][3])
        self.deposito_id.set_text(t[0][4])
        self.deposito.set_text(t[0][5])
        self.marca.set_text(t[0][6])
        self.descripcion.set_text(t[0][7])
        self.unidad.set_text(t[0][8])
        self.iva_compra.set_text(punto_coma(t[0][9]))
        self.iva_venta.set_text(punto_coma(t[0][10]))
        self.costo_anterior.set_text(punto_coma(t[0][11]))
        self.costo_promedio.set_text(punto_coma(t[0][12]))
        self.costo_actual.set_text(punto_coma(t[0][13]))
        self.utilidad.set_text(punto_coma(t[0][14]))
        self.precio_neto.set_text(punto_coma(t[0][15]))
        self.iva_venta.set_text(punto_coma(t[0][16]))
        self.precio_venta.set_text(punto_coma(t[0][17]))
        self.existencia.set_text(punto_coma(t[0][18]))
        self.existencia_min.set_text(punto_coma(t[0][19]))
        self.existencia_max.set_text(punto_coma(t[0][20]))
        self.usa_existencia.set_active(caracter_a_logico(t[0][21]))
        self.exento_iva.set_active(caracter_a_logico(t[0][22]))
        self.uso_interno.set_active(caracter_a_logico(t[0][23]))
        self.produccion.set_active(caracter_a_logico(t[0][24]))
        self.foto.set_from_file(unicode(t[0][25]))

    def on_grupo_id_changed(self, *args):
        codigo = self.grupo_id.get_text()
        l = Model().buscar_id_grupo(codigo)
        if l:
            self.grupo.set_text(l[0][1])
        else:
            self.grupo.set_text('')

    def on_deposito_id_changed(self, *args):
        codigo = self.deposito_id.get_text()
        l = Model().buscar_id_deposito(codigo)
        if l:
            deposito = l[0][1]
            if deposito == 'Producción':
                self.produccion.set_active(True)
                self.usa_existencia.set_active(False)
                self.costo_actual.set_text('1,00')
            else:
                self.produccion.set_active(False)
            self.deposito.set_text(l[0][1])
        else:
            self.deposito.set_text('')

    def on_buscar_grupo_clicked(self,*args):
        dlg = DlgBuscarGrupoArticulo()
        dlg.dialogo.run()
        if dlg.resultado:
            self.grupo_id.set_text(dlg.resultado[0][0])
            self.grupo.set_text(dlg.resultado[0][1])

    def on_buscar_deposito_clicked(self,*args):
        dlg = DlgBuscarDepositoArticulo()
        dlg.dialogo.run()
        if dlg.resultado:
            self.deposito_id.set_text(dlg.resultado[0][0])
            self.deposito.set_text(dlg.resultado[0][1])

    def on_proveedores_clicked(self,*args):
        articulo_id = self.codigo.get_text()
        articulo = self.articulo.get_text()
        if articulo_id:
            ArticulosAsociadosAProveedores(articulo_id, articulo)
        else:
            info('Debe colocarle un código al artículo')

    def on_costos_clicked(self,*args):
        articulo_id = self.codigo.get_text()
        articulo = self.articulo.get_text()
        if articulo_id:
            wCostosPorArticulo(articulo_id, articulo)
        else:
            info('Debe colocarle un código al artículo')

    def on_nuevo_grupo_clicked(self,*args):
        dlg = DlgGrupo()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_nuevo_deposito_clicked(self,*args):
        dlg = DlgDeposito()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_iva_venta_value_changed(self, *args):
        self.precio_neto.set_text(calcular_precio_neto( self.costo_actual.get_text(), self.utilidad.get_text()))
        self.precio_venta.set_text(calcular_precio_venta(self.iva_venta.get_text(), self.costo_actual.get_text(), self.utilidad.get_text()))
        self.monto_iva_venta.set_text(calcular_iva_venta(self.iva_venta.get_text(), self.precio_neto.get_text(), self.precio_venta.get_text()))

    def on_utilidad_value_changed(self, *args):
        if  self.costo_actual != '0,00':
            self.precio_neto.set_text(calcular_precio_neto( self.costo_actual.get_text(), self.utilidad.get_text()))
            self.precio_venta.set_text(calcular_precio_venta(self.iva_venta.get_text(), self.costo_actual.get_text(), self.utilidad.get_text()))
            self.iva_venta.set_text(calcular_iva_venta(self.iva_venta.get_text(), self.precio_neto.get_text(), self.precio_venta.get_text()))

    def on_precio_venta_value_changed(self, *args):
        if self.costo_actual != '0,00' and self.precio_venta.get_text() != '0,00':
            utilidad = calcular_utilidad(self.costo_actual.get_text(), self.precio_venta.get_text())
            self.utilidad.set_text(utilidad)
            precio_neto1 = calcular_precio_neto(self.costo_actual.get_text(), utilidad)
            iva_venta = calcular_iva_venta(self.iva_venta.get_text(), precio_neto1, self.precio_venta.get_text())
            precio_neto = coma_punto(self.precio_venta.get_text()) - coma_punto(iva_venta)
            self.precio_neto.set_text(punto_coma(precio_neto))
            self.utilidad.set_text(calcular_utilidad(self.costo_actual.get_text(), self.precio_neto.get_text()))
            self.iva_venta.set_text(iva_venta)

    def on_filechooserbutton_file_set(self, *args):
        self.ruta = unicode(self.filechooserbutton.get_filename())
        self.foto.set_from_file(self.ruta)

    def on_usa_existencia_toggled(self, *args):
        activo = self.usa_existencia.get_active()
        if activo == True:
            self.existencia_min.set_adjustment(self.ajuste_min)
            self.existencia_max.set_adjustment(self.ajuste_max)
            self.existencia_min.set_editable(True)
            self.existencia_max.set_editable(True)
        else:
            self.existencia_min.set_text('0,00')
            self.existencia_max.set_text('0,00')
            self.existencia_min.set_editable(False)
            self.existencia_max.set_editable(False)
            ajuste = gtk.Adjustment(0,0,0,0,0,0)
            self.existencia_min.set_adjustment(ajuste)
            self.existencia_max.set_adjustment(ajuste)

    def on_exento_iva_toggled(self, *args):
        activo = self.exento_iva.get_active()
        if activo == True:
            self.iva_compra.set_text('0,00')
            self.iva_venta.set_text('0,00')
            self.on_iva_venta_value_changed()
            self.iva_compra.set_editable(False)
            self.iva_venta.set_editable(False)
            ajuste = gtk.Adjustment(0,0,0,0,0,0)
            self.iva_compra.set_adjustment(ajuste)
            self.iva_venta.set_adjustment(ajuste)
        else:
            self.iva_venta.set_adjustment(self.ajuste_iva_venta)
            self.iva_compra.set_adjustment(self.ajuste_iva_compra)
            self.iva_compra.set_text('12,00')
            self.iva_venta.set_text('12,00')
            self.on_iva_venta_value_changed()
            self.iva_compra.set_editable(True)
            self.iva_venta.set_editable(True)

    def on_guardar_clicked(self, *args):
        articulo_id = self.codigo.get_text()
        nombre = self.articulo.get_text()
        grupo_id = self.grupo_id.get_text()
        deposito_id = self.deposito_id.get_text()
        marca = self.marca.get_text()
        descripcion = self.descripcion.get_text()
        unidad = self.unidad.get_text()
        iva_compra = coma_punto(self.iva_compra.get_text())
        iva_venta = coma_punto(self.iva_venta.get_text())
        costo_anterior = coma_punto(self.costo_anterior.get_text())
        costo_promedio = coma_punto(self.costo_promedio.get_text())
        costo_actual = coma_punto(self.costo_actual.get_text())
        utilidad = coma_punto(self.utilidad.get_text())
        precio_neto = coma_punto(self.precio_neto.get_text())
        monto_iva_venta = coma_punto(self.monto_iva_venta.get_text())
        precio_venta = coma_punto(self.precio_venta.get_text())
        existencia = coma_punto(self.existencia.get_text())
        existencia_min = coma_punto(self.existencia_min.get_text())
        existencia_max = coma_punto(self.existencia_max.get_text())
        usa_existencia = logico_a_caracter(self.usa_existencia.get_active())
        exento_iva = logico_a_caracter(self.exento_iva.get_active())
        uso_interno = logico_a_caracter(self.uso_interno.get_active())
        produccion = logico_a_caracter(self.produccion.get_active())
        foto = self.ruta
        if exento_iva == 'si':
            iva_compra = 0.00
            iva_venta = 0.00
        if not foto:
            foto = ''
        if produccion == 'si':
            existencia_min = 1
            existencia_max = 1
        lleno = self.campos_llenos(articulo_id, nombre, deposito_id, grupo_id)

        if lleno == 1 and not self.editando:
            Model().agregar_articulo(articulo_id, nombre, grupo_id, deposito_id, marca, descripcion,
                                        unidad, iva_compra, iva_venta, costo_anterior, costo_promedio,
                                        costo_actual, utilidad, precio_neto, monto_iva_venta,precio_venta,
                                        existencia, existencia_min, existencia_max, usa_existencia,
                                        exento_iva, uso_interno, produccion, foto)
            self.limpiar_todo()
            self.codigo.grab_focus()

        if lleno == 1 and self.editando:
            Model().modificar_articulo(articulo_id, nombre, grupo_id, deposito_id, marca, descripcion,
                                        unidad, iva_compra, iva_venta, costo_anterior, costo_promedio,
                                        costo_actual, utilidad, precio_neto, monto_iva_venta, precio_venta,
                                        existencia, existencia_min, existencia_max, usa_existencia,
                                        exento_iva, uso_interno, produccion, foto)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, articulo_id, nombre, deposito_id, grupo_id) :
        ok = 0

        if articulo_id == '':
            info("Debe colocar un codigo al artículo")
            return

        if nombre == '':
            info("Debe colocar un nombre al artículo")
            reurn

        if deposito_id == '':
            info("Debe seleccionar un depósito para el artículo")
            return

        if grupo_id == '':
            info('Debe seleccionar un grupo de inventario para el artículo')
            return

        if articulo_id != '' and nombre !='' and deposito_id != '' and grupo_id != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text('')
        self.articulo.set_text('')
        self.grupo_id.set_text('')
        self.grupo.set_text('')
        self.deposito_id.set_text('')
        self.deposito.set_text('')
        self.marca.set_text('')
        self.descripcion.set_text('')
        self.unidad.set_text('')
        self.iva_compra.set_text('12,00')
        self.iva_venta.set_text('12,00')
        self.costo_anterior.set_text('0,00')
        self.costo_promedio.set_text('0,00')
        self.costo_actual.set_text('0,00')
        self.utilidad.set_text('0,00')
        self.precio_neto.set_text('0,00')
        self.precio_neto.set_text('0,00')
        self.precio_venta.set_text('0,00')
        self.existencia.set_text('0,000')
        self.existencia_min.set_text('0,000')
        self.existencia_max.set_text('0,000')
        self.usa_existencia.set_active(False)
        self.exento_iva.set_active(False)
        self.uso_interno.set_active(False)
        self.produccion.set_active(False)
        self.foto.get_from_file('')

    def limpiar(self, *args):
        self.articulo.set_text('')
        self.grupo_id.set_text('')
        self.grupo.set_text('')
        self.deposito_id.set_text('')
        self.deposito.set_text('')
        self.marca.set_text('')
        self.descripcion.set_text('')
        self.unidad.set_text('')
        self.iva_compra.set_text('12,00')
        self.iva_venta.set_text('12,00')
        self.costo_anterior.set_text('0,00')
        self.costo_promedio.set_text('0,00')
        self.costo_actual.set_text('0,00')
        self.utilidad.set_text('0,00')
        self.precio_neto.set_text('0,00')
        self.iva_venta.set_text('0,00')
        self.precio_neto.set_text('0,00')
        self.precio_venta.set_text('0,00')
        self.existencia.set_text('0,000')
        self.existencia_min.set_text('0,000')
        self.existencia_max.set_text('0,000')
        self.usa_existencia.set_active(False)
        self.exento_iva.set_active(False)
        self.uso_interno.set_active(False)
        self.produccion.set_active(False)
        self.foto.set_from_file('')


class DlgBuscarGrupoArticulo:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Grupo_Articulo.glade")
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
        c = Model().grupos_ordenados_por_id()
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
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_grupo(id)
        self.on_dialogo_destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_grupo(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_grupo(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            mensajes.info('Debe seleccionar un criterio de búsqueda')
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

class DlgBuscarDepositoArticulo:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Deposito_Articulo.glade")
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
        c = Model().depositos_ordenados_por_id()
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
            self.lblValor.set_text('Depósito')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_deposito(id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_deposito(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_deposito(self.valor.get_text())
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

class InventarioValorizado:

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wInventario_Simple.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.lblMes = builder.get_object('lblMes')
        self.mes = builder.get_object('mes')
        self.lblYear = builder.get_object('lblYear')
        self.anno = builder.get_object("year")
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.total = builder.get_object('total')

        self.padre = padre
        if padre is None:
            self.padre = self.ventana
        else:
            self.padre = self.padre.frm_padre

        self.crear_columnas()
        self.lista_ordenada_por_id()
        self.ventana.show()

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", "str"])
        columnas.append ([ARTICULO, "Articulo", "str"])
        columnas.append ([EXISTENCIA, "Existencia Actual", "int"])
        columnas.append ([PRECIO, "Precio Unitario", "int"])
        columnas.append ([TOTAL, "Total", "int"])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self, *args):
        self.cargar_lista(Model().inventario_simple())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1], punto_coma(tupla[f][2]), punto_coma(tupla[f][3]), punto_coma(tupla[f][4])])
        self.mostrar_total()

    def calcular_total(self, *args):
        total = 0
        try:
            for i in self.lista:
                total += coma_punto(i[4])
        except:
            total = 0
        return total

    def mostrar_total(self, *args):
        try:
            total = float(str(self.calcular_total()))
            self.total.set_text(punto_coma('%.2f' % total))
        except:
            self.total.set_text('0,00')

    def on_buscar_clicked(self,*args):
        lblYear = self.lblYear.get_visible()
        anno = self.anno.get_visible()
        lblMes = self.lblMes.get_visible()
        mes = self.mes.get_visible()

        if anno == False and lblYear == False and lblMes == False:
            self.lblYear.set_visible(True)
            self.lblMes.set_visible(True)
            self.mes.set_visible(True)
            self.anno.set_visible(True)
            hoy = date.today()
            self.anno.set_text(str(hoy.year))
            self.mes.grab_focus()
        else:
            self.lblYear.set_visible(False)
            self.lblMes.set_visible(False)
            self.mes.set_visible(False)
            self.anno.set_visible(False)
            self.mes.grab_focus()

    def on_mes_changed(self, *args):
        if self.mes.get_active() == 0:
            self.resultado = Model().buscar_inventario_enero(self.anno.get_text())
        elif self.mes.get_active() == 1:
            self.resultado = Model().buscar_inventario_febrero(self.anno.get_text())
        elif self.mes.get_active() == 2:
            self.resultado = Model().buscar_inventario_marzo(self.anno.get_text())
        elif self.mes.get_active() == 3:
            self.resultado = Model().buscar_inventario_abril(self.anno.get_text())
        elif self.mes.get_active() == 4:
            self.resultado = Model().buscar_inventario_mayo(self.anno.get_text())
        elif self.mes.get_active() == 5:
            self.resultado = Model().buscar_inventario_junio(self.anno.get_text())
        elif self.mes.get_active() == 6:
            self.resultado = Model().buscar_inventario_julio(self.anno.get_text())
        elif self.mes.get_active() == 7:
            self.resultado = Model().buscar_inventario_agosto(self.anno.get_text())
        elif self.mes.get_active() == 8:
            self.resultado = Model().buscar_inventario_septiembre(self.anno.get_text())
        elif self.mes.get_active() == 9:
            self.resultado = Model().buscar_inventario_octubre(self.anno.get_text())
        elif self.mes.get_active() == 10:
            self.resultado = Model().buscar_inventario_noviembre(self.anno.get_text())
        elif self.mes.get_active() == 11:
            self.resultado = Model().buscar_inventario_diciembre(self.anno.get_text())
        self.cargar_lista(self.resultado)

    def on_imprimir_clicked(self,*args):
        t = printInventario.InventarioHTML(self.total.get_text(), self.tree,"Reporte de Inventario", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()


class ArticulosConExistenciaMinima():

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos.glade')
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
            self.padre = self.ventana
        else:
            self.padre = self.padre.frm_padre

        self.crear_columnas()
        self.lista_ordenada_por_id()
        self.mostrar_status()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('articulos')
        buff = "Total de artículos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de artículos registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([ARTICULO, "Articulo", str])
        columnas.append ([EXISTENCIA, "Existencia", str])
        columnas.append ([PRECIO, "Precio de Venta", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().todos_los_articulos_con_existencia_minima())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][18]),punto_coma(tupla[f][17])])

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Articulos para Comprar", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

class MateriaPrimaYLimpiezaConExistenciaMinima():

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos.glade')
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
            self.padre = self.ventana
        else:
            self.padre = self.padre.frm_padre

        self.crear_columnas()
        self.lista_ordenada_por_id()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('articulos')
        buff = "Total de artículos registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de artículos registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([ARTICULO, "Articulo", str])
        columnas.append ([EXISTENCIA, "Existencia", str])
        columnas.append ([PRECIO, "Precio de Venta", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        lista = Model().materia_prima_y_limpieza_con_existencia_minima()
        self.cargar_lista(lista)

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][18]),punto_coma(tupla[f][17])])

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Articulos", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

if __name__ == '__main__':
    Articulos().main()

