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

import gtk
import os
from libro_compras import LibroDeCompras
rDir = os.getcwd()
os.chdir(rDir)

class Periodo:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, fecha1 = None, fecha2 = None):
        builder = gtk.Builder()
        builder.add_from_file('fechas.glade')
        builder.connect_signals(self)
        self.ventana = builder.get_object('ventana')
        self.fecha1 = builder.get_object('fecha1')
        self.fecha2 = builder.get_object('fecha2')
        self.ventana.show()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_aceptar_clicked(self, *args):
        f1 = self.fecha1.get_date()
        f2 = self.fecha2.get_date()
        ano1 = f1[0]
        mes1 = f1[1] + 1
        dia1 = f1[2]
        ano2 = f2[0]
        mes2 = f2[1] + 1
        dia2 = f2[2]
        fecha1 =(ano1,mes1,dia1)
        fecha2 =(ano2,mes2,dia2)
        LibroDeCompras(fecha1, fecha2)
        self.ventana.destroy()

    def on_cancelar_clicked(self, *args):
        self.on_ventana_destroy()

if __name__ == '__main__':
    z = Periodo()
    z.main()
