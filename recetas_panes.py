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
from mensajes import info, yesno
from datetime import date, datetime
from articulos import DlgArticulo
from articulos_produccion import ArticulosEnProduccion
from modelo import Model
from comunes import punto_coma, coma_punto, caracter_a_logico, logico_a_caracter, calcular_iva_venta, calcular_precio_neto, calcular_precio_venta, calcular_utilidad


(CODIGO, RECETAS) = range(2)

rDir = os.getcwd()
os.chdir(rDir)

class Recetas:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wRecetas.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.statusbar = builder.get_object('statusbar')
        self.padre = ''
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
        registros = Model().contar_registros('recetas')
        buff = "Total de recetas registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de recetas registradas: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([RECETAS, "Recetas", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().recetas_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_agregar_clicked(self,*args):
        dlg = DlgReceta()
        dlg.masa.set_text('0,000')
        dlg.pesada.set_text('1,000')
        dlg.porciones.set_text('0')
        dlg.tacos.set_text('0,00')
        dlg.factor.set_text('1')
        dlg.panes.set_text('0,00')
        dlg.costo_pan.set_text('0,00')
        dlg.bruto.set_text('0,00')
        dlg.impuestos.set_text('0,00')
        dlg.mano_obra.set_text('0,00')
        dlg.total.set_text('0,00')

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        receta = model.get_value(it,1)

        if yesno("¿Desea eliminar la receta <b>%s</b>?\nEsta acción no se puede deshacer\n" % receta, self.padre) == gtk.RESPONSE_YES:
           Model().eliminar_receta(codigo)
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
            self.resultado = Model().buscar_id_receta(self.filtro.get_text())

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_receta(self.filtro.get_text())

        self.cargar_lista(self.resultado)

    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Recetas", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_receta(codigo)
        d = Model().buscar_detalles_id_receta(codigo)
        self.mostrar_dialogo_con_datos(l, d)

    def mostrar_dialogo_con_datos(self, l, d):
        dlg = DlgReceta()
        if l:
            dlg.receta_id.set_text(l[0])
            dlg.tipo_receta_id.set_text(l[1])
            dlg.tipo_receta.set_text(l[2])
            dlg.receta.set_text(l[3])
            dlg.articulo_id.set_text(l[4])
            dlg.articulo.set_text(l[5])
            dlg.masa.set_text(punto_coma(l[6]))
            dlg.pesada.set_text(punto_coma(l[7]))
            dlg.porciones.set_text(punto_coma(l[8]))
            dlg.tacos.set_text(punto_coma(l[9]))
            dlg.factor.set_text('1')
            dlg.peso_taco.set_text(punto_coma(l[10]))
            dlg.panes.set_text(punto_coma(l[11]))
            dlg.costo_pan.set_text(punto_coma(l[12]))
            dlg.bruto.set_text(punto_coma(l[13]))
            dlg.impuestos.set_text(punto_coma(l[14]))
            dlg.mano_obra.set_text(punto_coma(l[15]))
            dlg.total.set_text(punto_coma(l[16]))
        else:
            info('No existe la receta')
        if d:
            dlg.cargar_detalles(d)
        else:
            info('No hay ingredientes para mostrar')
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgReceta:
    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgReceta.glade")

        self.dialogo = builder.get_object("dialogo")
        self.receta_id = builder.get_object("receta_id")
        self.tipo_receta_id = builder.get_object('tipo_receta_id')
        self.tipo_receta = builder.get_object("tipo_receta")
        self.receta = builder.get_object("receta")
        self.articulo_id = builder.get_object("articulo_id")
        self.articulo = builder.get_object("articulo")
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcolumn0 = builder.get_object('tvcolumn0')
        self.tvcell0 = builder.get_object('tvcell0')
        self.masa = builder.get_object('masa')
        self.porciones = builder.get_object('porciones')
        self.pesada = builder.get_object('pesada')
        self.tacos = builder.get_object('tacos')
        self.factor = builder.get_object('factor')
        self.peso_taco = builder.get_object('peso_taco')
        self.operador = builder.get_object('operador')
        self.panes = builder.get_object('panes')
        self.costo_pan = builder.get_object('costo_pan')
        self.bruto = builder.get_object('bruto')
        self.impuestos = builder.get_object('impuestos')
        self.mano_obra = builder.get_object('mano_obra')
        self.total = builder.get_object('total')
        self.statusbar = builder.get_object('statusbar')

        self.buscar_articulo = builder.get_object('buscar_articulo')
        self.buscar_tipo_receta = builder.get_object('buscar_tipo_receta')
        #self.nuevo_articulo = builder.get_object('nuevo_articulo')
        self.agregar = builder.get_object('agregar')
        self.quitar = builder.get_object('quitar')
        self.imprimir = builder.get_object('imprimir')
        self.aceptar = builder.get_object('aceptar')
        self.salir = builder.get_object('salir')

        self.dialogo.connect("destroy", self.on_dialogo_destroy)
        self.tvcell0.connect( 'edited', self.on_tvcell0_edited_cb, self.lista )
        self.buscar_tipo_receta.connect("clicked", self.on_buscar_tipo_receta_clicked)
        self.buscar_articulo.connect("clicked", self.on_buscar_articulo_clicked)
        #self.nuevo_articulo.connect ("clicked", self.on_nuevo_articulo_clicked)
        self.agregar.connect ("clicked", self.on_agregar_clicked)
        self.quitar.connect ("clicked", self.on_quitar_clicked)
        self.pesada.connect('value_changed', self.on_pesada_value_changed)
        self.operador.connect('changed', self.on_operador_changed)
        self.factor.connect('value_changed', self.on_factor_value_changed)
        self.mano_obra.connect('value_changed', self.on_mano_obra_value_changed)
        self.imprimir.connect ("clicked", self.on_imprimir_clicked)
        self.aceptar.connect ("clicked", self.on_aceptar_clicked)
        self.salir.connect ("clicked", self.on_salir_clicked)

        self.padre = padre
        if padre is None:
            self.padre = self.dialogo
        else:
            self.padre = self.padre.padre
        self.operador.set_active(0)
        self.dialogo.show()

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        if len(codigo) >= 11:
            l = Model().buscar_id_receta(codigo)
            self.cargar_articulo(l)
        else:
            self.limpiar()

    def on_mano_obra_value_changed(self, *args):
        self.mostrar_totales()

    def on_pesada_value_changed(self, *args):
        self.mostrar_totales()

    def on_factor_value_changed(self, *args):
        self.mostrar_totales()

    def on_operador_changed(self, *args):
        self.mostrar_totales()

    def on_buscar_tipo_receta_clicked(self,*args):
        dlg = TiposDeRecetas()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.tipo_receta_id.set_text(dlg.resultado[0])
            self.tipo_receta.set_text(dlg.resultado[1])

    def on_buscar_articulo_clicked(self,*args):
        dlg = ArticulosEnProduccion()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.articulo_id.set_text(dlg.resultado[0][0])
            self.articulo.set_text(dlg.resultado[0][1])

    def on_agregar_clicked(self,*args):
        dlg = ArticulosADespachar()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_ingrediente(dlg.resultado)

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        articulo = model.get_value(it,1)

        if yesno("¿Desea eliminar el articulo <b>%s</b>?" % articulo, self.padre) == gtk.RESPONSE_YES:
           model.remove(it)

        self.mostrar_totales()

    def cargar_ingrediente(self, tupla):
        cantidad = tupla[0]
        codigo = tupla[1]
        self.lista.append([punto_coma(tupla[0]), tupla[1], tupla[2], punto_coma(tupla[3]), tupla[4], punto_coma(tupla[5]), punto_coma(tupla[6]), punto_coma(tupla[7])])
        self.tvcell0.set_property('editable', True)
        self.mostrar_totales()

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([punto_coma(tupla[f][0]), tupla[f][1], tupla[f][2], punto_coma(tupla[f][3]), tupla[f][4], punto_coma(tupla[f][5]), punto_coma(tupla[f][6]), punto_coma(tupla[f][7])])
        self.mostrar_totales()

    def on_tvcell0_edited_cb(self, cell, path, new_text, model):
        codigo = model[path][1]
        if codigo == '000002':
            model[path][0] = self.huevos_unidades_a_kg(new_text)
        else:
            model[path][0] = new_text
        nuevo_monto_neto = coma_punto(model[path][0]) * coma_punto(model[path][3])
        model[path][7] = punto_coma(nuevo_monto_neto)
        nuevo_iva = coma_punto(model[path][3])/100 * coma_punto(model[path][7])
        model[path][6] = punto_coma(nuevo_iva)
        self.mostrar_totales()
        return

    def huevos_unidades_a_kg(self, unidades):
        kg = 0
        try:
            kg = float(unidades) * 0.050
        except:
            kg = 0
        return punto_coma(kg)

    def calcular_total_bruto(self, *args):
        subtotal = 0
        try:
            for i in self.lista:
                subtotal += coma_punto(i[7])
        except:
            subtotal = 0
        return subtotal

    def calcular_cantidad(self, *args):
        cantidad = 0
        try:
            for i in self.lista:
                cantidad += coma_punto(i[0])
        except:
            cantidad = 0
        return cantidad

    def calcular_iva(self, *args):
        iva = 0
        try:
            for i in self.lista:
                iva += coma_punto(i[6])
        except:
            iva = 0
        return iva

    def mostrar_totales(self, *args):
        try:
            masa = float(str(self.calcular_cantidad()))
            pesadas = float(str(coma_punto(self.pesada.get_text())))
            porciones = masa / pesadas
            tacos = porciones * 36
            peso_taco = masa / tacos
            factor = coma_punto(self.factor.get_text())
            if self.operador.get_active() == 0:
                panes = tacos * float(factor)
            else:
                panes = tacos / float(factor)
            bruto =  self.calcular_total_bruto()
            impuestos = self.calcular_iva()
            mano_obra = coma_punto(self.mano_obra.get_text())
            total = bruto + impuestos + mano_obra
            costo_pan = float(total) / float(panes)
            self.bruto.set_text(punto_coma('%.2f' % bruto))
            self.impuestos.set_text(punto_coma('%.2f' % impuestos))
            self.total.set_text(punto_coma('%.2f' % total))
            self.masa.set_text(punto_coma('%.2f' % masa))
            self.porciones.set_text(punto_coma('%.2f' % porciones))
            self.tacos.set_text(punto_coma('%.2f' % tacos))
            self.peso_taco.set_text(punto_coma('%.3f' % peso_taco))
            self.panes.set_text(punto_coma('%.2f' % panes))
            self.costo_pan.set_text(punto_coma('%.2f' % costo_pan))
        except:
            self.bruto.set_text('0,00')
            self.impuestos.set_text('0,00')
            self.mano_obra.set_text('0,00')
            self.total.set_text('0,00')
            self.masa.set_text('0,00')
            self.pesada.set_text('0,00')
            self.porciones.set_text('0,00')
            self.tacos.set_text('0,00')
            self.peso_taco.set_text('0,00')
            self.panes.set_text('0,00')
            self.costo_pan.set_text('0,00')

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.receta_id.set_text('')
        self.tipo_receta_id.set_text('')
        self.tipo_receta.set_text('')
        self.articulo_id.set_text('')
        self.articulo.set_text('')
        self.lista.clear()
        self.masa.set_text('0,000')
        self.pesada.set_text('1,000')
        self.porciones.set_text('0,00')
        self.tacos.set_text('0,00')
        self.peso_taco.set_text('0,00')
        self.panes.set_text('0,00')
        self.costo_pan.set_text('0,00')
        self.bruto.set_text('0,00')
        self.impuestos.set_text('0,00')
        self.mano_obra.set_text('0,00')
        self.total.set_text('0,00')

    def limpiar(self, *args):
        self.tipo_receta_id.set_text('')
        self.tipo_receta.set_text('')
        self.articulo_id.set_text('')
        self.articulo.set_text('')
        self.lista.clear()
        self.masa.set_text('0,000')
        self.pesada.set_text('1,000')
        self.porciones.set_text('0,00')
        self.tacos.set_text('0,00')
        self.peso_taco.set_text('0,00')
        self.panes.set_text('0,00')
        self.costo_pan.set_text('0,00')
        self.bruto.set_text('0,00')
        self.impuestos.set_text('0,00')
        self.mano_obra.set_text('0,00')
        self.total.set_text('0,00')

    def campos_llenos(self, receta_id, tipo_receta_id, nombre, articulo_id, mano_obra):
        ok = 0

        if receta_id == '':
            info("Debe colocar un codigo a la receta")
            return

        if tipo_receta_id == '':
            info("Debe seleccionar una categoria de la receta")
            return

        if nombre == '':
            info("Debe colocar un nombre a la receta")
            return

        if articulo_id == '':
            info("Debe colocar un articulo de producción")
            return

        if mano_obra == 0.00 or mano_obra == '':
            info("Debe colocar el costo de la mano de obra")
            return

        if receta_id != '' and tipo_receta_id !='' and nombre != '' and articulo_id != '' and mano_obra != 0:
            ok = 1
        else:
            ok = 0

        return ok

    def on_imprimir_clicked(self, *args):
        pass

    def on_aceptar_clicked(self, *args):
        receta_id = self.receta_id.get_text()
        nombre = self.receta.get_text()
        tipo_receta_id = self.tipo_receta_id.get_text()
        articulo_id = self.articulo_id.get_text()
        masa = coma_punto(self.masa.get_text())
        pesada = coma_punto(self.pesada.get_text())
        porciones = coma_punto(self.porciones.get_text())
        tacos = coma_punto(self.tacos.get_text())
        peso_taco = coma_punto(self.peso_taco.get_text())
        panes = coma_punto(self.panes.get_text())
        costo = coma_punto(self.costo_pan.get_text())
        bruto = coma_punto(self.bruto.get_text())
        impuestos = coma_punto(self.impuestos.get_text())
        mano_obra = coma_punto(self.mano_obra.get_text())
        total = coma_punto(self.total.get_text())
        mano_obra = coma_punto(self.mano_obra.get_text())
        lleno = self.campos_llenos(receta_id, tipo_receta_id, nombre, articulo_id, mano_obra)
        filas = len(self.lista)

        existe = Model().buscar_id_receta(receta_id)
        if not existe:
            if lleno == 1 and filas >=1:
                insertado = Model().agregar_receta(receta_id, nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total)
                for i in self.lista:
                    cantidad = coma_punto(i[0])
                    articulo_id = i[1]
                    total_neto = coma_punto(i[7])
                    ingredientes_insertados = Model().agregar_recetas_detalles(receta_id, cantidad, articulo_id, total_neto)

            if lleno ==1 and filas == 0:
                info('Debe agregar un ingrediente para la receta')
                self.agregar.grab_focus()

            if insertado == 1 and ingredientes_insertados >= 1:
                Model().establecer_costo(articulo_id, costo_pan)
                self.limpiar_todo()
        else:
            modificado = Model().modificar_receta(nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total, receta_id)

            if modificado == 1:
                info('Receta actualizada')

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

