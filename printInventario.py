#!/usr/bin/env python
# -*- coding: UTF8  -*-
import sys
import os
import comunes
import subprocess
from modelo import Model
from datetime import date

(FECHA, EXISTENCIA_TOTAL) = range(2)

class InventarioHTML:
    def __init__(self, total = None, tree=None, title="", cols=[]):
        self.html = ""
        self.fecha = date.today()
        self.total = total
        self.treeview = tree
        self.html = ""
        self.title = title
        self.cols = cols
        self.tohtml()

    def tohtml(self):

        self.html = '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
        self.html += "<h1><center><U>Reporte de Inventario</U></center></h1>"
        self.html += "<tt>"
        self.html += '<table WIDTH=90%  rules="groups, cols">'
        self.html += '<tr><td><b>Fecha: </b>%s</td><td><b>Existencia Bs.: </b>%s</tr>'%(self.fecha, self.total)
        self.html += '</tr>'
        self.html += "</table></tt>"
        self.html += '<br><h5><u>Detalles del Inventario</u></h5>'
        self.html += '<table WIDTH=90% border=1 rules="groups, cols"><tr>'
        self.lista_inventario()

    def lista_inventario(self):
        for i in self.treeview.get_columns():
            self.html += "<th>%s</th>" % i.get_title()
        #self.html += "</table><table WIDTH=90%>"

        for i in self.treeview.get_model():
            self.html += "<tr>"
            for j in self.cols:
                if type(j) is int:
                    col = j
                    tipo = ""
                    align = "RIGHT"
                elif type(j) is str:
                    col = j[0]
                    tipo = j[1]
                    align = "LEFT"
                text = i[col]
                if text is None:
                    text = ""
                #align = "LEFT"
                if tipo == "dte":
                    text = CDateLocal(text)
                    align = "RIGHT"
                if tipo == "time":
                    text = text[:5]
                    align = "RIGHT"
                if tipo == "str":
                    align = "LEFT"
                if tipo == "int":
                    align = "RIGHT"

                self.html += "<td align=%s>%s</td>" % (align, text)
            self.html += "</tr>"

        self.html += "</tr>"
        self.html += "</table>"
        self.html += "</tt>"

    def show(self):
        self.tohtml()
        f = open("reporte.html", "w")
        f.write(self.html)
        f.close()
        if sys.platform == "win32":
           #os.system("explorer reporte.html")
           subprocess.Popen('explorer reporte.html', shell=True)
        else:
           #os.system("firefox reporte.html")
           subprocess.Popen('firefox reporte.html', shell=True)
