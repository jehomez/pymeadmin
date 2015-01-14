#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       empleado.py
#
#       Copyright 2010 Jesús Hómez <jesus@jesus-laptop>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY, WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import gtk
import os
import treetohtml
from mensajes import info, yesno
from datetime import date
from modelo import Model
from turnos import DlgTurno
from empleados_tipos import DlgTipoEmpleado
from zonas import DlgZona
from comunes import calcular_edad, punto_coma, coma_punto

(CODIGO, INGRESO, NOMBRE, TELEFONO_FIJO, TELEFONO_MOVIL, CORREO_ELECTRONICO, TIPO, TURNO, CARGO) = range(9)

rDir = os.getcwd()
os.chdir(rDir)


class Empleados:

    def main(self):
        gtk.main()
        return 0

    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file('wEmpleados.glade')
        builder.connect_signals(self)

        self.ventana = builder.get_object('ventana')
        self.buscar = builder.get_object('lblBuscar')
        self.criterio = builder.get_object('criterio')
        self.filtro = builder.get_object("filtro")
        self.tree = builder.get_object('tree')
        self.lista = builder.get_object('lista')
        self.statusbar = builder.get_object('statusbar')

        self.padre = padre
        if padre is None:
            self.frm_padre = self.ventana
        else:
            self.frm_padre = self.padre.frm_padre

        self.crear_columnas()
        self.on_refrescar_clicked()
        self.ventana.show()

    def mostrar_status(self):
        registros = Model().contar_registros('empleados')
        buff = "Total de empleados registrados: %s" % registros
        context_id = self.statusbar.get_context_id('Total de empleados registrados: ')
        self.statusbar.push(context_id,buff)

    def crear_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Código", int])
        columnas.append ([INGRESO, "Ingreso", str])
        columnas.append ([NOMBRE, "Nombre", str])
        columnas.append ([TELEFONO_FIJO, "Teléfono Fijo", str])
        columnas.append ([TELEFONO_MOVIL, "Teléfono Móvil", str])
        columnas.append ([CORREO_ELECTRONICO, "Correo Electrónico", str])
        columnas.append ([TIPO, "Tipo", str])
        columnas.append ([TURNO, "Turno", str])
        columnas.append ([CARGO, "Cargo", str])
        self.col_data = [x[0] for x in columnas]

    def lista_ordenada_por_id(self,*args):
        self.cargar_lista(Model().empleados_ordenados_por_id())

    def cargar_lista(self, tupla):
        self.lista.clear()
        for f in range(len(tupla)):
            self.lista.append([tupla[f][0],tupla[f][5],tupla[f][1],tupla[f][10],tupla[f][11],tupla[f][12],tupla[f][14], tupla[f][16], tupla[f][17]])

    def on_agregar_clicked(self,*args):
        dlg = DlgEmpleado(self.frm_padre, False)
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.on_refrescar_clicked()
           self.on_refrescar_clicked()

    def on_quitar_clicked(self, *args):
        model, it = self.tree.get_selection().get_selected()
        codigo = model.get_value(it,0)
        empleado = model.get_value(it,1)

        if yesno("¿Desea eliminar el empleado <b>%s</b>?\nEsta acción no se puede deshacer\n" % empleado, self.frm_padre) == gtk.RESPONSE_YES:
           Model().eliminar_empleado(codigo)
           model.remove(it)

        self.on_refrescar_clicked()

    def on_buscar_clicked(self,*args):
        self.filtro.set_text('')
        criterio = self.criterio.get_visible()
        buscar = self.buscar.get_visible()
        filtro = self.filtro.get_visible()

        if filtro == False and buscar == False and criterio == False:
            self.buscar.set_visible(True)
            self.criterio.set_visible(True)
            self.filtro.set_visible(True)
            self.criterio.grab_focus()
        else:
            self.buscar.set_visible(False)
            self.criterio.set_visible(False)
            self.filtro.set_visible(False)

    def on_criterio_changed(self, *args):
        criterio = self.criterio.get_active()
        if  criterio == 0 or criterio == 1 or criterio == 2:
            self.filtro.set_text('')
            self.filtro.grab_focus()

    def on_filtro_changed(self, *args):

        if self.criterio.get_active() == 0:

            self.resultado = Model().buscar_id_empleado(self.filtro.get_text())

        elif self.criterio.get_active() == 1:

            self.resultado = Model().buscar_nombre_empleado(self.filtro.get_text())

        self.cargar_lista(self.resultado)


    def on_refrescar_clicked(self,*args):
        self.mostrar_status()
        self.lista_ordenada_por_id()

    def on_propiedades_clicked(self,*args):
       self.on_tree_row_activated()

    def on_imprimir_clicked(self,*args):
        t = treetohtml.TreeToHTML(self.tree,"Lista de Empleados", self.col_data)
        t.show()

    def on_cerrar_clicked(self, *args):
        self.on_ventana_destroy()

    def on_ventana_destroy(self, *args):
        self.ventana.destroy()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        codigo = model.get_value(f,0)
        l = Model().buscar_id_empleado(codigo)
        self.mostrar_dialogo_con_datos(l)

    def mostrar_dialogo_con_datos(self, t):
        dlg = DlgEmpleado(self.frm_padre, False)
        dlg.editando = True
        dlg.codigo.set_text(t[0][0])
        dlg.codigo.set_editable(False)
        dlg.nombre.set_text(t[0][1])
        dlg.nacionalidad.set_text(t[0][2])
        dlg.cedula.set_text(t[0][3])
        nac = t[0][4]
        ing = t[0][5]
        dlg.nac_anio.set_text(str(nac.year))
        dlg.nac_mes.set_text(str(nac.month))
        dlg.nac_dia.set_text(str(nac.day))
        dlg.ingreso_anio.set_text(str(ing.year))
        dlg.ingreso_mes.set_text(str(ing.month))
        dlg.ingreso_dia.set_text(str(ing.day))
        dlg.edad.set_text(calcular_edad(nac.year, nac.month, nac.day))
        dlg.estado_civil.set_active(int(t[0][6]))
        dlg.direccion.set_text(t[0][7])
        dlg.zona_id.set_text(t[0][8])
        dlg.zona.set_text(t[0][9])
        dlg.telefono_fijo.set_text(t[0][10])
        dlg.telefono_movil.set_text(t[0][11])
        dlg.email.set_text(t[0][12])
        dlg.tipo_id.set_text(t[0][13])
        dlg.tipo.set_text(t[0][14])
        dlg.turno_id.set_text(t[0][15])
        dlg.turno.set_text(t[0][16])
        dlg.cargo.set_text(t[0][17])
        dlg.sueldo.set_text(punto_coma(t[0][18]))
        dlg.observaciones.set_text(t[0][19])
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
           self.lista.clear()
           self.lista_ordenada_por_id()

