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
from articulos_a_despachar import ArticulosADespachar
from total_despachado_diario import TotalDespachado
from despachos import DlgDespacho
from modelo import Model
from comunes import punto_coma, coma_punto, caracter_a_logico, logico_a_caracter, calcular_iva_venta, calcular_precio_neto, calcular_precio_venta, calcular_utilidad, kg_a_arroba, kg_a_bultos, arroba_a_kg


(CODIGO, PRODUCCION, FECHA, ESTADO, CANTIDAD_HARINA, COSTOS) = range(6)

rDir = os.getcwd()
os.chdir(rDir)

class ProduccionPasteleria:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wProduccion.glade')
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
        registros = Model().contar_registros('produccion')
        buff = "Total de producciones registradas: %s" % registros
        context_id = self.statusbar.get_context_id('Total de producciones registradas: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([PRODUCCION, "Produccion", str])
        columnas.append ([FECHA, "Fecha", str])
        columnas.append ([ESTADO, "Estado", str])
        columnas.append ([CANTIDAD_HARINA, "Cantidad de Harina", str])
        columnas.append ([COSTOS, "Costos", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().producciones_ordenadas_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        if tupla:
            for f in range(len(tupla)):
                self.lista.append([tupla[f][0],tupla[f][1], tupla[f][2], tupla[f][3]])
        else:
            info('No hay registros en produccion')

    def on_agregar_clicked(self,*args):
        dlg = DlgProduccionPasteleria()
        dlg.fecha.set_text(str(date.today()))
        dlg.estado.set_text('Sin procesar')
        dlg.harina_arroba.set_text('0,000')
        dlg.harina_kg.set_text('0,000')
        dlg.harina_bultos.set_text('0,000')
        dlg.costos.set_text('0,00')

        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = int(model.get_value(it,0))
        if yesno("¿Desea eliminar la produccion con código <b>%s</b>?\nEsta acción no se puede deshacer\n" % codigo, self.padre) == gtk.RESPONSE_YES:
           Model().eliminar_produccion(codigo)
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

    def on_despachado_clicked(self, *args):
        TotalDespachado()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_produccion(codigo)
        d = Model().buscar_detalles_id_produccion(codigo)
        self.mostrar_dialogo_con_datos(l, d)

    def mostrar_dialogo_con_datos(self, l, d):
        dlg = DlgProduccion()
        if l:
            dlg.produccion_id.set_text(str(l[0]))
            dlg.fecha.set_text(str(l[1]))
            dlg.estado.set_text(l[2])
            dlg.harina_arroba.set_text(punto_coma(l[3]))
            dlg.harina_kg.set_text(punto_coma(l[4]))
            dlg.harina_bultos.set_text(punto_coma(l[5]))
            dlg.costos.set_text(punto_coma(l[6]))
        else:
            info('No existe registro de producción')
        if d:
            dlg.cargar_detalles(d)
        else:
            info('No hay recetas registradas en la producción')
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgProduccionPasteleria:
    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgProduccionTortas.glade")

        self.dialogo = builder.get_object("dialogo")
        self.produccion_id = builder.get_object("produccion_id")
        self.fecha = builder.get_object("fecha")
        self.estado = builder.get_object("estado")
        self.harina_arroba = builder.get_object("harina_arroba")
        self.harina_kg = builder.get_object("harina_kg")
        self.harina_bultos = builder.get_object("harina_bultos")
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.tvcolumn2 = builder.get_object('tvcolumn2')
        self.tvcell2 = builder.get_object('tvcell2')
        self.costos = builder.get_object('costos')
        self.statusbar = builder.get_object('statusbar')
        self.agregar_receta_torta = builder.get_object('agregar_receta_torta')
        self.quitar_receta_torta = builder.get_object('quitar_receta_torta')
        self.limpiar_recetas_torta = builder.get_object('limpiar_recetas_torta')
        self.codigo = 0

        # Create a combobox column para empleados
        self.lsmodelo = gtk.ListStore(str)

        self.cellcombo = gtk.CellRendererCombo()

        self.cellcombo.set_property("text-column", 0)
        self.cellcombo.set_property("editable", True)
        self.cellcombo.set_property("has-entry", False)
        self.cellcombo.set_property("model", self.lsmodelo)
        self.tvcolumn5 = gtk.TreeViewColumn("Encargado de la elaboración", self.cellcombo, text=5)
        self.tree.append_column(self.tvcolumn5)

        self.imprimir = builder.get_object('imprimir')
        self.aceptar = builder.get_object('aceptar')
        self.salir = builder.get_object('salir')

        self.dialogo.connect("destroy", self.on_dialogo_destroy)
        self.tvcell2.connect( 'edited', self.on_tvcell2_edited_cb, self.lista )
        self.cellcombo.connect("edited", self.on_cellcombo_edited)
        self.agregar_receta_torta.connect("clicked", self.on_agregar_receta_torta_clicked)
        self.quitar_receta_torta.connect("clicked", self.on_quitar_receta_torta_clicked)
        self.limpiar_recetas_torta.connect("clicked", self.on_limpiar_recetas_torta_clicked)
        self.imprimir.connect("clicked", self.on_imprimir_clicked)
        self.aceptar.connect("clicked", self.on_aceptar_clicked)
        self.salir.connect("clicked", self.on_salir_clicked)

        self.padre = padre
        if padre is None:
            self.padre = self.dialogo
        else:
            self.padre = self.padre.padre

        self.cargar_combo()
        self.dialogo.show()

    def cargar_combo(self, *args):
        lista = Model().pasteleros_ordenados_por_id()
        for f in range(len(lista)):
            self.lsmodelo.append([lista[f][0]])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        if len(codigo) >= 11:
            l = Model().buscar_id_produccion(codigo)
            self.cargar_produccion(l)
        else:
            self.limpiar()

    def on_agregar_receta_torta_clicked(self,*args):
        dlg = RecetasDeTortasParaProduccion()
        response = dlg.dialogo.run()
        if dlg.resultado:
            self.cargar_receta(dlg.resultado)

    def on_quitar_receta_torta_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        receta = model.get_value(it,1)

        if yesno("¿Desea eliminar la receta <b>%s</b>?" % receta, self.padre) == gtk.RESPONSE_YES:
           model.remove(it)

        self.mostrar_totales()

    def on_limpiar_recetas_torta_clicked(self, *args):
        self.lista.clear()
        self.produccion_id.set_text('')
        self.estado.set_text('Sin procesar')
        self.fecha.set_text('')
        self.lista.clear()
        self.harina_arroba.set_text('0,000')
        self.harina_kg.set_text('0,000')
        self.harina_bultos.set_text('0,000')
        self.costos.set_text('0,00')

    def cargar_receta(self, tupla):
        self.lista.append([tupla[0], tupla[1], '', '', '', ''])
        self.tvcell2.set_property('editable', True)
        self.mostrar_totales()

    def cargar_detalles(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0], tupla[f][1], punto_coma(tupla[f][2]), punto_coma(tupla[f][3]), punto_coma(tupla[f][4]), tupla[f][5]])
        self.mostrar_totales()

    def on_cellcombo_edited(self, cellrenderertext, path, new_text):
        treeviewmodel = self.tree.get_model()
        iter = treeviewmodel.get_iter(path)
        treeviewmodel.set_value(iter, 5, new_text)

    def on_tvcell2_edited_cb(self, cell, path, new_text, model):
        codigo = model[path][0]
        model[path][2] = new_text
        model[path][3] = self.calcular_unidades_producidas(model[path][0], model[path][2])
        model[path][4] = self.calcular_costo_arroba(model[path][0], model[path][2])
        self.revisar_existencias(model[path][0], model[path][2])
        self.mostrar_totales()
        return

    def sumar_harina(self, *args):
        cantidad = 0
        try:
            for i in self.lista:
                cantidad += coma_punto(i[2])
        except:
            cantidad = 0
        return cantidad

    def sumar_costos(self, *args):
        subtotal = 0
        try:
            for i in self.lista:
                subtotal += coma_punto(i[3])
        except:
            subtotal = 0
        return subtotal

    def revisar_existencias(self, receta_id, harina):
        harina_arroba = coma_punto(harina)
        receta = list(Model().buscar_detalles_id_receta_arroba(receta_id))
        movimiento = 'Salida'
        for i in receta:
            articulo_id = i[1]
            nombre_articulo_id = i[2]
            cantidad = i[0] * harina_arroba
            status = Model().verificar_existencia_detallada(articulo_id, cantidad, movimiento)
            if status == 0:
                info('No hay existencia del articulo %s con código %s' % nombre_articulo, articulo_id)

    def calcular_unidades_producidas(self, receta_id, harina):
        harina_arroba = float(str(coma_punto(harina)))
        receta = list(Model().buscar_id_receta_arroba(receta_id))
        unidades = float(receta[11]) * harina_arroba
        return punto_coma('%.2f' % unidades)

    def calcular_costo_arroba(self, receta_id, harina):
        harina_arroba = float(str(coma_punto(harina)))
        receta = list(Model().buscar_id_receta_arroba(receta_id))
        nuevo_costo = float(receta[16]) * harina_arroba
        return punto_coma('%.2f' % nuevo_costo)

    def mostrar_totales(self, *args):
        try:
            harina_arroba = float(str(self.sumar_harina()))
            harina_kg = arroba_a_kg(harina_arroba)
            harina_bultos = kg_a_bultos(harina_kg)
            costos = float(str(self.sumar_costos()))
            self.harina_arroba.set_text(punto_coma('%.3f' % harina_arroba))
            self.harina_kg.set_text(punto_coma('%.3f' % harina_kg))
            self.harina_bultos.set_text(punto_coma('%.3f' % harina_bultos))
            self.costos.set_text(punto_coma('%.2f' % costos))
        except:
            self.harina_arroba.set_text('0,000')
            self.harina_kg.set_text('0,000')
            self.harina_bultos.set_text('0,000')
            self.costos.set_text('0,00')

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.produccion_id.set_text('')
        self.estado.set_text('Sin procesar')
        self.fecha.set_text('')
        self.lista.clear()
        self.harina_arroba.set_text('0,000')
        self.harina_kg.set_text('0,000')
        self.harina_bultos.set_text('0,000')
        self.costos.set_text('0,00')

    def limpiar(self, *args):
        self.estado.set_text('Sin procesar')
        self.fecha.set_text('')
        self.lista.clear()
        self.harina.set_text('0,000')
        self.harina_arroba.set_text('0,000')
        self.harina_kg.set_text('0,000')
        self.harina_bultos.set_text('0,000')
        self.costos.set_text('0,00')

    def campos_llenos(self, fecha, estado, ):
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

    def on_aplicar_clicked(self, *args):
        pass

    def campos_llenos(self, fecha, estado, harina_arroba, harina_kg, harina_bultos, costos):
        ok = 0

        if fecha == '':
            info("Debe colocar una fecha")
            return

        if estado == '':
            info("Debe colocar un estado a la producción")
            return

        if harina_arroba == '':
            return

        if harina_kg == '':
            return

        if harina_bultos == '':
            return

        if costos == '':
            return

        if fecha != '' and estado !='' and harina_arroba != '' and harina_bultos != '' and costos != '':
            ok = 1
        else:
            ok = 0

        return ok

    def on_aceptar_clicked(self, *args):
        fecha = self.fecha.get_text()
        estado = self.estado.get_text()
        harina_arroba = coma_punto(self.harina_arroba.get_text())
        harina_kg = coma_punto(self.harina_kg.get_text())
        harina_bultos = coma_punto(self.harina_bultos.get_text())
        costos = coma_punto(self.costos.get_text())
        lleno = self.campos_llenos(fecha, estado, harina_arroba, harina_kg, harina_bultos, costos)
        filas = len(self.lista)

        existe = self.produccion_id.get_text()
        if existe is None or existe == '':

            if lleno == 1 and filas >=1:
                produccion = Model().agregar_produccion(fecha, estado, harina_arroba, harina_kg, harina_bultos, costos)
                self.codigo = int(produccion[0])
                if self.produccion_id != 0:
                    for i in self.lista:
                        receta_id = i[0]
                        harina = coma_punto(i[2])
                        unidades = coma_punto(i[3])
                        costo = coma_punto(i[4])
                        nombre_empleado = i[5]
                        empleado = Model().buscar_un_nombre_de_empleado(nombre_empleado)
                        empleado_id = empleado[0]
                        elaboraciones_insertadas = Model().agregar_produccion_detalles(self.codigo, receta_id, harina, unidades, costo, empleado_id)
                else:
                    info('Ocurrio un error en la inserción de datos')

            if lleno ==1 and filas == 0:
                info('Debe agregar una receta')
                self.agregar.grab_focus()

            if self.codigo != 0 and elaboraciones_insertadas == filas:
                self.despachar()
                self.on_dialogo_destroy()
        else:
            modificado = Model().modificar_produccion(existe)

    def despachar(self, *args):
        filas = len(self.lista)
        emision = self.fecha.get_text()
        for i in self.lista:
            receta_id = i[0]
            harina = coma_punto(i[2])
            nombre_empleado = i[5]
            empleado = Model().buscar_un_nombre_de_empleado(nombre_empleado)
            empleado_id = empleado[0]
            enc_receta = Model().buscar_id_receta(receta_id)
            bruto = enc_receta[13]/4 * harina
            impuestos = enc_receta[14]/4 * harina
            total = enc_receta[16]/4 * harina
            despacho = Model().agregar_despacho(empleado_id, emision, bruto, impuestos, total)
            despacho_id = int(despacho[0])
            dtreceta = Model().buscar_detalles_id_receta_arroba(receta_id)
            for f in range(len(dtreceta)):
                cantidad = dtreceta[f][0] * harina
                articulo_id = dtreceta[f][1]
                total_neto = dtreceta[f][7] * harina
                status = Model().verificar_existencia_simple(articulo_id, cantidad, 'Salida')
                if status == 1:
                    renglones = Model().agregar_despacho_detalles(emision, despacho_id, cantidad, articulo_id, total_neto)

        if despacho_id != '' and renglones == filas:
           modificado = Model().produccion_procesada(self.codigo)
           if modificado == 1:
               self.actualizar_estado(self.codigo)

    def actualizar_estado(self, produccion_id):
        encabezado = Model().buscar_id_produccion(produccion_id)
        self.produccion_id.set_text(str(encabezado[0]))
        self.estado.set_text(encabezado[2])

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()


class RecetasDeTortasParaProduccion:

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file('wLista_De_Recetas.glade')
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
        buff = "Total de recetas registrados: %s" % filas
        context_id = self.statusbar.get_context_id('Total de recetas registradas: ')
        self.statusbar.push(context_id,buff)

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().recetas_de_tortas_ordenadas_por_id())

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
            self.resultado = Model().buscar_id_receta_de_torta(self.filtro.get_text())

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_de_receta_de_torta(self.filtro.get_text())

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
        self.resultado = Model().buscar_id_receta_de_torta_para_produccion(codigo)
        if self.resultado:
            self.dialogo.destroy()

if __name__ == '__main__':
    ProduccionPasteleria().main()

