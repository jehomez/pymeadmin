#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       sin título.py
#
#       Copyright 2010 Jesús Hómez <jesus@jesus>
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

#!/usr/bin/env python
import sys
from modelo import Model

try:
  import pygtk
  pygtk.require("2.6")
except:
  pass

try:
  import gtk, gobject
except:
  sys.exit(1)

class CellRendererExample:
  """ Main class of the application. """

  items = ("item 1",
           "item 2",
           "item 3",
           "item 4",
           "item 5")

  def __init__(self):
      # Create window and connect its destroy signal.
      self.window = gtk.Window()
      self.window.connect("destroy", gtk.main_quit)

      # Create and add a treeview widget to the window.
      self.treeview = gtk.TreeView()
      self.window.add(self.treeview)

      # Create a text column
      self.column0 = gtk.TreeViewColumn("Text",
                                    gtk.CellRendererText(),
                                    text=0)

      # Create a combobox column
      self.lsmodel = gtk.ListStore(str)

      self.cellcombo = gtk.CellRendererCombo()

      self.cellcombo.set_property("text-column", 0)
      self.cellcombo.set_property("editable", True)
      self.cellcombo.set_property("has-entry", False)
      self.cellcombo.set_property("model", self.lsmodel)

      self.cellcombo.connect("edited", self.on_cellcombo_edited)

      self.column1 = gtk.TreeViewColumn("Combobox", self.cellcombo, text=1)

      self.treeview.append_column(self.column0)
      self.treeview.append_column(self.column1)

      # Create liststore.
      self.liststore = gtk.ListStore(str, str)

      # Cargando el liststore
      self.liststore.append(["Some text", "Click here to select an item."])

      # Set model.
      self.treeview.set_model(self.liststore)
      self.cargar_combo()

      self.window.show_all()

  def cargar_combo(self, *args):
        lista = Model().panaderos_y_pasteleros_ordenados_por_id()
        for f in range(len(lista)):
            self.lsmodel.append([lista[f][0]])

  def on_cellcombo_edited(self, cellrenderertext, path, new_text):
      treeviewmodel = self.treeview.get_model()
      iter = treeviewmodel.get_iter(path)
      treeviewmodel.set_value(iter, 1, new_text)

  def main(self):
      gtk.main()

if __name__ == "__main__":
  CellRendererExample().main()
