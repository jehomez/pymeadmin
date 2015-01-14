#!/usr/bin/env python
## -*- coding: utf-8 -*-
import os, sys
#
#       sin titulo.py
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

from reportlab.pdfgen import canvas

oracion = ['Y en tu ausencia las paredes','se pintarán de tristeza',\
'y enjaularé mi corazón entre tus huesos.']


aux = canvas.Canvas("prueba.pdf")

textobject = aux.beginText()
textobject.setTextOrigin(100, 500)
textobject.setFont("Courier", 14)
for line in oracion:
    uniLine = unicode(line, 'utf-8')
    textobject.textLine(uniLine)
textobject.setFillGray(0.5)
lineas_texto = '''
Hola a todos. En este post vamos a ver
como escribir texto con Python y ReportLab.
Más información en El Viaje del Navegante.
'''
lineas_texto = unicode(lineas_texto,'utf-8')
textobject.textLines(lineas_texto)
aux.drawText(textobject)

# Salvamos.
aux.showPage()
aux.save()



