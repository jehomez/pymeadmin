#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       modelo.py
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

from decimal import Decimal
from datetime import date

def mov_str_to_int( valor):
    if valor == 'Entrada':
        v = 0
    else:
        v = 1

    return v

def mov_int_to_str(valor):
    if valor == 0:
        v = 'Entrada'

    if valor == 1:
        v = 'Salida'

    if valor != 0 and valor != 1:
        v = ''

    return v

def coma_guion(valor):
    a = str(valor)
    b = a.replace(',','-')
    return b

def punto_coma(valor):
    if type(valor) == 'float':
        a = repr(valor)
    else:
        a = str(valor)
    b = a.replace('.', ',')
    return b

def coma_punto( valor):
    a = str(valor)
    b = float(a.replace(',','.'))
    c = Decimal('%.3f' % b)
    return c

def logico_a_caracter( valor):
    if valor == True:
        v = 'si'
    else:
        v = 'no'

    return v

def caracter_a_logico( valor):
    if valor == 'si':
        v = True
    else:
        v = False

    return v

def kg_a_arroba(kg):
    arroba = 11.25
    try:
        x = float(str(coma_punto(kg)))/arroba
    except:
        x = 0
    return x

def arroba_a_kg(arroba ):
    try:
        x = float(str(coma_punto(arroba))) * 11.25
    except:
        x = 0
    return x

def kg_a_bultos(kg):
    try:
        x = float(str(coma_punto(kg))) / 45
    except:
        x = 0
    return x

def es_ve(value, places=2, curr='Bs', sep='.', dp=',', pos='', neg='-', overall=10):
    """ Convert Decimal ``value'' to a money-formatted string.
    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, or blank) every 3
    dp:      decimal point indicator (comma or period); only specify as
                 blank when places is zero
    pos:     optional sign for positive numbers: "+", space or blank
    neg:     optional sign for negative numbers: "-", "(", space or blank
    overall: optional overall length of result, adds padding on the
                 left, between the currency symbol and digits"""
    q = Decimal((0, (1,), -places))
    sign, digits, exp = value.quantize(q).as_tuple( )
    result = [  ]
    digits = map(str, digits)
    append, next = result.append, digits.pop
    for i in range(places):
        if digits:
            append(next( ))
        else:
            append('0')
    append(dp)
    i = 0
    while digits:
        append(next( ))
        i += 1
        if i == 3 and digits:
            i = 0
            append(sep)
    while len(result) < overall:
        append('')
    append(curr)
    if sign:
        append(neg)
    else:
        append(pos)
        result.reverse( )

    return ''.join(result)

def calcular_precio_neto(costo, utilidad):
    n = float(coma_punto(utilidad))/100*float(coma_punto(costo)) + float(coma_punto(costo))
    n1 = str(Decimal('%.7f' % n))
    neto = n1.replace('.', ',')
    return neto

def calcular_iva_compra(iva, neto, costo):
    factor = float('1.'+str(int(coma_punto(iva))))
    i = float(coma_punto(costo)) - float(coma_punto(neto))

    if i == 0:
        i = float(coma_punto(costo))- float(coma_punto(costo))/factor

    i1 = str(Decimal('%.7f' % i))
    iva_compra = i1.replace('.', ',')
    return iva_compra

def calcular_iva_venta(iva, neto, venta):
    factor = float('1.'+str(int(coma_punto(iva))))
    i = float(coma_punto(venta)) - float(coma_punto(neto))

    if i == 0:
        i = float(coma_punto(venta))- float(coma_punto(venta))/factor

    i1 = str(Decimal('%.7f' % i))
    iva_venta = i1.replace('.', ',')
    return iva_venta

def calcular_precio_venta(iva, costo, utilidad):
    neto = float(coma_punto(calcular_precio_neto(costo, utilidad)))
    p = float(coma_punto(iva))/100*float(neto) + float(neto)
    p1 = str(Decimal('%.3f' % p))
    precio_venta = p1.replace('.', ',')
    return precio_venta

def calcular_utilidad(costo, venta):
    p = float(coma_punto(venta))
    c = float(coma_punto(costo))
    u = 100*((p - c)/c)
    u1 = str(Decimal('%.3f' % u))
    utilidad = u1.replace('.', ',')
    return utilidad

def calcular_edad(anio, mes, dia):
    fecha_nac = date(anio,mes,dia)
    hoy = date.today()
    edad = hoy - fecha_nac
    return str(edad.days/365) + ' años'

def nombre_mes(mes):
    if mes == 1:
        mes1 = 'Enero'
    if mes == 2:
        mes1 = 'Febrero'
    if mes == 3:
        mes1 = 'Marzo'
    if mes == 4:
        mes1 = 'Abril'
    if mes == 5:
        mes1 = 'Mayo'
    if mes == 6:
        mes1 = 'Junio'
    if mes == 7:
        mes1 = 'Julio'
    if mes == 8:
        mes1 = 'Agosto'
    if mes == 9:
        mes1 = 'Septiembre'
    if mes == 10:
        mes1 = 'Octubre'
    if mes == 11:
        mes1 = 'Noviembre'
    if mes == 12:
        mes1 = 'Diciembre'
    return mes1
