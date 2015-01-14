#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       configuracion_ids_iniciales
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
from modelo import Model

class Ids:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("configuracion_ids_iniciales.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.venta_id = builder.get_object("venta_id")
        self.cargar_ids_iniciales()
        self.dialogo.show()

    def cargar_ids_iniciales(self, *args):
        ids = Model().cargar_ids_iniciales()
        if ids:
            self.venta_id.set_text(ids[0])
        else:
            self.venta_id.set_text('')

    def on_aplicar_clicked(self, *args):
        venta_id_inicial = self.venta_id.get_text()
        ok = Model().guardar_configuracion_ids('ventas', venta_id_inicial)
        if ok==1:
            self.on_dialogo_destroy()

    def on_cerrar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    Ids().main()
