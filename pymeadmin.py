#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       wprincipal.py
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


import gtk
import os
from empresas import Empresas
from monedas import Monedas
from depositos import Depositos
from grupos import Grupos
from articulos import Articulos
from zonas import Zonas
from tipos_proveedores import TiposProveedores
from proveedores import Proveedores
from tipos_clientes import TiposClientes
from clientes import Clientes
from asistencias import Asistencias
from movimientos import Movimientos
from despachos import Despachos
from compras import Compras
from ventas import Ventas
from produccion_panaderia import ProduccionPanaderia
from produccion_pasteleria import ProduccionPasteleria
from recetas_panaderia import RecetasDePanaderia
from recetas_pasteleria import RecetasDePasteleria
from recetas_tortas import RecetasTortas
from operaciones import Operaciones
from tarjeta_debito import TarjetasDeDebito
from tarjeta_credito import TarjetasDeCredito
from bancos import Bancos
from turnos import Turnos
from empleados_tipos import TiposEmpleados
from empleados import Empleados
from periodo_inventario import PeriodoInventario
from libro_compras import LibroDeCompras
from libro_ventas import LibroDeVentas
from creditos import DlgAcerca
from filtro_fechas_compras import Periodo
from filtro_fechas_ventas import Periodo
from configuracion_ids_iniciales import Ids


rDir = os.getcwd()
os.chdir(rDir)

class Principal:

    def main(self):
        gtk.main()
        return 0

    def __init__(self):

        builder = gtk.Builder()
        builder.add_from_file("pymeadmin.glade")
        builder.connect_signals(self)

        #Se llaman las objetos del archivo wprincipal.glade
        self.ventana = builder.get_object("ventana")
        self.frm_padre = self.ventana
        self.ventana.show

    def on_item_empresa_activate(self, *args):
        Empresas(self)

    def on_item_moneda_activate(self, *args):
        Monedas(self)

    def on_item_zona_activate(self, *args):
        Zonas(self)

    def on_item_tipo_proveedor_activate(self, *args):
        TiposProveedores(self)

    def on_item_tipo_cliente_activate(self, *args):
        TiposClientes(self)

    def on_item_proveedor_activate(self, *args):
        Proveedores(self)

    def on_item_cliente_activate(self, *args):
        Clientes(self)

    def on_item_deposito_activate(self, *args):
        Depositos(self)

    def on_item_grupo_activate(self, *args):
        Grupos(self)

    def on_item_articulo_activate(self, *args):
        Articulos(self)

    def on_item_recetas_panaderia_activate(self, *args):
        RecetasDePanaderia(self)

    def on_item_recetas_pasteleria_activate(self, *args):
        RecetasDePasteleria(self)

    def on_item_asistencias_activate(self, *args):
        Asistencias(self)

    def on_item_movimiento_activate(self, *args):
        Movimientos(self)

    def on_item_despachos_activate(self, *args):
        Despachos(self)

    def on_item_compra_activate(self, *args):
        Compras(self)

    def on_item_venta_activate(self, *args):
        Ventas(self)

    def on_item_produccion_panaderia_activate(self, *args):
        ProduccionPanaderia(self)

    def on_item_salir_activate(self, *args):
        gtk.main_quit(self)

    def on_item_autor_activate(self, *args):
        DlgAcerca()

    def on_item_operacion_activate(self, *args):
        Operaciones(self)

    def on_item_tarjetas_debito_activate(self, *args):
        TarjetasDeDebito(self)

    def on_item_tarjetas_credito_activate(self, *args):
        TarjetasDeCredito(self)

    def on_item_banco_activate(self, *args):
        Bancos(self)

    def on_item_horario_activate(self, *args):
        Turnos(self)

    def on_item_tipo_empleado_activate(self, *args):
        TiposEmpleados(self)

    def on_item_empleados_activate(self, *args):
        Empleados(self)

    def on_item_libro_inventario_activate(self, *args):
        PeriodoInventario(self)

    def on_item_libro_compras_activate(self, *args):
        Periodo()

    def on_item_libro_ventas_activate(self, *args):
        Periodo()

    def on_item_respaldar_activate(self, *args):
        os.system('sudo ./respaldar.sh')

    def on_item_restaurar_activate(self, *args):
        os.system('sudo ./respaldar.sh')

    def on_item_configurar_ids_activate(self, *args):
        Ids()

    def on_ventana_destroy(self,*args):
        gtk.main_quit(self)

if __name__ == "__main__":
    Principal().main()
