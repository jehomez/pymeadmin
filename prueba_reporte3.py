#!/usr/bin/env python
## -*- coding: utf-8 -*-
import os, sys
#Ejemplo de uso de PLATYPUS. El Viaje del Navegante. 04/04/2010.

#~ Obtenemos de platypus las clases Paragraph, para escribir párrafos Image, para insertar imágenes y SimpleDocTemplate para definir el DocTemplate. Además importamos Spacer, para incluir espacios .

from reportlab.platypus import Paragraph
from reportlab.platypus import Image
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer

#~ Importamos clase de hoja de estilo de ejemplo.

from reportlab.lib.styles import getSampleStyleSheet

#~ Se importa el tamaño de la hoja.

from reportlab.lib.pagesizes import A4

#~ Y los colores.

from reportlab.lib import colors

#~ Creamos un PageTemplate de ejemplo.

estiloHoja = getSampleStyleSheet()

#~ Inicializamos la lista Platypus Story.

story = []

#~ Definimos cómo queremos que sea el estilo de la PageTemplate.

cabecera = estiloHoja['Heading4']

#~ No se hará un salto de página después de escribir la cabecera (valor 1 en caso contrario).

cabecera.pageBreakBefore=0

#~ Se quiere que se empiece en la primera página a escribir. Si es distinto de 0 deja la primera hoja en blanco.

cabecera.keepWithNext=0

#~ Color de la cabecera.

cabecera.backColor=colors.cyan

#~ Incluimos un Flowable, que en este caso es un párrafo.

parrafo = Paragraph("CABECERA DEL DOCUMENTO ",cabecera)

#~ Lo incluimos en el Platypus story.

story.append(parrafo)

#~ Definimos un párrafo. Vamos a crear un texto largo para demostrar cómo se genera más de una hoja.

cadena = " El Viaje del Navegante " * 600

#~ Damos un estilo BodyText al segundo párrafo, que será el texto a escribir.

estilo = estiloHoja['BodyText']
parrafo2 = Paragraph(cadena, estilo)

#~ Y lo incluimos en el story.

story.append(parrafo2)

#~ Dejamos espacio.

story.append(Spacer(0,20))

#~ Ahora incluimos una imagen.

#~ fichero_imagen = "logo.png"
#~ imagen_logo = Image(os.path.realpath(fichero_imagen),width=402,height=342)
#~ story.append(imagen_logo)

#~ Creamos un DocTemplate en una hoja DIN A4, en la que se muestra el texto enmarcado (showBoundary=1) por un recuadro.

doc=SimpleDocTemplate("ejemplo1.pdf",pagesize=A4,showBoundary=1)

#~ Construimos el Platypus story.

doc.build(story)