class DlgEmpleado:
    def __init__(self, padre= None, editando = False):
        builder = gtk.Builder()
        builder.add_from_file("dlgEmpleado.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.codigo = builder.get_object("codigo")
        self.nombre = builder.get_object("nombre")
        self.nacionalidad = builder.get_object('nacionalidad')
        self.cedula = builder.get_object('cedula')
        self.nac_anio = builder.get_object('nac_anio')
        self.nac_mes = builder.get_object('nac_mes')
        self.nac_dia = builder.get_object('nac_dia')
        self.ingreso_anio = builder.get_object('ingreso_anio')
        self.ingreso_mes = builder.get_object('ingreso_mes')
        self.ingreso_dia = builder.get_object('ingreso_dia')
        self.edad = builder.get_object('edad')
        self.estado_civil = builder.get_object('estado_civil')
        self.direccion = builder.get_object("direccion")
        self.zona_id  = builder.get_object("zona_id")
        self.zona =  builder.get_object("zona")
        self.telefono_fijo = builder.get_object("telefono_fijo")
        self.telefono_movil = builder.get_object("telefono_movil")
        self.email = builder.get_object("email")
        self.tipo_id = builder.get_object("tipo_id")
        self.tipo = builder.get_object("tipo")
        self.turno_id = builder.get_object("turno_id")
        self.turno = builder.get_object("turno")
        self.cargo = builder.get_object('cargo')
        self.sueldo = builder.get_object('sueldo')
        self.observaciones = builder.get_object('observaciones')

        self.dialogo.show()

        self.nac_anio.set_text('1970')
        self.nac_mes.set_text('1')
        self.nac_dia.set_text('1')

        hoy = date.today()

        self.ingreso_anio.set_text(str(hoy.year))
        self.ingreso_mes.set_text(str(hoy.month))
        self.ingreso_dia.set_text(str(hoy.day))

        self.sueldo.set_text('0,00')

    def on_nac_anio_value_changed(self, *args):
        dia = int(self.nac_dia.get_text())
        mes = int(self.nac_mes.get_text())
        anio = int(self.nac_anio.get_text())
        edad = calcular_edad(anio,mes,dia)
        self.edad.set_text(edad)

    def on_nac_mes_value_changed(self, *args):
        dia = int(self.nac_dia.get_text())
        mes = int(self.nac_mes.get_text())
        anio = int(self.nac_anio.get_text())
        edad = calcular_edad(anio,mes,dia)
        self.edad.set_text(edad)

    def on_nac_dia_value_changed(self, *args):
        dia = int(self.nac_dia.get_text())
        mes = int(self.nac_mes.get_text())
        anio = int(self.nac_anio.get_text())
        edad = calcular_edad(anio,mes,dia)
        self.edad.set_text(edad)

    def cargar_empleado(self, t):
        self.nombre.set_text(t[0][1])
        self.nacionalidad.set_text(t[0][2])
        self.cedula.set_text(t[0][3])
        nac = t[0][4]
        ing = t[0][5]
        self.nac_anio.set_text(str(nac.year))
        self.nac_mes.set_text(str(nac.month))
        self.nac_dia.set_text(str(nac.day))
        self.ingreso_anio.set_text(str(ing.year))
        self.ingreso_mes.set_text(str(ing.month))
        self.ingreso_dia.set_text(str(ing.day))
        self.edad.set_text(calcular_edad(nac.year, nac.month, nac.day))
        self.estado_civil.set_active(int(t[0][6]))
        self.direccion.set_text(t[0][7])
        self.zona_id.set_text(t[0][8])
        self.zona.set_text(t[0][9])
        self.telefono_fijo.set_text(t[0][10])
        self.telefono_movil.set_text(t[0][11])
        self.email.set_text(t[0][12])
        self.tipo_id.set_text(t[0][13])
        self.tipo.set_text(t[0][14])
        self.turno_id.set_text(t[0][15])
        self.turno.set_text(t[0][16])
        self.cargo.set_text(t[0][17])
        self.sueldo.set_text(punto_coma(t[0][18]))
        self.observaciones.set_text(t[0][19])

    def on_codigo_changed(self, *args):
        codigo = self.codigo.get_text()
        l = Model().buscar_id_empleado(codigo)
        if l:
            self.cargar_empleado(l)
        else:
            self.limpiar()

    def on_tipo_id_changed(self, *args):
        codigo = self.tipo_id.get_text()
        l = Model().buscar_id_tipo_empleado(codigo)
        if l:
            self.tipo.set_text(l[0][1])
        else:
            self.tipo.set_text('')

    def on_zona_id_changed(self, *args):
        codigo = self.zona_id.get_text()
        l = Model().buscar_id_zona(codigo)
        if l:
            self.zona.set_text(l[0][1])
        else:
            self.zona.set_text('')

    def on_turno_id_changed(self, *args):
        codigo = self.turno_id.get_text()
        l = Model().buscar_id_turno(codigo)
        if l:
            self.turno.set_text(l[0][1])
        else:
            self.turno.set_text('')

    def on_buscar_tipo_clicked(self,*args):
        dlg = DlgBuscarTipoEmpleado()
        response = dlg.dialogo.run()
        self.tipo_id.set_text(dlg.resultado[0][0])
        self.tipo.set_text(dlg.resultado[0][1])

    def on_buscar_zona_clicked(self,*args):
        dlg = DlgBuscarZonaEmpleado()
        response = dlg.dialogo.run()
        self.zona_id.set_text(dlg.resultado[0][0])
        self.zona.set_text(dlg.resultado[0][1])

    def on_buscar_turno_clicked(self,*args):
        dlg = DlgBuscarTurnoEmpleado()
        response = dlg.dialogo.run()
        self.turno_id.set_text(dlg.resultado[0][0])
        self.turno.set_text(dlg.resultado[0][1])

    def on_nuevo_tipo_clicked(self,*args):
        dlg = DlgTipoEmpleado()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_nuevo_turno_clicked(self,*args):
        dlg = dlgTurno()
        dlg.editando = False
        response = dlg.dlgTurno.run()
        if response == gtk.RESPONSE_OK:
            dlg.dlgTurno.hide()

    def on_nueva_zona_clicked(self,*args):
        dlg = DlgZona()
        dlg.editando = False
        response = dlg.dialogo.run()
        if response == gtk.RESPONSE_OK:
            dlg.dialogo.hide()

    def on_guardar_clicked(self, *args):
        codigo = self.codigo.get_text()
        nombre = self.nombre.get_text()
        nacionalidad = self.nacionalidad.get_text()
        cedula = self.cedula.get_text()
        nac_anio = int(self.nac_anio.get_text())
        nac_mes = int(self.nac_mes.get_text())
        nac_dia = int(self.nac_dia.get_text())
        nacimiento = date.isoformat(date(nac_anio,nac_mes,nac_dia))
        ing_anio = int(self.ingreso_anio.get_text())
        ing_mes = int(self.ingreso_mes.get_text())
        ing_dia = int(self.ingreso_dia.get_text())
        ingreso = date.isoformat(date(ing_anio, ing_mes, ing_dia))
        estado_civil = self.estado_civil.get_active()
        direccion = self.direccion.get_text()
        zona = self.zona_id.get_text()
        telefono_fijo = self.telefono_fijo.get_text()
        celular = self.telefono_movil.get_text()
        email = self.email.get_text()
        tipo = self.tipo_id.get_text()
        turno = self.turno_id.get_text()
        cargo = self.cargo.get_text()
        sueldo = coma_punto(self.sueldo.get_text())
        observaciones = self.observaciones.get_text()
        lleno = self.campos_llenos(codigo, ingreso, nombre, tipo, direccion, zona, turno, cargo)

        if lleno == 1 and not self.editando:
            Model().agregar_empleado(codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona, telefono_fijo, celular, email, tipo, turno, cargo, sueldo, observaciones)
            self.limpiar_todo()
            self.codigo.grab_focus()

        if lleno == 1 and self.editando:
            Model().modificar_empleado(codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona, telefono_fijo, celular, email, tipo, turno, cargo, sueldo, observaciones)
            self.on_cancelar_clicked()

    def on_cancelar_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

    def campos_llenos(self, codigo, ingreso, nombre, tipo, direccion, zona, turno, cargo):

        if codigo == '':
            info("Debe colocar un codigo al empleado")
            return

        if nombre == '':
            info("Debe colocar un nombre al empleado")
            return

        if tipo == '':
            info("Debe seleccionar un tipo de empleado")
            return

        if zona == '':
            info('Debe seleccionar una zona para el empleado')
            return

        if ingreso == '':
            info("Debe colocar una fecha de ingreso al empleado")
            return

        if direccion == '':
            info("Debe colocar una direccion al empleado")
            return

        if turno == '':
            info("Debe seleccionar un turno al empleado")
            return

        if cargo == '':
            info("Debe colocarle un cargo al empleado")
            return

        if codigo!= '' and nombre!='' and tipo!= '' and zona!= '' and turno!= '' and ingreso!= '' and direccion!= '' and cargo != '':
            ok = 1
        else:
            ok = 0

        return ok

    #Se limpian las cajas de texto
    def limpiar_todo(self, *args):
        self.codigo.set_text("")
        self.nombre.set_text("")
        self.nacionalidad.set_text('')
        self.cedula.set_text('')
        self.nac_anio.set_text('1970')
        self.nac_mes.set_text('1')
        self.nac_dia.set_text('1')
        self.edad.set_text('')
        hoy = date.today()
        self.ingreso_anio.set_text(str(hoy.year))
        self.ingreso_mes.set_text(str(hoy.month))
        self.ingreso_dia.set_text(str(hoy.day))
        self.edad.set_text('')
        self.tipo_id.set_text("")
        self.tipo.set_text("")
        self.zona_id.set_text("")
        self.zona.set_text("")
        self.direccion.set_text("")
        self.telefono_fijo.set_text("")
        self.telefono_movil.set_text("")
        self.turno_id.set_text("")
        self.turno.set_text("")
        self.cargo.set_text('')
        self.email.set_text("")
        self.observaciones.set_text("")

    def limpiar(self, *args):
        self.nombre.set_text("")
        self.nacionalidad.set_text('')
        self.cedula.set_text('')
        self.nac_anio.set_text('1970')
        self.nac_mes.set_text('1')
        self.nac_dia.set_text('1')
        self.edad.set_text('')
        hoy = date.today()
        self.ingreso_anio.set_text(str(hoy.year))
        self.ingreso_mes.set_text(str(hoy.month))
        self.ingreso_dia.set_text(str(hoy.day))
        self.tipo_id.set_text("")
        self.tipo.set_text("")
        self.zona_id.set_text("")
        self.zona.set_text("")
        self.direccion.set_text("")
        self.telefono_fijo.set_text("")
        self.telefono_movil.set_text("")
        self.turno_id.set_text("")
        self.turno.set_text("")
        self.cargo.set_text('')
        self.email.set_text("")
        self.observaciones.set_t


class DlgBuscarZonaEmpleado:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Zona_Proveedor.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.lblValor = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.tree = builder.get_object("tree")
        self.lista = builder.get_object('lista')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.padre = padre
        self.resultado = ''
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().zonas_ordenadas_por_id()
        self.cargar_lista(c)

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Nombre')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_zona(id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_zona(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_zona(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            info('Debe seleccionar un criterio de búsqueda')
            return

    def on_limpiar_clicked(self, *args):
        self.valor.set_text('')
        self.valor.grab_focus()
        self.lista_ordenada_por_id()

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.dialogo.destroy()

class DlgBuscarTipoEmpleado:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Tipo_de_Empleado_Para_Empleado.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.lblValor = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.tree = builder.get_object("tree")
        self.lista = builder.get_object('lista')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.padre = padre
        self.resultado = ''
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().tipos_de_empleados_ordenados_por_id()
        self.cargar_lista(c)

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Tipo')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_aceptar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_tipo_empleado(id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_tipo_empleado(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_tipo_empleado(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            info('Debe seleccionar un criterio de búsqueda')
            return

    def on_limpiar_clicked(self, *args):
        self.valor.set_text('')
        self.valor.grab_focus()
        self.lista_ordenada_por_id()

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.on_dialogo_destroy()

    def on_dialogo_destroy(self, *args):
        self.dialogo.destroy()

class DlgBuscarTurnoEmpleado:
    def __init__(self, padre = None):
        builder = gtk.Builder()
        builder.add_from_file("wBuscar_Turno_Para_Empleado.glade")
        builder.connect_signals(self)

        self.dialogo = builder.get_object("dialogo")
        self.lblValor = builder.get_object('lblValor')
        self.valor = builder.get_object("valor")
        self.criterio = builder.get_object("criterio")
        self.tree = builder.get_object("tree")
        self.lista = builder.get_object('lista')
        self.resultado = ''
        self.lista_ordenada_por_id()
        self.padre = padre
        self.resultado = ''
        self.dialogo.show()

    def lista_ordenada_por_id(self,*args):
        c = Model().turnos_ordenados_por_id()
        self.cargar_lista(c)

    def cargar_lista(self, tupla):
        self.lista.clear()
        x = len(tupla)
        for f in range(x):
            self.lista.append([tupla[f][0],tupla[f][1]])

    def on_criterio_changed(self, *args):

        if self.criterio.get_active() == 0:
            self.lblValor.set_text('Codigo')
            self.valor.set_text('')
            self.valor.grab_focus()

        elif self.criterio.get_active() == 1:
            self.lblValor.set_text('Turnos')
            self.valor.set_text('')
            self.valor.grab_focus()

    def on_valor_changed(self, *args):
        self.on_buscar_clicked()

    def on_tree_row_activated(self, *args):
        (model, f) = self.tree.get_selection().get_selected()
        id = model.get_value(f,0)
        self.resultado = Model().buscar_id_turno(id)
        self.dialogo.destroy()

    def on_buscar_clicked(self, *args):

        if self.criterio.get_active() == 0:
            self.resultado = Model().buscar_id_turno(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == 1:
            self.resultado = Model().buscar_nombre_turno(self.valor.get_text())
            self.cargar_lista(self.resultado)

        elif self.criterio.get_active() == -1:
            info('Debe seleccionar un criterio de búsqueda')
            return

    def on_limpiar_clicked(self, *args):
        self.valor.set_text('')
        self.valor.grab_focus()
        self.lista_ordenada_por_id()

    def on_aceptar_clicked(self, *args):
        pass

    def on_salir_clicked(self, *args):
        self.dialogo.destroy()

if __name__ == '__main__':
    p = Empleados()
    p.main()
