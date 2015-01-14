#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       bancos.py
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
#~ import HTML

import gtk
import os
from inventariotreetohtml import TreeToHTML, TotalesToHTML
from mensajes import info
from modelo import Model
from comunes import nombre_mes, punto_coma, coma_punto

(ITEM, DESCRIPCION, EXISTENCIA_ANTERIOR, ENTRADAS, SALIDAS, RETIROS, AUTOCONSUMOS, EXISTENCIA_ACTUAL, VALOR_ANTERIOR, ENTRADAS_BS, SALIDAS_BS, RETIROS_BS, AUTOCONSUMOS_BS, EXISTENCIA_BS) = range(14)

#~

rDir = os.getcwd()
os.chdir(rDir)

class InventarioValorizado:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, year = None, mes = None):
        builder = gtk.Builder()
        builder.add_from_file('wInventario2.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.razon_social = builder.get_object('razon_social')
        self.rif = builder.get_object('rif')
        self.fecha = builder.get_object('fecha')
        self.tree = builder.get_object('treeview')
        self.tree_totales = builder.get_object('tree_totales')
        self.lista = builder.get_object('lista')
        self.lista_totales = builder.get_object('lista_totales')
        self.listado = []

        self.crear_columnas()
        self.lista_ordenada_por_id(year, mes)
        self.razon_social.set_text('Panadería y Pastelería La Criollita')
        self.rif.set_text('J-30026088-7')
        self.fecha.set_text(nombre_mes(mes)+'/'+ str(year))
        self.ventana.show()

    def crear_columnas(self):
        columnas = []
        columnas.append ([ITEM, "Item de inventario", str])
        columnas.append ([DESCRIPCION, "Descripción", str])
        columnas.append ([EXISTENCIA_ANTERIOR, "Existencia Anterior", int])
        columnas.append ([ENTRADAS, "Entradas", int])
        columnas.append ([SALIDAS, "Salidas", int])
        columnas.append ([RETIROS, "Retiros", int])
        columnas.append ([AUTOCONSUMOS, "Autoconsumos", int])
        columnas.append ([EXISTENCIA_ACTUAL,"Existencia Actual", int])
        columnas.append ([VALOR_ANTERIOR, "Valor Anterior", int])
        columnas.append ([ENTRADAS_BS, "Entradas Bs.", int])
        columnas.append ([SALIDAS_BS, "Salidas Bs.", int])
        columnas.append ([RETIROS_BS, "Retiros Bs.", int])
        columnas.append ([AUTOCONSUMOS_BS, "Autoconsumos Bs.", int])
        columnas.append ([EXISTENCIA_BS, "Existencia Bs.", int])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self, year, mes):
        listado = Model().inventario_valorizado(int(year), int(mes))
        if listado:
            self.listado = listado
            self.cargar_lista(listado)
            self.mostrar_totales()

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0], tupla[f][1], punto_coma(tupla[f][2]), punto_coma(tupla[f][3]), punto_coma(tupla[f][4]), punto_coma(tupla[f][5]), punto_coma(tupla[f][6]), punto_coma(tupla[f][7]), punto_coma(tupla[f][8]), punto_coma(tupla[f][9]), punto_coma(tupla[f][10]), punto_coma(tupla[f][11]), punto_coma(tupla[f][12]), punto_coma(tupla[f][13])])

    def calcular_existencias_anteriores_totales(self, *args):
        existencia_ant = 0
        try:
            for i in self.lista:
                existencia_ant += coma_punto(i[2])
        except:
            existencia_ant = 0
        return existencia_ant

    def calcular_entradas_totales(self, *args):
        entradas = 0
        try:
            for i in self.lista:
                entradas += coma_punto(i[3])
        except:
            entradas = 0
        return entradas

    def calcular_salidas_totales(self, *args):
        salidas = 0
        try:
            for i in self.lista:
                salidas += coma_punto(i[4])
        except:
            salidas = 0
        return salidas

    def calcular_retiros_totales(self, *args):
        retiros = 0
        try:
            for i in self.lista:
                retiros += coma_punto(i[5])
        except:
            retiros = 0
        return retiros

    def calcular_autoconsumos_totales(self, *args):
        autoconsumos = 0
        try:
            for i in self.lista:
                autoconsumos += coma_punto(i[6])
        except:
            autoconsumos = 0
        return autoconsumos

    def calcular_existencias_totales(self, *args):
        existencia = 0
        try:
            for i in self.lista:
                existencia += coma_punto(i[7])
        except:
            existencia = 0
        return existencia

    def calcular_valores_anteriores_totales(self, *args):
        valor_anterior = 0
        try:
            for i in self.lista:
                valor_anterior += coma_punto(i[8])
        except:
            valor_anterior = 0
        return valor_anterior

    def calcular_entradas_bs_totales(self, *args):
        entrada_bs = 0
        try:
            for i in self.lista:
                entrada_bs += coma_punto(i[9])
        except:
            entrada_bs = 0
        return entrada_bs

    def calcular_salidas_bs_totales(self, *args):
        salidas_bs = 0
        try:
            for i in self.lista:
                salidas_bs += coma_punto(i[4])
        except:
            salidas_bs = 0
        return salidas_bs

    def calcular_retiros_bs_totales(self, *args):
        retiros_bs = 0
        try:
            for i in self.lista:
                retiros_bs += coma_punto(i[5])
        except:
            retiros_bs = 0
        return retiros_bs

    def calcular_autoconsumos_bs_totales(self, *args):
        autoconsumos_bs = 0
        try:
            for i in self.lista:
                autoconsumos_bs += coma_punto(i[6])
        except:
            autoconsumos_bs = 0
        return autoconsumos_bs

    def calcular_existencia_bs_totales(self, *args):
        existencia_bs = 0
        try:
            for i in self.lista:
                existencia_bs += coma_punto(i[7])
        except:
            existencia_bs = 0
        return existencia_bs

    def mostrar_totales(self, *args):
        existencias_anteriores = punto_coma('%.2f' % self.calcular_existencias_anteriores_totales())
        entradas = punto_coma('%.2f' % self.calcular_entradas_totales())
        salidas = punto_coma('%.2f' % self.calcular_salidas_totales())
        retiros = punto_coma('%.2f' % self.calcular_retiros_totales())
        autoconsumos = punto_coma('%.2f' % self.calcular_autoconsumos_totales())
        existencias = punto_coma('%.2f' % self.calcular_existencias_totales())
        valores_anteriores = punto_coma('%.2f' % self.calcular_valores_anteriores_totales())
        entradas_bs = punto_coma('%.2f' % self.calcular_entradas_bs_totales())
        salidas_bs = punto_coma('%.2f' % self.calcular_salidas_bs_totales())
        retiros_bs = punto_coma('%.2f' % self.calcular_retiros_bs_totales())
        autoconsumos_bs = punto_coma('%.2f' % self.calcular_autoconsumos_bs_totales())
        existencia_bs = punto_coma('%.2f' % self.calcular_existencia_bs_totales())
        self.lista_totales.append([existencias_anteriores, entradas, salidas, retiros, autoconsumos, existencias, valores_anteriores, entradas_bs, salidas_bs, retiros_bs, autoconsumos_bs, existencia_bs])

    def on_imprimir_clicked(self,*args):
        t = TreeToHTML(self.tree,'Panaderia y Pasteleria La Criollita RIF J-30026088-7 Inventario Valorizado', self.col_data)
        t.show1()
        x = TotalesToHTML(self.tree_totales,'Totales Inventario Valorizado')
        x.show2()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

if __name__ == '__main__':
    z = InventarioValorizado()
    z.main()
