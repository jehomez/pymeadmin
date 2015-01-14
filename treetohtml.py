#!/usr/bin/env python
# -*- coding: UTF8  -*-
import sys
import os
import subprocess
from fechas import CDateLocal

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
        self.html += '<table WIDTH=90% border=1 rules="groups, cols"><tr>'
        for i in self.treeview.get_columns():
            self.html += "<th>%s</th>" % i.get_title()
        #self.html += "</table><table WIDTH=90%>"

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

                align = "LEFT"
                if tipo == "dte":
                    text = CDateLocal(text)
                    align = "RIGHT"
                if tipo == "time":
                    text = text[:5]
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
