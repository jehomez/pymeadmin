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
from inventario import InventarioValorizado

rDir = os.getcwd()
os.chdir(rDir)

class PeriodoInventario:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('periodo_inventario.glade')
        builder.connect_signals(self)
        self.ventana = builder.get_object('ventana')
        self.anyo = builder.get_object('anyo')
        self.mes = builder.get_object('mes')

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.ventana.show()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_aceptar_clicked(self, *args):
        mes = self.mes.get_active()
        mes1 = 0

        if mes == 0:
            mes1 = 1
        if mes == 1:
            mes1 = 2
        if mes == 2:
            mes1 = 3
        if mes == 3:
            mes1 = 4
        if mes == 4:
            mes1 = 5
        if mes == 5:
            mes1 = 6
        if mes == 6:
            mes1 = 7
        if mes == 7:
            mes1 = 8
        if mes == 8:
            mes1 = 9
        if mes == 9:
            mes1 = 10
        if mes == 10:
            mes1 = 11
        if mes == 11:
            mes1 = 12

        year = self.anyo.get_text()
        InventarioValorizado(int(year), int(mes1))
        self.ventana.destroy()

    def on_cancelar_clicked(self, *args):
        self.on_ventana_destroy()

if __name__ == '__main__':
    z = PeriodoInventario()
    z.main()
