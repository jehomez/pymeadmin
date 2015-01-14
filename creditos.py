#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wPrincipal.py
#
#       Este archivo muestra la ventana principal del sistema
#
#       Copyright 2010 Jesús Hómez <jesusenriquehomez@gmail.com>
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

import pygtk
import gtk
import os

rDir = os.getcwd()
os.chdir(rDir)


class DlgAcerca:

    def main(self):
        gtk.main()

    def __init__(self):
        builder = gtk.Builder()
        builder.add_from_file("wAcerca.glade")
        builder.connect_signals(self)
        self.dlgAcerca = builder.get_object("dlgAcerca")
        self.dlgAcerca.run()
        self.dlgAcerca.destroy()

    def hide_dialog(self, widget, data):
        widget.hide()

if __name__ == "__main__":
    about = DlgAcerca()
    about.main()
