#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Line
from PIL import Image
import os

PAGE_HEIGHT=29.7*cm
PAGE_WIDTH=21*cm
capitulo = 'Cap %d' % 1
tema = 'Descripcion General del Edificio'
logo = Image.open('/home/jesus/Proyectos/pymeadmin/logo.jpg')
##logo = 'el logo de 40x40pixels'
arquitecto = 'Nombre del arquitecto'
empresa = 'nombre de la empresa'
proyecto = 'Descripcion del proyecto'
situacion = 'poblacion, municipio'
referencia = 'referencia interna'

l1 = (1*cm, PAGE_HEIGHT-2.3*cm, PAGE_WIDTH-1.5*cm, PAGE_HEIGHT-2.3*cm)
l2 = (1*cm, 1.5*cm, PAGE_WIDTH-1.5*cm, 1.5*cm)
lineas = [l1,l2]

estiloencabezado = ParagraphStyle('',
                              fontName = 'DejaVuBd',
                              fontSize = 10,
                              alignment = 0,
                              spaceBefore = 0,
                              spaceAfter = 0,
                              leftIndent = -1*cm,
                              rightIndent = -0.7*cm)

estilonormal = ParagraphStyle('',
                              fontName = 'DejaVu',
                              fontSize = 10,
                              alignment = 4,
                              spaceBefore = 0,
                              spaceAfter = 0,
                              firstLineIndent = 1*cm,
                              topIndent =-1*cm,
                              leftIndent = -1*cm,
                              rightIndent = -0.7*cm)

##plantillaBase = BaseDocTemplate(filename = fich_pdf,
##                            pagesize = A4,
##                            showBoundary=0,
##                            allowSplitting = 1,
##                            _pageBreakQuick = 1)

#importar una fuente TT
pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBd', 'DejaVuSansBold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBdIt', 'DejaVuSansBoldOblique.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuIt', 'DejaVuSansOblique.ttf'))
registerFontFamily('Dejavu', normal = 'DejaVu', bold = 'DejaVuBd', italic = 'DejaVuIt', boldItalic = 'DejaVuBdIt')

def myFirstPage(canvas, doc):
    canvas.saveState()

    ##    Lineas
    canvas.setStrokeColor('Grey')
    canvas.setLineWidth(0.01)
    canvas.lines(lineas)

##    Textos
    canvas.setFont('DejaVu',7)
##    Cabecera
    canvas.drawInlineImage(logo, 1*cm, PAGE_HEIGHT-2.*cm, width = 40, height = 40)
    canvas.drawString(2.5*cm, PAGE_HEIGHT-1.*cm, 'ARQUITECTO: ' + arquitecto)
    canvas.drawString(2.5*cm, PAGE_HEIGHT-1.5*cm, 'EMPRESA: ' + empresa)

    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-1.0*cm, capitulo)

    canvas.drawRightString(PAGE_WIDTH-1.7*cm, PAGE_HEIGHT-1*cm, 'PROYECTO: '+ proyecto)
    canvas.drawRightString(PAGE_WIDTH-1.7*cm, PAGE_HEIGHT-1.5*cm, 'SITUACION: ' + situacion)
    canvas.drawRightString(PAGE_WIDTH-1.7*cm, PAGE_HEIGHT-2.*cm, 'REFERENCIA: ' + referencia)
##    Pie

    canvas.drawCentredString(PAGE_WIDTH/2.0, 1.0 * cm, u'%s' % tema)
    canvas.drawRightString(PAGE_WIDTH - 1.7 * cm, 1.0 * cm, u'Pág. %d' % doc.page)

    canvas.restoreState()

def myLaterPages(canvas, doc):
    canvas.saveState()

    ##    Lineas
    canvas.setStrokeColor('Grey')
    canvas.setLineWidth(0.01)
    canvas.lines(lineas)

##    Textos
    canvas.setFont('DejaVu',7)
##    Cabecera
    canvas.drawInlineImage(logo, 1*cm, PAGE_HEIGHT-2.*cm, width = 40, height = 40)
    canvas.drawString(2.5*cm, PAGE_HEIGHT-1.*cm, 'ARQUITECTO: ' + arquitecto)
    canvas.drawString(2.5*cm, PAGE_HEIGHT-1.5*cm, 'EMPRESA: ' + empresa)

    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-1.0*cm, capitulo)

    canvas.drawRightString(PAGE_WIDTH-1.7*cm, PAGE_HEIGHT-1*cm, 'PROYECTO: '+ proyecto)
    canvas.drawRightString(PAGE_WIDTH-1.7*cm, PAGE_HEIGHT-1.5*cm, 'SITUACION: ' + situacion)
    canvas.drawRightString(PAGE_WIDTH-1.7*cm, PAGE_HEIGHT-2.*cm, 'REFERENCIA: ' + referencia)
##    Pie

    canvas.drawCentredString(PAGE_WIDTH/2.0, 1.0 * cm, u'%s' % tema)
    canvas.drawRightString(PAGE_WIDTH - 1.7 * cm, 1.0 * cm, u'Pág. %d' % doc.page)

    canvas.restoreState()

def go():
    doc = SimpleDocTemplate("esquemaimpresion.pdf")
    Story = [Spacer(1,cm)]
    Titulo1 = u'CAPITULO 1: La formación de las virutas de chocolate.'
    T1 = Paragraph(Titulo1, estiloencabezado)
    textoT1 = u'Un texto muy, muy, muy, pero que muuuuuuuy largo. '*20
    txtT1 = Paragraph(textoT1, estilonormal)
    Story.append(T1)
    Story.append(txtT1)
    Story.append(Spacer(1,0.2*cm))
    Story.append(T1)
    Story.append(txtT1)
    Story.append(Spacer(1,0.2*cm))

    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
if __name__ == "__main__":
    go()
