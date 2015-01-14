#!/usr/bin/env python
# -*- coding: UTF8  -*-
import sys
import os
import subprocess
import webbrowser
from fechas import CDateLocal


(EXISTENCIA_ANTERIOR, ENTRADAS, SALIDAS, RETIROS, AUTOCONSUMOS, EXISTENCIA_ACTUAL, VALOR_ANTERIOR, ENTRADAS_BS, SALIDAS_BS, RETIROS_BS, AUTOCONSUMOS_BS, EXISTENCIA_BS) = range(12)


class TreeToHTML:

    def __init__(self, tree=None, title="", cols=[]):
        self.treeview = tree
        self.html = ""
        self.title = title
        self.cols = cols

    def tohtml(self):
        self.html = '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
        self.html += "<h1><center>%s</center></h1>" % self.title
        self.html += "<tt>"
        self.html += '<table WIDTH=180% border=1 rules="groups, cols"><tr>'
        for i in self.treeview.get_columns():
            self.html += "<th>%s</th>" % i.get_title()
            #self.html += "</table><table WIDTH=150%>"

        for i in self.treeview.get_model():
            self.html += "<tr>"
            for j in self.cols:
                if j < 2:
                    align = "LEFT"
                else:
                    align = "RIGHT"
                if type(j) is int:
                    col = j
                    tipo = ""
                else:
                    col = j[0]
                    tipo = j[1]
                text = i[col]
                if text is None:
                    text = ""

                if tipo == "dte":
                    text = CDateLocal(text)
                    align = "RIGHT"
                if tipo == "time":
                    text = text[:5]
                    align = "RIGHT"
                self.html += "<td align=%s>%s</td>" % (align, text)
            self.html += "</utr>"

    def show1(self):
          self.tohtml()
          f = open("inventario_valorizado.html", "w")
          f.write(self.html)
          f.close()
          if sys.platform == "win32":
               #os.system("explorer reporte.html")
               webbrowser.open_new_tab('inventario_valorizado.html')
          else:
               #os.system("firefox %s reporte.html")
               webbrowser.open_new_tab('inventario_valorizado.html')


class TotalesToHTML:

    def crear_columnas():
        columnas = []
        columnas.append([EXISTENCIA_ANTERIOR, "Existencia Anterior", str])
        columnas.append([ENTRADAS, "Entradas", str])
        columnas.append([SALIDAS, "Salidas", str])
        columnas.append([RETIROS, "Retiros", str])
        columnas.append([AUTOCONSUMOS, "Autoconsumos", str])
        columnas.append([EXISTENCIA_ACTUAL,"Existencia Actual", str])
        columnas.append([VALOR_ANTERIOR, "Valor Anterior", str])
        columnas.append([ENTRADAS_BS, "Entradas Bs.", str])
        columnas.append([SALIDAS_BS, "Salidas Bs.", str])
        columnas.append([RETIROS_BS, "Retiros Bs.", str])
        columnas.append([AUTOCONSUMOS_BS, "Autoconsumos Bs.", str])
        columnas.append([EXISTENCIA_BS, "Existencia Bs.", str])
        col_data = [z[0] for z in columnas]
        return col_data

    def __init__(self, tree=None, title="", cols= crear_columnas()):
        self.treeview = tree
        self.html = ""
        self.title = title
        self.cols = cols

    def tohtml(self):
        self.html = '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
        self.html += "<h1><center>%s</center></h1>" % self.title
        self.html += "<tt>"
        self.html += '<table WIDTH=180% border=1 rules="groups, cols"><tr>'
        for i in self.treeview.get_columns():
            self.html += "<th>%s</th>" % i.get_title()
            #self.html += "</table><table WIDTH=150%>"

        for i in self.treeview.get_model():
            self.html += "<tr>"
            for j in self.cols:
                if type(j) is int:
                    col = j
                    tipo = ""
                else:
                    col = j[0]
                    tipo = j[1]
                text = i[col]
                if text is None:
                    text = ""

                align = "RIGHT"
                if tipo == "dte":
                    text = CDateLocal(text)
                    align = "LEFT"
                if tipo == "time":
                    text = text[:5]
                    align = "LEFT"

                self.html += "<td align=%s>%s</td>" % (align, text)
            self.html += "</utr>"

    def show2(self):
      self.tohtml()
      f = open("totales_inventario_valorizado.html", "w")
      f.write(self.html)
      f.close()
      if sys.platform == "win32":
          webbrowser.open_new_tab('totales_inventario_valorizado.html')
      else:
          webbrowser.open_new_tab('totales_inventario_valorizado.html')