class TiposDeRecetas:

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('wLista_De_Tipos_De_Recetas.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.resultado = ''

        self.statusbar = builder.get_object('statusbar')

        self.lista_ordenada_por_id()
        self.dialogo.show()
        self.on_buscar_clicked()
        self.criterio.set_active(0)

    def mostrar_status(self, filas):
        buff = "Total de tipos de recetas registradas: %s" % filas
        context_id = self.statusbar.get_context_id('Total de tipos de recetas registradas: ')
        self.statusbar.push(context_id,buff)

    def lista_ordenada_por_id(self, *args):
        self.cargar_lista(Model().tipos_de_recetas_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        filas = len(tupla)
        self.mostrar_status(filas)
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

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
        if  criterio == 0 or criterio == 1:
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

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.dialogo.hide()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_id_tipo_receta(codigo)
        if self.resultado:
            self.dialogo.destroy()

class ArticulosADespachar:
    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('wArticulos_Compra.glade')
        builder.connect_signals(self)

        self.dialogo = builder.get_object('dialogo')
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.resultado = ''

        self.statusbar = builder.get_object('statusbar')

        self.lista_ordenada_por_id()
        self.dialogo.show()
        self.on_buscar_clicked()
        self.criterio.set_active(0)

    def mostrar_status(self, filas):
        buff = "Total de artículos como materia prima registrados: %s" % filas
        context_id = self.statusbar.get_context_id('Total de artículos como materia prima registrados: ')
        self.statusbar.push(context_id,buff)

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().solo_materia_prima())

    def cargar_lista(self, tupla):
        self.lista.clear()
        filas = len(tupla)
        self.mostrar_status(filas)
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1],punto_coma(tupla[f][18]),punto_coma(tupla[f][13]),punto_coma(tupla[f][17])])

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
        if  criterio == 0 or criterio == 1:
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

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.dialogo.hide()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        self.resultado = Model().buscar_articulo_pedido(codigo)
        if self.resultado:
            self.dialogo.destroy()

if __name__ == '__main__':
    Recetas().main()

