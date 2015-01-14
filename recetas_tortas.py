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

class RecetasTortas:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wRecetasTortas.glade')
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
        registros = Model().contar_registros('recetas_tortas')
        buff = "Total de recetas de tortas registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de recetas de tortas registradas: ')
        self.statusbar.push(context_id, buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([RECETAS, "Recetas de tortas", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().recetas_de_tortas_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_agregar_clicked(self,*args):
        dlg = DlgReceta()
        dlg.mezcla.set_text('0,000')
        dlg.tortas_producidas.set_text('0,00')
        dlg.costo_torta.set_text('0,00')
        dlg.bruto.set_text('0,00')
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
           Model().eliminar_receta_de_torta(codigo)
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
        l = Model().buscar_id_receta_de_torta(codigo)
        d = Model().buscar_detalles_id_receta_torta(codigo)
        self.mostrar_dialogo_con_datos(l, d)

    def mostrar_dialogo_con_datos(self, l, d):
        dlg = DlgReceta()
        if l:
            dlg.receta_torta_id.set_text(l[0])
            dlg.receta.set_text(l[1])
            dlg.articulo_id.set_text(l[2])
            dlg.articulo.set_text(l[3])
            dlg.mezcla.set_text(punto_coma(l[4]))
            dlg.peso_torta.set_text(punto_coma(l[5]))
            dlg.tortas_producidas.set_text(punto_coma(l[6]))
            dlg.costo_torta.set_text(punto_coma(l[7]))
            dlg.bruto.set_text(punto_coma(l[8]))
            dlg.mano_obra.set_text(punto_coma(l[9]))
            dlg.total.set_text(punto_coma(l[10]))
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
        builder.add_from_file("dlgRecetaTortas.glade")

        self.dialogo = builder.get_object("dialogo")
        self.receta_torta_id = builder.get_object("receta_torta_id")
        self.receta = builder.get_object("receta")
        self.articulo_id = builder.get_object("articulo_id")
        self.articulo = builder.get_object("articulo")
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcolumn0 = builder.get_object('tvcolumn0')
        self.tvcell0 = builder.get_object('tvcell0')
        self.mezcla = builder.get_object('mezcla')
        self.peso_torta = builder.get_object('peso_torta')
        self.tortas_producidas = builder.get_object('tortas_producidas')
        self.costo_torta = builder.get_object('costo_torta')
        self.bruto = builder.get_object('bruto')
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
        self.buscar_articulo.connect("clicked", self.on_buscar_articulo_clicked)
        #self.nuevo_articulo.connect ("clicked", self.on_nuevo_articulo_clicked)
        self.agregar.connect ("clicked", self.on_agregar_clicked)
        self.quitar.connect ("clicked", self.on_quitar_clicked)
        self.peso_torta.connect('value_changed', self.on_peso_torta_value_changed)
        self.mano_obra.connect('value_changed', self.on_mano_obra_value_changed)
        self.imprimir.connect ("clicked", self.on_imprimir_clicked)
        self.aceptar.connect ("clicked", self.on_aceptar_clicked)
        self.salir.connect ("clicked", self.on_salir_clicked)

        self.padre = padre
        if padre is None:
            self.padre = self.dialogo
        else:
            self.padre = self.padre.padre
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

    def on_peso_torta_value_changed(self, *args):
        self.mostrar_totales()

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
            mezcla = float(str(self.calcular_cantidad()))
            peso = float(str(coma_punto(self.peso_torta.get_text())))
            tortas = mezcla / peso
            bruto =  self.calcular_total_bruto()
            mano_obra = coma_punto(self.mano_obra.get_text())
            total = bruto + mano_obra
            costo_torta = float(total) / float(tortas)
            self.bruto.set_text(punto_coma('%.2f' % bruto))
            self.total.set_text(punto_coma('%.2f' % total))
            self.mezcla.set_text(punto_coma('%.2f' % mezcla))
            self.tortas_producidas.set_text(punto_coma('%.2f' % tortas))
            self.costo_torta.set_text(punto_coma('%.2f' % costo_torta))
        except:
            self.bruto.set_text('0,00')
            self.mano_obra.set_text('0,00')
            self.total.set_text('0,00')
            self.mezcla.set_text('0,000')
            self.tortas_producidas.set_text('0,00')
            self.costo_torta.set_text('0,00')

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.receta_torta_id.set_text('')
        self.articulo_id.set_text('')
        self.articulo.set_text('')
        self.lista.clear()
        self.mezcla.set_text('0,000')
        self.peso_torta.set_text('0,000')
        self.tortas_producidas.set_text('0,00')
        self.costo_torta.set_text('0,00')
        self.bruto.set_text('0,00')
        self.mano_obra.set_text('0,00')
        self.total.set_text('0,00')

    def limpiar(self, *args):
        self.articulo_id.set_text('')
        self.articulo.set_text('')
        self.lista.clear()
        self.mezcla.set_text('0,000')
        self.peso_torta.set_text('0,000')
        self.tortas_producidas.set_text('0,00')
        self.costo_torta.set_text('0,00')
        self.bruto.set_text('0,00')
        self.mano_obra.set_text('0,00')
        self.total.set_text('0,00')

    def campos_llenos(self, receta_torta_id, nombre, articulo_id):
        ok = 0

        if receta_torta_id == '':
            info("Debe colocar un codigo a la receta")
            return

        if nombre == '':
            info("Debe colocar un nombre a la receta")
            return

        if articulo_id == '':
            info("Debe colocar un articulo de producción")
            return

        if receta_torta_id != '' and nombre != '' and articulo_id != '':
            ok = 1
        else:
            ok = 0

        return ok

    def on_imprimir_clicked(self, *args):
        pass

    def on_aceptar_clicked(self, *args):
        receta_torta_id = self.receta_torta_id.get_text()
        nombre = self.receta.get_text()
        articulo_id = self.articulo_id.get_text()
        mezcla = coma_punto(self.mezcla.get_text())
        peso_torta = coma_punto(self.peso_torta.get_text())
        tortas_producidas = coma_punto(self.tortas_producidas.get_text())
        costo_torta = coma_punto(self.costo_torta.get_text())
        bruto = coma_punto(self.bruto.get_text())
        mano_obra = coma_punto(self.mano_obra.get_text())
        total = coma_punto(self.total.get_text())
        lleno = self.campos_llenos(receta_torta_id, nombre, articulo_id)
        filas = len(self.lista)
        existe = Model().buscar_id_receta_de_torta(receta_torta_id)
        if not existe:
            if lleno == 1 and filas >=1:
                insertado = Model().agregar_receta_de_torta(receta_torta_id, nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total)
                if insertado == 1:
                    for i in self.lista:
                        cantidad = coma_punto(i[0])
                        articulo_id = i[1]
                        total_neto = coma_punto(i[7])
                        ingredientes_insertados = Model().agregar_recetas_tortas_detalles(receta_torta_id, cantidad, articulo_id, total_neto)
                else:
                    info('No se pudo insertar la cabecera de la receta')

            if lleno ==1 and filas == 0:
                info('Debe agregar un ingrediente para la receta')
                self.agregar.grab_focus()

            if insertado == 1 and ingredientes_insertados >= 1:
                Model().establecer_costo(articulo_id, costo_torta)
                self.limpiar_todo()
        else:
            modificado = Model().modificar_receta_de_torta(nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total, receta_torta_id)

            if modificado == 1:
                info('Receta actualizada')

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
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
    RecetasTortas().main()

