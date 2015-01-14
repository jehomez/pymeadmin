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

from psycopg2 import connect
from mensajes import info, yesno
from decimal import Decimal
from datetime import date
from mensajes import info
from comunes import calcular_precio_neto, calcular_precio_venta, calcular_iva_venta, coma_punto, punto_coma
import sys


class Model:

    def conectar(self):
        try:
            self.cnn = connect("dbname='admin0' user='postgres' password='root' host='localhost' port='5432'");
            #self.cnn = connect("dbname='admin0' user='postgres' password='root' host='192.168.10.105' port='5432'");
            self.cursor = self.cnn.cursor()
        except:
            info('No se pudo establecer la conexion')

    def desconectar(self):
        self.cursor.close()
        self.cnn.commit()
        self.cnn.close()

    def contar_registros(self, tabla):
        self.conectar()
        sql = "SELECT count(*) FROM %s" % (tabla)
        self.cursor.execute(sql)
        registros = self.cursor.fetchone()
        self.desconectar()
        return registros

    def contar_proveedores(self, articulo):
        self.conectar()
        sql = "SELECT count(*) FROM articulos_proveedores where articulo_id = '%s'" % (articulo)
        self.cursor.execute(sql)
        registros = self.cursor.fetchone()
        self.desconectar()
        return registros

    def contar_ingredientes(self):
        self.conectar()
        sql = """
                SELECT
                    COUNT(*)
                FROM
                    articulos
                INNER JOIN depositos
                ON  depositos.deposito_id = articulos.deposito_id
                WHERE
                    articulos.deposito_id = '01'"""
        self.cursor.execute(sql)
        registros = self.cursor.fetchone()
        self.desconectar()
        return registros

    def contar_articulos_asociados_a_proveedor(self, proveedor):
        self.conectar()
        sql = """select a.articulo_id,
                        a.nombre,
                        a.costo_actual,
                        a.existencia
                from articulos a
                inner join articulos_proveedores p
                    on p.articulo_id = a.articulo_id
                where p.proveedor_id = '%s'
            """ % (proveedor)
        self.cursor.execute(sql)
        filas = self.cursor.rowcount
        self.desconectar()
        return filas

    # Modelo para Despachos
    def agregar_despacho(self, empleado_id, emision, bruto, impuestos, total):
        self.conectar()
        sql = """INSERT INTO despachos(empleado_id, emision, bruto, impuestos, total)
                 VALUES ('%s', '%s', '%.2f', '%.2f', '%.2f' ) returning despacho_id
                 """ % (empleado_id, emision, bruto, impuestos, total)
        self.cursor.execute(sql)
        oid = self.cursor.fetchone()
        self.desconectar()
        return oid

    def produccion_procesada(self, produccion_id):
        self.conectar()
        sql = """UPDATE produccion
                    set estado = 'Procesada'
                WHERE produccion_id = '%s' and estado = 'Sin procesar'""" % produccion_id
        self.cursor.execute(sql)
        modificado = self.cursor.rowcount
        self.desconectar()
        return modificado

    def agregar_despacho_detalles(self, despacho_id, cantidad, articulo_id, total_neto):
        self.conectar()
        sql = """INSERT INTO despacho_detalles(despacho_id, cantidad, articulo_id, total_neto) VALUES ('%i', '%.3f', '%s', '%.2f' )
                 """ % (despacho_id, cantidad, articulo_id, total_neto)
        self.cursor.execute(sql)
        renglones = self.cursor.rowcount
        self.desconectar()
        return renglones

    def buscar_id_despacho(self, codigo):
        self.conectar()
        sql = """SELECT d.despacho_id, d.emision, d.empleado_id, e.nombre, d.bruto, d.impuestos, d.total
                FROM despachos d
                INNER JOIN empleados e
                    ON  d.empleado_id = e.empleado_id
                WHERE d.despacho_id = %i
            """ % codigo
        self.cursor.execute(sql)
        despacho = self.cursor.fetchone()
        self.desconectar()
        return despacho

    def buscar_detalles_id_despacho(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    de.cantidad,
                    de.articulo_id,
                    ar.nombre,
                    ar.costo_actual,
                    ar.unidad,
                    ar.iva_compra,
                    round((ar.iva_compra/100) * ar.costo_actual,2) as monto_iva_compra,
                    de.total_neto
                FROM
                    despacho_detalles de
                INNER JOIN
                    articulos ar
                ON
                    de.articulo_id = ar.articulo_id
                INNER JOIN
                    despachos d
                ON
                    de.despacho_id = d.despacho_id
                WHERE
                    de.despacho_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles

    def buscar_fecha_despacho(self, fecha):
        self.conectar()
        sql = """SELECT d.despacho_id, d.emision, d.empleado_id, e.nombre, d.bruto, d.impuestos, d.total
                FROM despachos d
                INNER JOIN empleados e
                    ON  d.empleado_id = e.empleado_id
                WHERE d.emision = '%s'
            """ % fecha
        self.cursor.execute(sql)
        despacho = self.cursor.fetchall()
        self.desconectar()
        return despacho

    def buscar_empleado_despacho(self, empleado):
        self.conectar()
        empleado = empleado.upper() + '%'
        sql = """SELECT d.despacho_id, d.emision, d.empleado_id, e.nombre, d.bruto, d.impuestos, d.total
                FROM despachos d
                INNER JOIN empleados e
                    ON  d.empleado_id = e.empleado_id
                WHERE upper(e.nombre) LIKE '%s'
            """ % empleado
        self.cursor.execute(sql)
        despacho = self.cursor.fetchall()
        self.desconectar()
        return despacho

    def despachos_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT d.despacho_id, d.emision, d.empleado_id, e.nombre, d.bruto, d.impuestos, d.total
                    FROM despachos d
                    INNER JOIN empleados e
                        ON d.empleado_id = e.empleado_id
                    ORDER BY d.despacho_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    #Modelo para compras
    def agregar_compra(self, compra_id, proveedor_id, orden, deposito_id, emision, vence, bruto, impuestos, total):
        self.conectar()
        sql = """INSERT INTO
                    compras(compra_id, 
							proveedor_id, 
							orden_compra, 
							deposito_id, 
							emision, 
							vence, 
							bruto, 
							impuestos, 
							total)
                 VALUES
                    ('%s', 
                    '%s', 
                    '%s', 
                    '%s', 
                    '%s', 
                    '%s', 
                    '%.2f', 
                    '%.2f', 
                    '%.2f' )
                 """ % (compra_id, proveedor_id, orden, deposito_id, emision, vence, bruto, impuestos, total)
        self.cursor.execute(sql)
        compra = self.cursor.rowcount
        self.desconectar()
        return compra

    def agregar_compra_detalles(self, compra_id, cantidad, articulo_id, costo, monto_iva_compra, total_neto):
        self.conectar()
        sql = """
                INSERT INTO compras_detalles
						(compra_id, 
							cantidad, 
							articulo_id, 
							costo, 
							monto_iva_compra, 
							total_neto) VALUES ('%s', '%.3f', '%s', '%.2f', '%f', '%.2f')
                 """ % (compra_id, cantidad, articulo_id, costo, monto_iva_compra, total_neto)
        self.cursor.execute(sql)
        renglones = self.cursor.rowcount
        self.desconectar()
        return renglones

    def buscar_id_compra(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    c.compra_id,
                    c.proveedor_id,
                    p.nombre,
                    p.proveedor_id,
                    p.dias,
                    c.orden_compra,
                    c.deposito_id,
                    d.nombre,
                    c.emision,
                    c.vence,
                    c.bruto,
                    c.impuestos,
                    c.total
                FROM
                    compras c
                INNER JOIN
                    proveedores p
                ON
                    c.proveedor_id = p.proveedor_id
                INNER JOIN
                    depositos d
                ON
                    c.deposito_id = d.deposito_id
                WHERE
                    c.compra_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        compra = self.cursor.fetchone()
        self.desconectar()
        return compra

    def buscar_detalles_id_compra(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    cd.cantidad,
                    cd.articulo_id,
                    ar.nombre,
                    cd.costo,
                    ar.iva_compra,
                    cd.monto_iva_compra,
                    cd.total_neto
                FROM
                    compras_detalles cd
                INNER JOIN
                    articulos ar
                ON
                    cd.articulo_id = ar.articulo_id
                INNER JOIN
                    compras c
                ON
                    cd.compra_id = c.compra_id
                WHERE
                    c.compra_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles

    def buscar_fecha_compra(self, fecha):
        self.conectar()
        sql = """SELECT
                    c.compra_id,
                    c.proveedor_id,
                    p.nombre,
                    p.proveedor_id,
                    p.dias,
                    c.orden_compra,
                    c.deposito_id,
                    d.nombre,
                    c.emision,
                    c.vence,
                    c.bruto,
                    c.impuestos,
                    c.total
                FROM
                    compras c
                INNER JOIN
                    proveedores p
                ON
                    c.proveedor_id = p.proveedor_id
                INNER JOIN
                    depositos d
                ON
                    c.deposito_id = d.deposito_id
                WHERE c.emision = '%s'
            """ % fecha
        self.cursor.execute(sql)
        compra = self.cursor.fetchall()
        self.desconectar()
        return compra

    def buscar_proveedor_compra(self, proveedor):
        self.conectar()
        proveedor = proveedor.upper() + '%'
        sql = """SELECT
                    c.compra_id,
                    c.proveedor_id,
                    p.nombre,
                    p.proveedor_id,
                    p.dias,
                    c.orden_compra,
                    c.deposito_id,
                    d.nombre,
                    c.emision,
                    c.vence,
                    c.bruto,
                    c.impuestos,
                    c.total
                FROM
                    compras c
                INNER JOIN
                    proveedores p
                ON
                    c.proveedor_id = p.proveedor_id
                INNER JOIN
                    depositos d
                ON
                    c.deposito_id = d.deposito_id
                WHERE upper(p.nombre) LIKE '%s'
            """ % proveedor
        self.cursor.execute(sql)
        compra = self.cursor.fetchall()
        self.desconectar()
        return compra

    def compras_ordenadas_por_fecha(self):
        self.conectar()
        sql = """
                SELECT
                    c.compra_id,
                    c.proveedor_id,
                    p.nombre,
                    p.proveedor_id,
                    p.dias,
                    c.orden_compra,
                    c.deposito_id,
                    d.nombre,
                    c.emision,
                    c.vence,
                    c.bruto,
                    c.impuestos,
                    c.total
                FROM
                    compras c
                INNER JOIN
                    proveedores p
                ON
                    c.proveedor_id = p.proveedor_id
                INNER JOIN
                    depositos d
                ON
                    c.deposito_id = d.deposito_id
                ORDER BY
                    c.emision
            """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    #Modelo para ventas
    def agregar_venta(self, venta_id, cliente_id, emision, bruto, impuestos, total):
        self.conectar()
        sql = """INSERT INTO
                    ventas(venta_id, cliente_id, emision, bruto, impuestos, total)
                 VALUES
                    ('%s', '%s', '%s', '%.2f', '%.2f', '%.2f' )
                 """ % (venta_id, cliente_id, emision, bruto, impuestos, total)
        self.cursor.execute(sql)
        venta = self.cursor.rowcount
        self.desconectar()
        return venta

    def agregar_venta_detalles(self, venta_id, emision, cantidad, articulo_id, precio, monto_iva_venta, subtotal):
        self.conectar()
        sql = """
                INSERT INTO ventas_detalles(venta_id, cantidad, articulo_id, precio, monto_iva_venta, subtotal) VALUES ('%s', '%.3f', '%s', '%.2f', '%.2f', '%.2f')
                 """ % (venta_id, cantidad, articulo_id, precio, monto_iva_venta, subtotal)
        self.cursor.execute(sql)
        renglones = self.cursor.rowcount
        self.desconectar()
        return renglones

    def procesar_venta(self, venta_id):
        self.conectar()
        sql = """UPDATE ventas SET procesada = 'si' WHERE venta_id = '%s'""" % (venta_id)
        self.cursor.execute(sql)
        self.desconectar()

    def insertar_nro_cliente(self, nro_cliente, venta_id):
        self.conectar()
        sql = "INSERT INTO numero_clientes(nro_cliente, nro_factura) VALUES ('%s', '%s')" % (nro_cliente, venta_id)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_nro_cliente(self, nro_cliente):
        self.conectar()
        sql = "SELECT nro_cliente, nro_factura FROM numero_clientes WHERE nro_cliente = '%s'" % (nro_cliente)
        self.cursor.execute(sql)
        cliente = self.cursor.fetchone()
        self.desconectar()
        return cliente

    def eliminar_nro_cliente(self, venta_id):
        self.conectar()
        sql = "DELETE FROM numero_clientes WHERE nro_factura = '%s'" % (venta_id)
        self.cursor.execute(sql)
        self.desconectar()

    def nro_clientes_ordenados(self):
        self.conectar()
        sql = 'SELECT nro_cliente, nro_factura FROM numero_clientes ORDER BY nro_cliente'
        self.cursor.execute(sql)
        clientes = self.cursor.fetchall()
        self.desconectar()
        return clientes

    def buscar_id_venta(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    v.venta_id,
                    v.cliente_id,
                    c.nombre,
                    v.emision,
                    v.bruto,
                    v.impuestos,
                    v.total,
                    v.procesada
                FROM
                    ventas v
                INNER JOIN
                    clientes c
                ON
                    c.cliente_id = v.cliente_id
                WHERE
                    v.venta_id = '%s'""" % codigo
        self.cursor.execute(sql)
        venta = self.cursor.fetchone()
        self.desconectar()
        return venta

    def buscar_detalles_id_venta(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    vd.cantidad,
                    vd.articulo_id,
                    ar.nombre,
                    vd.precio,
                    ar.iva_venta,
                    vd.monto_iva_venta,
                    vd.subtotal
                FROM
                    ventas_detalles vd
                INNER JOIN
                    articulos ar
                ON
                    vd.articulo_id = ar.articulo_id
                INNER JOIN
                    ventas v
                ON
                    vd.venta_id = v.venta_id
                WHERE
                    v.venta_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles

    def buscar_fecha_venta(self, fecha):
        self.conectar()
        sql = """SELECT
                    c.compra_id,
                    c.proveedor_id,
                    p.nombre,
                    p.proveedor_id,
                    p.dias,
                    c.orden_compra,
                    c.deposito_id,
                    d.nombre,
                    c.emision,
                    c.vence,
                    c.bruto,
                    c.impuestos,
                    c.total
                FROM
                    compras c
                INNER JOIN
                    proveedores p
                ON
                    c.proveedor_id = p.proveedor_id
                INNER JOIN
                    depositos d
                ON
                    c.deposito_id = d.deposito_id
                WHERE c.emision = '%s'
            """ % fecha
        self.cursor.execute(sql)
        compra = self.cursor.fetchall()
        self.desconectar()
        return compra

    def buscar_cliente_venta(self, proveedor):
        self.conectar()
        proveedor = proveedor.upper() + '%'
        sql = """SELECT
                    c.compra_id,
                    c.proveedor_id,
                    p.nombre,
                    p.proveedor_id,
                    p.dias,
                    c.orden_compra,
                    c.deposito_id,
                    d.nombre,
                    c.emision,
                    c.vence,
                    c.bruto,
                    c.impuestos,
                    c.total
                FROM
                    compras c
                INNER JOIN
                    proveedores p
                ON
                    c.proveedor_id = p.proveedor_id
                INNER JOIN
                    depositos d
                ON
                    c.deposito_id = d.deposito_id
                WHERE upper(p.nombre) LIKE '%s'
            """ % proveedor
        self.cursor.execute(sql)
        compra = self.cursor.fetchall()
        self.desconectar()
        return compra

    def ventas_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT
                    v.venta_id,
                    v.emision,
                    c.nombre,
                FROM
                    ventas v
                INNER JOIN
                    clientes c
                ON
                    v.cliente_id = c.cliente_id
                ORDER BY
                    v.venta_id
            """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    #~ Modelo para Empresas
    def agregar_empresa(self, codigo, rif, empresa, direccion, telefonos, fax, email, web, contacto):
        self.conectar()
        sql = """
            INSERT INTO empresas
                        (empresa_id,
                        rif,
                        empresa,
                        direccion,
                        telefonos,
                        fax,
                        email,
                        web,
                        contacto)
            VALUES  ('%s',
                    '%s',
                    '%s',
                    '%s',
                    '%s',
                    '%s',
                    '%s',
                    '%s',
                    '%s')
        """ % (codigo, rif, empresa, direccion, telefonos, fax, email, web, contacto)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_empresa(self, codigo, rif, empresa, direccion, telefonos, fax, email, web, contacto):
        self.conectar()
        sql = """
                UPDATE empresas
                    SET rif ='%s',
                        empresa = '%s',
                        direccion = '%s',
                        telefonos = '%s',
                        fax = '%s',
                        email = '%s',
                        web = '%s',
                        contacto = '%s'
                WHERE empresa_id = '%s'
            """ % (rif, empresa, direccion, telefonos, fax, email, web, contacto, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_empresa(self, codigo):
        self.conectar()
        sql = "DELETE FROM empresas WHERE empresa_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_empresa(self, codigo):
        self.conectar()
        sql = """
            SELECT  empresa_id,
                    rif,
                    empresa,
                    direccion,
                    telefonos,
                    fax,
                    email,
                    web,
                    contacto
            FROM empresas
            WHERE empresa_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchall()
        self.desconectar
        return nombre

    def buscar_nombre_empresa(self, empresa):
        self.conectar()
        empresa = empresa.upper() + '%'
        sql = """
            SELECT  empresa_id,
                    rif,
                    empresa,
                    direccion,
                    telefonos,
                    fax,
                    email,
                    web,
                    contacto
            FROM empresas
            WHERE UPPER(empresa) LIKE '%s'
        """ % (empresa)
        self.cursor.execute(sql)
        empresa = self.cursor.fetchall()
        self.desconectar
        return empresa

    def empresas_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT  empresa_id,
                        rif,
                        empresa,
                        direccion,
                        telefonos,
                        fax,
                        email,
                        web,
                        contacto
                FROM empresas
                ORDER BY empresa_id
                """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #~ Modelo para Monedas
    def agregar_moneda(self, codigo, nombre, plural, simbolo):
        self.conectar()
        a = nombre.upper()
        sql = """
            INSERT INTO monedas
                        (moneda_id,
                        nombre,
                        plural,
                        simbolo)
            VALUES  ('%s',
                    '%s',
                    '%s',
                    '%s')
        """ % (codigo, nombre, plural, simbolo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_moneda(self, codigo, nombre, plural, simbolo):
        self.conectar()
        sql = """
                UPDATE monedas
                    SET nombre ='%s',
                        plural = '%s',
                        simbolo = '%s'
                WHERE moneda_id = '%s'
            """ % (nombre, plural, simbolo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_moneda(self, codigo):
        self.conectar()
        sql = "DELETE FROM monedas WHERE moneda_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_moneda(self, codigo):
        self.conectar()
        sql = """
            SELECT  moneda_id,
                    nombre,
                    plural,
                    simbolo
            FROM monedas
            WHERE moneda_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchall()
        self.desconectar
        return nombre

    def buscar_nombre_monedas(self, moneda):
        self.conectar()
        moneda = moneda + '%'
        sql = """
            SELECT  moneda_id,
                    nombre,
                    plural,
                    simbolo
            FROM monedas
            WHERE nombre LIKE '%s'
        """ % (empresa)
        self.cursor.execute(sql)
        empresa = self.cursor.fetchall()
        self.desconectar
        return empresa

    def monedas_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT  moneda_id,
                        nombre,
                        plural,
                        simbolo
                FROM monedas
                ORDER BY moneda_id
                """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

#Modelo para Tipos de recetas
    def agregar_tipo_receta(self, codigo, descripcion):
        self.conectar()
        descripcion = descripcion.upper()
        sql = "INSERT INTO recetas_tipos ( tipo_receta_id, descripcion) VALUES( '%s','%s')" % (codigo, tipo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_tipo_receta(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "UPDATE recetas_tipos SET descripcion ='%s' WHERE tipo_receta_id = '%s'" % (tipo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_tipo_receta(self, codigo):
        self.conectar()
        sql = "DELETE FROM recetas_tipos WHERE tipo_receta_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_tipo_receta(self, codigo):
        self.conectar()
        sql = "SELECT tipo_receta_id, descripcion FROM recetas_tipos WHERE tipo_receta_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchone()
        self.desconectar
        return tipo

    def buscar_tipo_receta(self, tipo):
        self.conectar()
        tipo = tipo.upper()+'%'
        sql = "SELECT tipo_receta_id, descripcion FROM recetas_tipos WHERE upper(descripcion) LIKE '%s'" % (tipo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def tipos_de_recetas_ordenadas_por_id(self):
        self.conectar()
        sql = "SELECT tipo_receta_id, descripcion FROM recetas_tipos ORDER BY tipo_receta_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

 # Modelo para Produccion
    def agregar_produccion(self, fecha, estado, harina_arroba, harina_kg, harina_bultos, costos):
        self.conectar()
        sql =  "INSERT INTO produccion (fecha, estado, harina_arroba, harina_kg, harina_bultos, costos) VALUES ('%s', '%s', '%.3f', '%.3f', '%.3f', '%.2f') returning produccion_id" % (fecha, estado, harina_arroba, harina_kg, harina_bultos, costos)
        self.cursor.execute(sql)
        produccion_id = self.cursor.fetchone()
        self.desconectar()
        return produccion_id

    def modificar_produccion(self, estado, harina_arroba, harina_kg, harina_bultos, costos, produccion_id):
        self.conectar()
        sql =  """UPDATE produccion
                    SET estado = '%S',
                        harina_arroba = '%.3f',
                        harina_kg = '%.3f',
                        harina_bultos = '%.3f',
                        costos = '%.2f'
                    WHERE produccion_id = '%i'""" % ( estado, harina_arroba, harina_kg, harina_bultos, costos, produccion_id)
        self.cursor.execute(sql)
        modificado = self.cursor.rowcount
        self.desconectar()
        return modificado

    def agregar_produccion_detalles(self, produccion_id, receta_id, cantidad_harina, unidades, costo, empleado_id):
        self.conectar()
        sql = """INSERT INTO produccion_detalles(produccion_id, receta_id, cantidad_harina, unidades_producidas, costo, empleado_id) VALUES ('%i', '%s', '%.3f', '%.2f', '%.2f', '%s'  )""" % (produccion_id, receta_id, cantidad_harina, unidades, costo, empleado_id)
        self.cursor.execute(sql)
        renglones = self.cursor.rowcount
        self.desconectar()
        return renglones

    def eliminar_produccion(self, codigo):
        self.conectar()
        sql = "DELETE FROM produccion_detalles WHERE produccion_id = %i" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()
        self.conectar()
        sql = "DELETE FROM produccion WHERE produccion_id = %i" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_produccion(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    produccion_id,
                    fecha,
                    estado,
                    harina_arroba,
                    harina_kg,
                    harina_bultos,
                    costos
                FROM
                    produccion
                WHERE
                    produccion_id = '%s'""" % codigo
        self.cursor.execute(sql)
        listado = self.cursor.fetchone()
        self.desconectar()
        return listado

    def buscar_detalles_id_produccion(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    pd.receta_id,
                    r.nombre,
                    pd.cantidad_harina,
                    pd.unidades_producidas,
                    pd.costo,
                    e.nombre
                FROM
                    produccion_detalles pd
                INNER JOIN
                    recetas r
                ON
                    pd.receta_id = r.receta_id
                INNER JOIN
                    empleados e
                ON
                    pd.empleado_id = e.empleado_id
                INNER JOIN
                    produccion p
                ON
                    pd.produccion_id = p.produccion_id
                WHERE
                    p.produccion_id = '%s'""" % codigo
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def producciones_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT
                    produccion_id,
                    fecha,
                    estado,
                    costos
                FROM
                    produccion
                ORDER BY
                    produccion_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

 #~ Modelo para Recetas para panes
    def agregar_receta(self, receta_id, nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total):
        self.conectar()
        nombre = nombre.upper()
        sql = "INSERT INTO recetas (receta_id, nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total) VALUES ('%s', '%s', '%s', '%s', '%s', '%.3f', '%.3f', '%.2f', '%.2f', '%.3f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f')" % (receta_id, nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total)
        self.cursor.execute(sql)
        receta = self.cursor.rowcount
        self.desconectar()
        return receta

    def modificar_receta(self, nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total, receta_id):
        self.conectar()
        sql = """
                UPDATE recetas
                    SET nombre = '%s',
                        tipo_receta_id = '%s',
                        articulo_id = '%s',
                        masa = '%.3f',
                        pesada = '%.3f',
                        porciones = '%.2f',
                        tacos = '%.2f',
                        peso_taco = '%.3f',
                        panes = '%.2f',
                        costo = '%.2f',
                        bruto = '%.2f',
                        impuestos = '%.2f',
                        mano_obra = '%.2f',
                        total = '%.2f'
                WHERE receta_id = '%s'
            """ % (nombre, tipo_receta_id, articulo_id, masa, pesada, porciones, tacos, peso_taco, panes, costo, bruto, impuestos, mano_obra, total, receta_id)
        self.cursor.execute(sql)
        registro = self.cursor.rowcount
        self.desconectar()
        return registro

    def eliminar_receta(self, codigo):
        self.conectar()
        sql = "DELETE FROM recetas WHERE receta_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_receta(self, codigo):
        self.conectar()
        sql = """
            SELECT
                re.receta_id,
                re.tipo_receta_id,
                tr.descripcion,
                re.nombre,
                re.articulo_id,
                ar.nombre,
                re.masa,
                re.pesada,
                re.porciones,
                re.tacos,
                re.peso_taco,
                re.panes,
                re.costo,
                re.bruto,
                re.impuestos,
                re.mano_obra,
                re.total
            FROM
                recetas re
            INNER JOIN
                articulos ar
            ON
                re.articulo_id = ar.articulo_id
            INNER JOIN
                recetas_tipos tr
            ON
                re.tipo_receta_id = tr.tipo_receta_id
            WHERE
                re.receta_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchone()
        self.desconectar
        return nombre

    def buscar_id_receta_de_pan_para_produccion(self, codigo):
        self.conectar()
        sql = """
            SELECT
                re.receta_id,
                re.nombre
            FROM
                recetas re
            WHERE
                re.receta_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchone()
        self.desconectar
        return nombre

    def buscar_id_receta_pan_arroba(self, codigo):
        self.conectar()
        sql = """
            SELECT
                re.receta_id,
                re.tipo_receta_id,
                tr.descripcion,
                re.nombre,
                re.articulo_id,
                ar.nombre,
                re.masa/4 as masa,
                re.pesada/4 as pesada,
                re.porciones/4 as porciones,
                re.tacos/4 as tacos,
                re.peso_taco/4 as peso_taco,
                re.panes/4 as panes,
                re.costo/4 as costo,
                re.bruto/4 as bruto,
                re.impuestos/4 as impuestos,
                re.mano_obra/4 as mano_obra,
                re.total/4 as total
            FROM
                recetas re
            INNER JOIN
                articulos ar
            ON
                re.articulo_id = ar.articulo_id
            INNER JOIN
                recetas_tipos tr
            ON
                re.tipo_receta_id = tr.tipo_receta_id
            WHERE
                re.receta_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchone()
        self.desconectar
        return nombre

    def buscar_nombre_receta(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """
            SELECT  receta_id,
                    nombre,
            FROM recetas
            WHERE upper(nombre) LIKE '%s'
        """ % (nombre)
        self.cursor.execute(sql)
        receta = self.cursor.fetchall()
        self.desconectar
        return receta

    def recetas_de_panes_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT  receta_id,
                        nombre
                FROM recetas
                ORDER BY receta_id
                """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def recetas_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT  receta_id,
                        nombre
                FROM recetas
                ORDER BY receta_id
                union
                select receta_tortas_id, nombre
                from recetas_tortas

                """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def agregar_recetas_detalles(self, receta_id, cantidad, articulo_id, total_neto):
        self.conectar()
        sql = """INSERT INTO recetas_detalles(receta_id, cantidad, articulo_id, total_neto) VALUES ('%s', '%.3f', '%s', '%.2f' )""" % (receta_id, cantidad, articulo_id, total_neto)
        self.cursor.execute(sql)
        renglones = self.cursor.rowcount
        self.desconectar()
        return renglones
        if renglones:
            info('Registro insertado con éxito')

    def buscar_detalles_id_receta(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    rd.cantidad,
                    rd.articulo_id,
                    ar.nombre,
                    ar.costo_actual,
                    ar.unidad,
                    ar.iva_compra,
                    round((ar.iva_compra/100) * rd.total_neto,2) as monto_iva_compra,
                    rd.total_neto
                FROM
                    recetas_detalles rd
                INNER JOIN
                    articulos ar
                ON
                    rd.articulo_id = ar.articulo_id
                INNER JOIN
                    recetas r
                ON
                    rd.receta_id = r.receta_id
                WHERE
                    r.receta_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles

    def buscar_detalles_id_receta_arroba(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    rd.cantidad/4 as cantidad,
                    rd.articulo_id,
                    ar.nombre,
                    ar.costo_actual/4 as costo_actual,
                    '@',
                    ar.iva_compra,
                    round((ar.iva_compra/100) * (rd.total_neto/4),2) as monto_iva_compra,
                    rd.total_neto/4 as total_neto
                FROM
                    recetas_detalles rd
                INNER JOIN
                    articulos ar
                ON
                    rd.articulo_id = ar.articulo_id
                INNER JOIN
                    recetas r
                ON
                    rd.receta_id = r.receta_id
                WHERE
                    r.receta_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles

    def modificar_receta_arroba(self, arrobas):
        self.conectar()
        sql = """
                SELECT
                    rd.cantidad/4 as cantidad,
                    rd.articulo_id,
                    ar.nombre,
                    ar.costo_actual/4 as costo_actual,
                    '@',
                    ar.iva_compra,
                    round((ar.iva_compra/100) * (rd.total_neto/4),2) as monto_iva_compra,
                    rd.total_neto/4 as total_neto
                FROM
                    recetas_detalles rd
                INNER JOIN
                    articulos ar
                ON
                    rd.articulo_id = ar.articulo_id
                INNER JOIN
                    recetas r
                ON
                    rd.receta_id = r.receta_id
                WHERE
                    r.receta_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles


#~ Modelo para Recetas para tortas
    def agregar_receta_de_torta(self, receta_torta_id, nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total):
        self.conectar()
        nombre = nombre.upper()
        sql = "INSERT INTO recetas_tortas ( receta_torta_id, nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total) VALUES ('%s', '%s', '%s', '%.3f', '%.3f', '%.2f', '%.2f', '%.2f', '%.2f', '%.2f')" % ( receta_torta_id, nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total)
        self.cursor.execute(sql)
        receta = self.cursor.rowcount
        self.desconectar()
        return receta

    def modificar_receta_de_torta(self, nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total, receta_torta_id):
        self.conectar()
        sql = """
                UPDATE recetas
                    SET nombre = '%s',
                        articulo_id = '%s',
                        mezcla = '%.3f',
                        peso_torta = '%.3f',
                        tortas_producidas = '%.2f',
                        costo_torta = '%.2f',
                        bruto = '%.2f',
                        mano_obra = '%.2f',
                        total = '%.2f'
                WHERE receta_torta_id = '%s'
            """ % (nombre, articulo_id, mezcla, peso_torta, tortas_producidas, costo_torta, bruto, mano_obra, total, receta_torta_id)
        self.cursor.execute(sql)
        registro = self.cursor.rowcount
        self.desconectar()
        return registro

    def eliminar_receta__de_torta(self, codigo):
        self.conectar()
        sql = "DELETE FROM recetas_tortas WHERE receta_torta_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_receta_de_torta(self, codigo):
        self.conectar()
        sql = """
            SELECT
                rt.receta_torta_id,
                rt.nombre,
                rt.articulo_id,
                ar.nombre,
                rt.mezcla,
                rt.peso_torta,
                rt.tortas_producidas,
                rt.costo_torta,
                rt.bruto,
                rt.mano_obra,
                rt.total
            FROM
                recetas_tortas rt
            INNER JOIN
                articulos ar
            ON
                rt.articulo_id = ar.articulo_id
            WHERE
                rt.receta_torta_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchone()
        self.desconectar
        return nombre

    def buscar_id_receta_de_torta_para_produccion(self, codigo):
        self.conectar()
        sql = """
            SELECT
                rt.receta_torta_id,
                rt.nombre
            FROM
                recetas_tortas rt
            WHERE
                rt.receta_torta_id = '%s'
        """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchone()
        self.desconectar
        return nombre

    def buscar_nombre_de_receta_de_torta(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """
            SELECT  receta_torta_id,
                    nombre,
            FROM recetas_tortas
            WHERE upper(nombre) LIKE '%s'
        """ % (nombre)
        self.cursor.execute(sql)
        receta = self.cursor.fetchall()
        self.desconectar
        return receta

    def recetas_de_tortas_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT  receta_torta_id,
                        nombre
                FROM recetas_tortas
                ORDER BY receta_torta_id
                """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def agregar_recetas_tortas_detalles(self, receta_torta_id, cantidad, articulo_id, total_neto):
        self.conectar()
        sql = """INSERT INTO recetas_tortas_detalles(receta_torta_id, cantidad, articulo_id, total_neto) VALUES ('%s', '%.3f', '%s', '%.2f' )""" % (receta_torta_id, cantidad, articulo_id, total_neto)
        self.cursor.execute(sql)
        renglones = self.cursor.rowcount
        self.desconectar()
        return renglones
        if renglones:
            info('Registro insertado con éxito')

    def buscar_detalles_id_receta_torta(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    rtd.cantidad,
                    rtd.articulo_id,
                    ar.nombre,
                    ar.costo_actual,
                    ar.unidad,
                    ar.iva_compra,
                    round((ar.iva_compra/100) * rtd.total_neto,2) as monto_iva_compra,
                    rtd.total_neto
                FROM
                    recetas_tortas_detalles rtd
                INNER JOIN
                    articulos ar
                ON
                    rtd.articulo_id = ar.articulo_id
                INNER JOIN
                    recetas_tortas rt
                ON
                    rt.receta_torta_id = rtd.receta_torta_id
                WHERE
                    rt.receta_torta_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles


#~ Modelo para Depositos
    def agregar_deposito(self, codigo, nombre):
        self.conectar()
        sql = "INSERT INTO depositos (deposito_id, nombre) VALUES('%s','%s')" % (codigo, nombre)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_deposito(self, codigo, nombre):
        self.conectar()
        sql = "UPDATE depositos SET nombre = '%s' WHERE deposito_id = '%s'" % (nombre, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_deposito(self, codigo):
        self.conectar()
        sql = "DELETE FROM depositos WHERE deposito_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_deposito(self, codigo):
        self.conectar()
        sql = "SELECT deposito_id, nombre FROM depositos WHERE deposito_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        deposito = self.cursor.fetchall()
        self.desconectar
        return deposito

    def buscar_nombre_deposito(self, nombre):
        self.conectar()
        nombre = nombre.upper()+ '%'
        sql = "SELECT deposito_id, nombre FROM depositos where upper(nombre) LIKE '%s'" % (nombre)
        self.cursor.execute(sql)
        deposito = self.cursor.fetchall()
        self.desconectar
        return deposito

    def depositos_ordenados_por_id(self):
        self.conectar()
        sql = "SELECT deposito_id, nombre FROM depositos ORDER BY deposito_id"
        self.cursor.execute(sql)
        depositos = self.cursor.fetchall()
        self.desconectar()
        return depositos

    #~ Modelo para Grupos
    def agregar_grupo(self, codigo, nombre, foto):
        self.conectar()
        if sys.platform == "win32":
            rfoto = "'%s'" % foto
            rf = rfoto.replace("'", "$$")
            sql = "INSERT INTO grupos (grupo_id, nombre, foto) VALUES('%s','%s',%s)" % (codigo, nombre, rf)
        else:
            sql = "INSERT INTO grupos (grupo_id, nombre, foto) VALUES('%s','%s','%s')" % (codigo, nombre, foto)

        self.cursor.execute(sql)
        self.desconectar()

    def modificar_grupo(self, codigo, nombre, foto):
        self.conectar()
        if sys.platform == "win32":
            rfoto = "'%s'" % foto
            rf = rfoto.replace("'", "$$")
            sql = "UPDATE grupos SET nombre = '%s', foto = %s WHERE grupo_id = '%s'" % (nombre, rf, codigo)
        else:
            sql = "UPDATE grupos SET nombre = '%s', foto = '%s' WHERE grupo_id = '%s'" % (nombre, foto, codigo)

        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_grupo(self, codigo):
        self.conectar()
        sql = "DELETE FROM grupos WHERE grupo_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_grupo(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = "SELECT grupo_id, nombre, foto FROM grupos WHERE upper(grupo_id) = '%s'" % (codigo)
        self.cursor.execute(sql)
        grupo = self.cursor.fetchall()
        self.desconectar
        return grupo

    def buscar_nombre_grupo(self, nombre):
        self.conectar()
        nombre = nombre.upper()+ '%'
        sql = "SELECT grupo_id, nombre, foto FROM grupos WHERE upper(nombre) LIKE '%s'" % (nombre)
        self.cursor.execute(sql)
        grupo = self.cursor.fetchall()
        self.desconectar
        return grupo

    def grupos_ordenados_por_id(self):
        self.conectar()
        sql = "SELECT grupo_id, nombre, foto FROM grupos ORDER BY grupo_id"
        self.cursor.execute(sql)
        grupos = self.cursor.fetchall()
        self.desconectar()
        return grupos

    #Modelo de Venta
    def ventas_ordenadas_por_id(self):
        self.conectar()
        sql = """
            SELECT
                v.venta_id,
                v.emision,
                c.nombre,
                v.procesada
            FROM
                ventas v
            INNER JOIN
                clientes c
            ON
                v.cliente_id = c.cliente_id
            ORDER BY
                v.venta_id"""
        self.cursor.execute(sql)
        ventas = self.cursor.fetchall()
        self.desconectar()
        return ventas

    #~ Modelo para Zonas
    def agregar_zona(self, codigo, nombre):
        self.conectar()
        a = nombre.upper()
        sql = "INSERT INTO zonas( zona_id, nombre) VALUES('%s','%s')" % (codigo, nombre)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_zona(self, codigo, nombre):
        self.conectar()
        a = nombre.upper()
        sql = "UPDATE zonas SET nombre ='%s' WHERE zona_id = '%s'" % (nombre, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_zona(self, codigo):
        self.conectar()
        sql = "DELETE FROM zonas WHERE zona_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_zona(self, codigo):
        self.conectar()
        sql = "SELECT zona_id, nombre FROM zonas WHERE zona_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchall()
        self.desconectar
        return nombre

    def buscar_nombre_zona(self, nombre):
        self.conectar()
        nombre = nombre + '%'
        sql = "SELECT zona_id, nombre FROM zonas WHERE nombre LIKE '%s'" % (nombre)
        self.cursor.execute(sql)
        zonas = self.cursor.fetchall()
        self.desconectar
        return zonas

    def zonas_ordenadas_por_id(self):
        self.conectar()
        sql = "SELECT zona_id, nombre FROM zonas ORDER BY zona_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #~ Modelo para Tipos de Proveedor
    def agregar_tipo_proveedor(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "INSERT INTO proveedores_tipos ( tipo_id, nombre) VALUES( '%s','%s')" % (codigo, tipo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_tipo_proveedor(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "UPDATE proveedores_tipos SET nombre ='%s' WHERE tipo_id = '%s'" % (tipo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_tipo_proveedor(self, codigo):
        self.conectar()
        sql = "DELETE FROM proveedores_tipos WHERE tipo_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_tipo_proveedor(self, codigo):
        self.conectar()
        sql = "SELECT tipo_id, nombre FROM proveedores_tipos WHERE tipo_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def buscar_nombre_tipo_proveedor(self, tipo):
        self.conectar()
        tipo = tipo.upper()+'%'
        sql = "SELECT tipo_id, nombre FROM proveedores_tipos WHERE upper(nombre) LIKE '%s'" % (tipo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def tipos_de_proveedores_ordenados_por_id(self):
        self.conectar()
        sql = "SELECT tipo_id, nombre FROM proveedores_tipos ORDER BY tipo_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #~ Modelo para Tipos de Clientes
    def agregar_tipo_cliente(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "INSERT INTO clientes_tipos ( tipo_cliente_id, nombre) VALUES( '%s','%s')" % (codigo, tipo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_tipo_cliente(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "UPDATE clientes_tipos SET nombre ='%s' WHERE tipo_cliente_id = '%s'" % (tipo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_tipo_cliente(self, codigo):
        self.conectar()
        sql = "DELETE FROM clientes_tipos WHERE tipo_cliente_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_tipo_cliente(self, codigo):
        self.conectar()
        sql = "SELECT tipo_cliente_id, nombre FROM clientes_tipos WHERE tipo_cliente_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def buscar_nombre_tipo_cliente(self, tipo):
        self.conectar()
        tipo = tipo.upper()+'%'
        sql = "SELECT tipo_cliente_id, nombre FROM proveedores_tipos WHERE upper(tipo) LIKE '%s'" % (tipo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def tipos_de_clientes_ordenados_por_id(self):
        self.conectar()
        sql = "SELECT tipo_cliente_id, nombre FROM clientes_tipos ORDER BY tipo_cliente_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #~ Modelo para Tipo de Operaciones
    def agregar_operacion(self, codigo, operacion):
        self.conectar()
        sql = "INSERT INTO tipo_operacion (operacion_id, operacion) VALUES('%s','%s')" % (codigo, operacion)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_operacion(self, codigo, operacion):
        self.conectar()
        sql = "UPDATE tipo_operacion SET operacion = '%s' WHERE operacion_id = '%s'" % (operacion, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_operacion(self, codigo):
        self.conectar()
        sql = "DELETE FROM tipo_operacion WHERE operacion_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_operacion(self, codigo):
        self.conectar()
        sql = "SELECT operacion_id, operacion FROM tipo_operacion WHERE operacion_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        operacion = self.cursor.fetchall()
        self.desconectar
        return operacion

    def buscar_nombre_operacion(self, operacion):
        self.conectar()
        operacion = operacion.upper()+ '%'
        sql = "SELECT operacion_id, operacion FROM tipo_operacion where upper(operacion) LIKE '%s'" % (operacion)
        self.cursor.execute(sql)
        operacion = self.cursor.fetchall()
        self.desconectar
        return operacion

    def operaciones_ordenadas_por_id(self):
        self.conectar()
        sql = "SELECT operacion_id, operacion FROM tipo_operacion ORDER BY operacion_id"
        self.cursor.execute(sql)
        operacion = self.cursor.fetchall()
        self.desconectar()
        return operacion

    # Modelo para Proveedor
    def agregar_proveedor(self, codigo, nombre, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta):
        dias = int(dias)
        self.conectar()
        sql = """Insert into proveedores (proveedor_id, nombre, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta)
        Values('%s','%s','%s','%s','%s','%s','%s', '%s','%s','%s','%s','%s')""" % (codigo, nombre, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_proveedor(self, codigo, nombre, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta):
        dias = int(dias)
        self.conectar()
        sql = """Update proveedores set nombre = '%s',
                                    tipo_id = '%s',
                                    zona_id = '%s',
                                    direccion = '%s',
                                    telefono = '%s',
                                    email = '%s',
                                    dias = '%i',
                                    banco_id = '%s',
                                    titular = '%s',
                                    cuenta = '%s',
                                    tipo_cuenta = '%s'
                    where proveedor_id = '%s'""" % (nombre, tipo_id, zona_id, direccion, telefono, email, dias, banco_id, titular, cuenta, tipo_cuenta, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_proveedor(self, codigo):
        self.conectar()
        sql = "DELETE FROM proveedores WHERE proveedor_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_proveedor(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    WHERE upper(p.proveedor_id) = '%s'""" % (codigo)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def buscar_nombre_proveedor(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    WHERE upper(p.nombre) LIKE '%s'""" % (nombre)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_tipo_proveedor(self, tipo):
        self.conectar()
        tipo = tipo.upper() + '%'
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    WHERE upper(t.nombre) like '%s'""" % (tipo)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def buscar_telefono_proveedor(self, telefono):
        self.conectar()
        telefono = telefono + '%'
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    WHERE p.telefono like '%s'""" % (telefono)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_zona_proveedor(self, zona):
        self.conectar()
        zona = zona + '%'
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    WHERE z.nombre like '%s'""" % (zona)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def buscar_email_proveedor(self, email):
        self.conectar()
        email = email.lower() + '%'
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    WHERE lower(p.email) like '%s'""" % (email)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def proveedores_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT p.proveedor_id,
                        p.nombre,
                        p.tipo_id,
                        t.nombre,
                        p.zona_id,
                        z.nombre,
                        p.direccion,
                        p.telefono,
                        p.email,
                        p.dias,
                        p.banco_id,
                        b.nombre,
                        p.titular,
                        p.cuenta,
                        p.tipo_cuenta
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    left join bancos b
                        on p.banco_id = b.banco_id
                    order by p.proveedor_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def articulos_asociados_a_proveedor(self, proveedor):
        self.conectar()
        sql = """select a.articulo_id,
                        a.nombre,
                        a.costo_actual,
                        a.existencia
                from articulos a
                inner join articulos_proveedores p
                    on p.articulo_id = a.articulo_id
                where p.proveedor_id = '%s'
                order by a.articulo_id
            """ % (proveedor)
        self.cursor.execute(sql)
        lista = self.cursor.fetchall()
        self.desconectar()
        return lista

    #~ Modelo para Tipos de empleados
    def agregar_tipo_empleado(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "INSERT INTO empleados_tipos ( tipo_empleado_id, descripcion) VALUES( '%s','%s')" % (codigo, tipo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_tipo_empleado(self, codigo, tipo):
        self.conectar()
        t = tipo.upper()
        sql = "UPDATE empleados_tipos SET descripcion ='%s' WHERE tipo_empleado_id = '%s'" % (tipo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_tipo_empleado(self, codigo):
        self.conectar()
        sql = "DELETE FROM empleados_tipos WHERE tipo_empleado_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_tipo_empleado(self, codigo):
        self.conectar()
        sql = "SELECT tipo_empleado_id, descripcion FROM empleados_tipos WHERE tipo_empleado_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def buscar_tipo_empleado(self, tipo):
        self.conectar()
        tipo = tipo.upper()+'%'
        sql = "SELECT tipo_empleado_id, descripcion FROM empleados_tipos WHERE upper(descripcion) LIKE '%s'" % (tipo)
        self.cursor.execute(sql)
        tipo = self.cursor.fetchall()
        self.desconectar
        return tipo

    def tipos_de_empleados_ordenados_por_id(self):
        self.conectar()
        sql = "SELECT tipo_empleado_id, descripcion FROM empleados_tipos ORDER BY tipo_empleado_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #~ Modelo para Turnos
    def agregar_turno(self, codigo, inicio, fin, descripcion):
        self.conectar()
        sql = "INSERT INTO turnos ( turno_id, inicio, fin, descripcion) VALUES( '%s','%s', '%s','%s')" % (codigo, inicio, fin, descripcion)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_turno(self, codigo, inicio, fin, descripcion):
        self.conectar()
        sql = """
                UPDATE turnos
                    SET descripcion ='%s',
                        inicio = '%s',
                        fin = '%s'
                WHERE turno_id = '%s'
                """ % (descripcion, inicio, fin, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_turno(self, codigo):
        self.conectar()
        sql = "DELETE FROM turnos WHERE turno_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_turno(self, codigo):
        self.conectar()
        sql = """
                SELECT  turno_id,
                        descripcion,
                        inicio,
                        fin
                FROM turnos
                WHERE turno_id = '%s'
                """ % (codigo)
        self.cursor.execute(sql)
        datos = self.cursor.fetchall()
        self.desconectar
        return datos

    def buscar_nombre_turno(self, descripcion):
        self.conectar()
        descripcion = descripcion.upper()+'%'
        sql = """
                SELECT  turno_id,
                        descripcion,
                        inicio,
                        fin
                FROM turnos
                WHERE upper(descripcion) LIKE '%s'
                """ % (descripcion)
        self.cursor.execute(sql)
        datos = self.cursor.fetchall()
        self.desconectar
        return datos

    def turnos_ordenados_por_id(self):
        self.conectar()
        sql = """
                SELECT  turno_id,
                        descripcion,
                        inicio,
                        fin
                FROM turnos
                ORDER BY turno_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def total_diario_de_articulos_despachados(self, fecha):
        self.conectar()
        sql = """
                select
                    dd.articulo_id,
                    a.nombre,
                    sum(dd.cantidad) as cantidad
                from
                    despacho_detalles dd
                inner join
                    articulos a
                on
                    dd.articulo_id = a.articulo_id
                inner join
                    despachos d
                on
                    dd.despacho_id = d.despacho_id
                where
                    d.emision = '%s'
                group by
                    d.emision, dd.articulo_id, a.nombre
                order by
                    cantidad desc
                """ % fecha
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    # Modelo para empleado
    def agregar_empleado(self, codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona, telefono_fijo, celular, email, tipo, turno, cargo, sueldo, observaciones):
        self.conectar()
        sql = """
                Insert into empleados
                        (empleado_id,
                        nombre,
                        nacionalidad,
                        cedula,
                        nacimiento,
                        ingreso,
                        estado_civil,
                        direccion,
                        zona_id,
                        telefono_fijo,
                        telefono_movil,
                        email,
                        tipo_empleado_id,
                        turno_id,
                        cargo,
                        sueldo,
                        observaciones)
                Values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s','%s','%s','%s','%.2f','%s')
                """ % (codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona, telefono_fijo, celular, email, tipo, turno, cargo, sueldo, observaciones)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_empleado(self, codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona, telefono_fijo, celular, email, tipo, turno, cargo, sueldo, observaciones):
        self.conectar()
        sql = """Update empleados
                    set nombre = '%s',
                        nacionalidad = '%s',
                        cedula = '%s',
                        nacimiento = '%s',
                        ingreso = '%s',
                        estado_civil = '%s',
                        direccion = '%s',
                        zona_id = '%s',
                        telefono_fijo = '%s',
                        telefono_movil = '%s',
                        email = '%s',
                        tipo_empleado_id = '%s',
                        turno_id = '%s',
                        cargo = '%s',
                        sueldo = '%.2f',
                        observaciones = '%s'
                    where empleado_id = '%s'
               """ % (nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona, telefono_fijo, celular, email, tipo, turno, cargo, sueldo, observaciones, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_empleado(self, codigo):
        self.conectar()
        sql = "DELETE FROM empleados WHERE empleado_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_empleado(self, codigo):
        self.conectar()
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE e.empleado_id = '%s'""" % (codigo)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchone()
        self.desconectar
        return vendedor

    def buscar_una_vendedora(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    e.empleado_id,
                    e.nombre
                FROM
                    empleados e
                WHERE
                    e.empleado_id = '%s'""" % (codigo)
        self.cursor.execute(sql)
        vendedora = self.cursor.fetchone()
        self.desconectar
        return vendedora

    def buscar_tipo_para_empleado(self, codigo):
        self.conectar()
        codigo = codigo.upper() + '%'
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE t.descripcion LIKE '%s'""" % (codigo)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_tipo_para_empleado(self, codigo):
        self.conectar()
        codigo = codigo.upper() + '%'
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE t.descripcion LIKE '%s'""" % (codigo)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_un_nombre_de_empleado(self, nombre):
        self.conectar()
        sql = """
                SELECT
                    e.empleado_id
                FROM
                    empleados e
                WHERE
                    e.nombre = '%s'
                """ % (nombre)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchone()
        self.desconectar
        return vendedor

    def buscar_nombre_empleado(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE upper(e.nombre) LIKE '%s'""" % (nombre)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_telefono_fijo_empleado(self, telefono):
        self.conectar()
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN tipo_empleado t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE e.telefono_fijo LIKE '%s'""" % (telefono)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_celular_empleado(self, telefono):
        self.conectar()
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE e.telefono_movil LIKE '%s'""" % (telefono)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_zona_empleado(self, zona):
        self.conectar()
        zona = zona.upper() + '%'
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE z.nombre LIKE '%s'""" % (zona)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_correo_empleado(self, correo):
        self.conectar()
        correo = correo + '%'
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE e.email LIKE '%s'""" % (correo)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def panaderos_ordenados_por_id(self):
        self.conectar()
        sql = """
                SELECT
                    e.nombre
                FROM
                    empleados e
                INNER JOIN
                    empleados_tipos t
                ON
                    e.tipo_empleado_id = t.tipo_empleado_id
                WHERE
                    e.tipo_empleado_id = '03' and e.cargo = 'Panadero'
                ORDER BY
                    e.nombre"""
        self.cursor.execute(sql)
        lista = self.cursor.fetchall()
        self.desconectar
        return lista

    def pasteleros_ordenados_por_id(self):
        self.conectar()
        sql = """
                SELECT
                    e.nombre
                FROM
                    empleados e
                INNER JOIN
                    empleados_tipos t
                ON
                    e.tipo_empleado_id = t.tipo_empleado_id
                WHERE
                    e.tipo_empleado_id = '03' and e.cargo = 'Pastelero'
                ORDER BY
                    e.nombre"""
        self.cursor.execute(sql)
        lista = self.cursor.fetchall()
        self.desconectar
        return lista

    def empleados_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT e.empleado_id,
                        e.nombre,
                        e.nacionalidad,
                        e.cedula,
                        e.nacimiento,
                        e.ingreso,
                        e.estado_civil,
                        e.direccion,
                        e.zona_id,
                        z.nombre,
                        e.telefono_fijo,
                        e.telefono_movil,
                        e.email,
                        e.tipo_empleado_id,
                        t.descripcion,
                        e.turno_id,
                        u.descripcion,
                        e.cargo,
                        e.sueldo,
                        e.observaciones
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    ORDER BY e.empleado_id"""
        self.cursor.execute(sql)
        lista = self.cursor.fetchall()
        self.desconectar
        return lista

    def vendedoras_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT
                    e.empleado_id,
                    e.nombre
                FROM
                    empleados e
                INNER JOIN
                    empleados_tipos t
                ON
                    e.tipo_empleado_id = t.tipo_empleado_id
                WHERE
                    e.tipo_empleado_id = '02'
                ORDER BY
                    e.nombre"""
        self.cursor.execute(sql)
        lista = self.cursor.fetchall()
        self.desconectar
        return lista

    # Modelo para Asistencias
    def agregar_asistencia(self, empleado):
        iguales = self.buscar_dia_asistencia_empleado_con_entrada_y_salida_iguales( date.today(), empleado)
        diferentes = self.buscar_dia_asistencia_empleado_con_entrada_y_salida_distintas( date.today(), empleado)
        if iguales == 0 and diferentes == 0:
            self.agregar_entrada(empleado)
        elif iguales == 1 and diferentes == 0:
            self.agregar_salida(empleado)
        elif iguales == 1 and diferentes != 0:
            self.agregar_salida(empleado)
        elif iguales == 0 and diferentes != 0:
            self.agregar_entrada( empleado)

    def agregar_entrada(self, empleado):
        self.conectar()
        sql = "INSERT INTO asistencias (empleado_id) VALUES ('%s')" % (empleado)
        self.cursor.execute(sql)
        self.desconectar()

    def agregar_salida(self, empleado):
        self.conectar()
        sql = """
                UPDATE asistencias
                    SET salida = DEFAULT
                WHERE dia = current_date AND entrada = salida AND empleado_id = '%s'
                """ % (empleado)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_asistencia(self, codigo):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE a.asistencia_id = '%s'
                """ % (codigo)
        self.cursor.execute(sql)
        dato = self.cursor.fetchall()
        self.desconectar()
        return dato

    def buscar_empleado_asistencia(self, empleado):
        self.conectar()
        empleado = empleado.upper() + '%'
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE upper(e.nombre) LIKE '%s'
                """ % (empleado)
        self.cursor.execute(sql)
        dato = self.cursor.fetchall()
        self.desconectar()
        return dato

    def buscar_dia_asistencia(self, dia):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE a.dia = '%s'
                """ % (dia)
        self.cursor.execute(sql)
        dato = self.cursor.fetchall()
        self.desconectar()
        return dato

    def buscar_dia_asistencia_empleado(self, dia, empleado):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE a.dia = '%s' and a.empleado_id = '%s'
                """ % (dia, empleado)
        self.cursor.execute(sql)
        dato = self.cursor.fetchall()
        self.desconectar()
        return dato

    def buscar_dia_asistencia_empleado_con_entrada_y_salida_distintas(self, dia, empleado):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE a.dia = '%s' and a.empleado_id = '%s' and a.entrada != a.salida
                """ % (dia, empleado)
        self.cursor.execute(sql)
        dato = self.cursor.rowcount
        self.desconectar()
        return dato

    def buscar_dia_asistencia_empleado_con_entrada_y_salida_iguales(self, dia, empleado):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE a.dia = '%s' and a.empleado_id = '%s' and a.entrada = a.salida
                """ % (dia, empleado)
        self.cursor.execute(sql)
        dato = self.cursor.rowcount
        self.desconectar()
        return dato

    def asistencias_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida,
                        age(salida, entrada)
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                order by asistencia_id
            """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #Modelo para horas diarias
    def horas_diarias(self, dia):
        self.conectar()
        sql = """
            SELECT  a.empleado_id,
                    e.nombre,
                    a.dia,
                    sum(age(a.salida, a.entrada))
            FROM asistencias a
            INNER JOIN empleados e
            ON a.empleado_id = e.empleado_id
            WHERE a.dia = '%s'
            GROUP BY a.empleado_id, e.nombre, a.dia
            """ % dia
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado
        self.procesar_horas_diarias(dia)

    def procesar_horas_diarias(self, dia):
        self.conectar()
        sql = "DELETE FROM horas_diarias WHERE dia = '%s'" % (dia)
        self.cursor.execute(sql)
        sql1 = """
            INSERT INTO horas_diarias (empleado_id, dia, tiempo)
            SELECT  a.empleado_id,
                    a.dia,
                    sum(age(a.salida, a.entrada))
            FROM asistencias a
            INNER JOIN empleados e
            ON a.empleado_id = e.empleado_id
            WHERE a.dia = '%s'
            GROUP BY a.empleado_id, a.dia
            """ % (dia)
        self.cursor.execute(sql1)
        self.desconectar()

    def horas_semanales(self, inicio, fin):
        self.conectar()
        sql = """
            SELECT  h.empleado_id,
                    e.nombre,
                    sum(h.tiempo)
            FROM horas_diarias h
            INNER JOIN empleados e
            ON h.empleado_id = e.empleado_id
            WHERE h.dia >='%s' and h.dia <= '%s'
            GROUP BY h.empleado_id, e.nombre
            """ % (inicio, fin)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    # Modelo para Clientes
    def agregar_cliente(self, codigo, nombre, tipo_id, zona_id, direccion, telefono, email):
        self.conectar()
        sql = """Insert into clientes (cliente_id, nombre, tipo_cliente_id, zona_id, direccion, telefono, email)
        Values('%s','%s','%s','%s','%s','%s','%s')""" % (codigo, nombre, tipo_id, zona_id, direccion, telefono, email)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_cliente(self, codigo, nombre, tipo_id, zona_id, direccion, telefono, email):
        self.conectar()
        sql = """Update clientes set nombre = '%s',
                                    tipo_cliente_id = '%s',
                                    zona_id = '%s',
                                    direccion = '%s',
                                    telefono = '%s',
                                    email = '%s'
                    where cliente_id = '%s'""" % (nombre, tipo_id, zona_id, direccion, telefono, email, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_cliente(self, codigo):
        self.conectar()
        sql = "DELETE FROM clientes WHERE cliente_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_cliente(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    WHERE upper(c.cliente_id) = '%s'""" % (codigo)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def buscar_id_cliente_venta(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    WHERE upper(c.cliente_id) LIKE '%s'""" % (codigo)

    def buscar_nombre_cliente(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on p.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    WHERE upper(c.nombre) LIKE '%s'""" % (nombre)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_tipo_cliente(self, tipo):
        self.conectar()
        tipo = tipo.upper() + '%'
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    WHERE upper(t.nombre) like '%s'""" % (tipo)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def buscar_telefono_cliente(self, telefono):
        self.conectar()
        telefono = telefono + '%'
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    WHERE c.telefono like '%s'""" % (telefono)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_zona_cliente(self, zona):
        self.conectar()
        zona = zona + '%'
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    WHERE z.nombre like '%s'""" % (zona)
        self.cursor.execute(sql)
        cliente = self.cursor.fetchall()
        self.desconectar
        return cliente

    def buscar_email_cliente(self, email):
        self.conectar()
        email = email.lower() + '%'
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    WHERE lower(c.email) like '%s'""" % (email)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def clientes_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT c.cliente_id,
                        c.nombre,
                        c.tipo_cliente_id,
                        t.nombre,
                        c.zona_id,
                        z.nombre,
                        c.direccion,
                        c.telefono,
                        c.email
                    FROM clientes c
                    inner join clientes_tipos t
                        on c.tipo_cliente_id = t.tipo_cliente_id
                    inner join zonas z
                        on c.zona_id = z.zona_id
                    order by c.cliente_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    # Modelo para Articulos
    def agregar_articulo(self, articulo_id, nombre, grupo_id, deposito_id, marca, descripcion,
                        unidad, iva_compra, iva_venta, costo_anterior, costo_promedio,
                        costo_actual, utilidad, precio_neto, monto_iva_venta, precio_venta,
                        existencia, existencia_min, existencia_max, usa_existencia,
                        exento_iva, uso_interno, produccion, foto):
        self.conectar()
        sql = """Insert into articulos (articulo_id, nombre, grupo_id, deposito_id, marca,
                                        descripcion, unidad, iva_compra, iva_venta,
                                        costo_anterior, costo_promedio, costo_actual,
                                        utilidad, precio_neto, monto_iva_venta, precio_venta,
                                        existencia, existencia_min, existencia_max,
                                        usa_existencia, exento_iva, uso_interno, produccion, foto)
                    Values('%s', '%s', '%s', '%s','%s',
                            '%s', '%s', '%.2f', %.2f,
                            '%.2f', %.2f, '%.2f',
                            '%.2f', %.2f, '%.2f','%.2f',
                            '%.3f', %.3f, '%.3f',
                            '%s', '%s', '%s', '%s', '%s')""" % (articulo_id, nombre, grupo_id, deposito_id, marca, descripcion, unidad, iva_compra, iva_venta, costo_anterior, costo_promedio, costo_actual, utilidad, precio_neto, monto_iva_venta, precio_venta, existencia, existencia_min, existencia_max, usa_existencia, exento_iva, uso_interno, produccion, foto)

        self.cursor.execute(sql)
        self.desconectar()

    def modificar_articulo(self, articulo_id, nombre, grupo_id, deposito_id, marca, descripcion,
                                        unidad, iva_compra, iva_venta, costo_anterior, costo_promedio,
                                        costo_actual, utilidad, precio_neto, monto_iva_venta, precio_venta,
                                        existencia, existencia_min, existencia_max, usa_existencia,
                                        exento_iva, uso_interno, produccion, foto):
        self.conectar()
        sql = """Update articulos set nombre = '%s',
                            grupo_id = '%s',
                            deposito_id = '%s',
                            marca = '%s',
                            descripcion = '%s',
                            unidad = '%s',
                            iva_compra = '%.2f',
                            iva_venta = '%.2f',
                            costo_anterior = '%.5f',
                            costo_promedio = '%.5f',
                            costo_actual = '%.5f',
                            utilidad = '%.2f',
                            precio_neto = '%.2f',
                            monto_iva_venta = '%.2f',
                            precio_venta = '%.2f',
                            existencia = '%.3f',
                            existencia_min = '%.3f',
                            existencia_max = '%.3f',
                            usa_existencia = '%s',
                            exento_iva = '%s',
                            uso_interno = '%s',
                            produccion = '%s',
                            foto = '%s'
            where articulo_id = '%s'""" % (nombre, grupo_id, deposito_id, marca, descripcion,
                                        unidad, iva_compra, iva_venta, costo_anterior, costo_promedio,
                                        costo_actual, utilidad, precio_neto, monto_iva_venta, precio_venta,
                                        existencia, existencia_min, existencia_max, usa_existencia,
                                        exento_iva, uso_interno, produccion, foto, articulo_id)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_articulo(self, codigo):
        self.conectar()
        sql = "DELETE FROM articulos WHERE articulo_id = '%s'" % (codigo)
        self.cursor.execute(ql)
        self.desconectar()

    def buscar_articulo_compra(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = """SELECT '1',
                        a.articulo_id,
                        a.nombre,
                        a.costo_actual,
                        a.iva_compra,
                        round((a.iva_compra/100) * a.costo_actual,2) as monto_iva_compra,
                        a.costo_actual,
                        a.exento_iva
                    FROM articulos a
                    WHERE a.articulo_id = '%s'""" % (codigo)
        self.cursor.execute(sql)
        articulo = self.cursor.fetchone()
        self.desconectar
        return articulo

    def buscar_articulo_pedido(self, codigo):
        codigo = codigo.upper()
        status = Model().verificar_existencia_simple(codigo,Decimal('1.0'), 'Salida')
        self.conectar()
        if status == 1:
            sql = """SELECT '1',
                            a.articulo_id,
                            a.nombre,
                            a.costo_actual,
                            a.unidad,
                            a.iva_compra,
                            round((a.iva_compra/100) * a.costo_actual,2) as monto_iva_compra,
                            a.costo_actual
                    FROM articulos a
                    inner join depositos d
                            on a.deposito_id = d.deposito_id
                     WHERE upper(a.articulo_id) = '%s'
                    and a.deposito_id = '01'""" % (codigo)
            self.cursor.execute(sql)
            articulo = self.cursor.fetchone()
            self.desconectar
            return articulo

    def buscar_ingrediente(self, codigo):
        codigo = codigo.upper()
        status = Model().verificar_existencia_simple(codigo,Decimal('1.0'), 'Salida')
        self.conectar()
        if status == 1:

            sql = """SELECT '1',
                        a.articulo_id,
                        a.nombre,
                        a.costo_actual,
                        a.iva_compra,
                        round((a.iva_compra/100) * a.costo_actual,2) as monto_iva_compra,
                        a.costo_actual
                    FROM articulos a
                    inner join depositos d
                            on a.deposito_id = d.deposito_id
                     WHERE upper(a.articulo_id) = '%s'
                    and a.deposito_id = '01'""" % (codigo)
            self.cursor.execute(sql)
            articulo = self.cursor.fetchone()
            self.desconectar
            return articulo

    def buscar_articulo_punto_venta(self, codigo):
        self.conectar()
        status = Model().verificar_existencia_simple(codigo,Decimal('1.0'), 'Salida')
        if status == 1:
            sql = """
                    SELECT
                        '1' as cantidad,
                        a.articulo_id,
                        a.nombre,
                        a.iva_venta,
                        round((a.iva_venta/100) * a.precio_venta,2) as monto_iva_venta,
                        a.precio_venta,
                        a.precio_venta
                    FROM
                        articulos a
                    WHERE
                        a.articulo_id = '%s'""" % (codigo)
            self.cursor.execute(sql)
            articulo = self.cursor.fetchone()
            self.desconectar
            return articulo

    def buscar_articulo_venta(self, codigo):
        self.conectar()
        status = Model().verificar_existencia_simple(codigo,Decimal('1.0'), 'Salida')
        if status == 1:
            sql = """
                    SELECT
                        '1' as cantidad,
                        a.articulo_id,
                        a.nombre,
                        a.iva_venta,
                        round((a.iva_venta/100) * a.precio_venta,2) as monto_iva_venta,
                        a.precio_venta,
                        a.precio_venta
                    FROM
                        articulos a
                    WHERE
                        a.articulo_id = '%s'""" % (codigo)
            self.cursor.execute(sql)
            articulo = self.cursor.fetchone()
            self.desconectar
            return articulo

    def buscar_id_articulo(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE upper(a.articulo_id) = '%s'""" % (codigo)
        self.cursor.execute(sql)
        articulo = self.cursor.fetchall()
        self.desconectar
        return articulo

    def buscar_un_articulo(self, codigo):
        self.conectar()
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE articulo_id = '%s'""" % (codigo)
        self.cursor.execute(sql)
        articulo = self.cursor.fetchone()
        self.desconectar
        return articulo

    def buscar_nombre_articulo(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE upper(a.nombre) LIKE '%s'""" % (nombre)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_id_articulo_produccion(self, codigo):
        self.conectar()
        codigo = codigo.upper()
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE upper(a.articulo_id) = '%s' and a.produccion = 'si'""" % (codigo)
        self.cursor.execute(sql)
        articulo = self.cursor.fetchall()
        self.desconectar
        return articulo

    def buscar_nombre_articulo_produccion(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE upper(a.nombre) LIKE '%s' and a.produccion = 'si'""" % (nombre)
        self.cursor.execute(sql)
        articulo = self.cursor.fetchall()
        self.desconectar
        return articulo

    def buscar_deposito_articulo(self, deposito):
        self.conectar()
        deposito = deposito.upper() + '%'
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE upper(d.nombre) like '%s'""" % (deposito)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_grupo_articulo(self, grupo):
        self.conectar()
        grupo = grupo.upper() + '%'
        sql = """a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.produccion,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    WHERE upper(g.nombre) like '%s'""" % (grupo)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

    def articulos_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    order by a.articulo_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def articulos_para_vender_ordenados_por_id(self):
        self.conectar()
        sql = """
                SELECT
                    a.articulo_id,
                    a.nombre,
                    a.existencia,
                    a.precio_venta
                FROM
                    articulos a
                inner join
                    depositos d
                on
                    a.deposito_id = d.deposito_id
                WHERE
                    d.nombre = 'Expendio'
                order by a.articulo_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def inventario_simple(self):
        self.conectar()
        sql = """
                SELECT
                    a.articulo_id,
                    a.nombre,
                    a.existencia,
                    a.costo_actual,
                    round(a.existencia * costo_actual, 2) as total
                FROM
                    articulos a
                ORDER BY
                    a.articulo_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def inventario_valorizado(self):
        self.conectar()
        sql = """
                SELECT
                    a.articulo_id,
                    a.nombre,
                    a.existencia,
                    a.costo_actual,
                    round(a.existencia * costo_actual, 2) as total,
                    '0,00',
                    '0,00',
                    '0,00',
                    '0,00',
                    '0,00',
                    '0,00',
                    '0,00',
                    '0,00',
                    '0,00'
                FROM
                    articulos a
                ORDER BY
                    a.articulo_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def articulos_produccion_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.foto
                    FROM articulos a
                    inner join grupos g
                        on a.grupo_id = g.grupo_id
                    inner join depositos d
                        on a.deposito_id = d.deposito_id
                    where a.produccion = 'si'
                    order by a.articulo_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def solo_materia_prima(self):
        self.conectar()
        sql = """
                SELECT
                        a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva_compra,
                        a.iva_venta,
                        a.costo_anterior,
                        a.costo_promedio,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.monto_iva_venta,
                        a.precio_venta,
                        a.existencia,
                        a.existencia_min,
                        a.existencia_max,
                        a.usa_existencia,
                        a.exento_iva,
                        a.uso_interno,
                        a.foto
                FROM
                        articulos a
                INNER JOIN
                        grupos g
                ON
                        a.grupo_id = g.grupo_id
                INNER JOIN
                        depositos d
                ON
                    a.deposito_id = d.deposito_id
                WHERE
                    a.deposito_id = '01'
                    AND a.uso_interno = 'si'
                ORDER BY
                    a.articulo_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #Modelo para articulos asociados a proveedores
    def agregar_proveedor_a_articulo(self, proveedor, costo, fecha, articulo):
        self.conectar()
        sql = """
                Insert into articulos_proveedores(proveedor_id, costo, fecha, articulo_id) Values ('%s', '%.2f', '%s', '%s')
                 """ % (proveedor, costo, fecha, articulo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_proveedor_a_articulo(self, codigo, proveedor, costo, fecha):
        self.conectar()
        sql = """
                Update articulos_proveedores
                    set proveedor_id = '%s',
                        costo = '%.02f',
                        fecha = '%s'
                where artiprov_id = '%s'
            """ % (proveedor, costo, fecha, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_proveedor_de_articulo(self, proveedor_id, articulo_id):
        self.conectar()
        sql = "delete from articulos_proveedores where proveedor_id = '%s' and articulo_id = '%s'" % (proveedor_id, articulo_id)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_artiprov(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    ap.artiprov_id,
                    ap.proveedor_id,
                    p.nombre,
                    ap.costo,
                    a.existencia,
                    ap.fecha
                FROM
                    articulos_proveedores ap
                INNER JOIN
                    proveedores p
                ON
                    ap.proveedor_id = p.proveedor_id
                INNER JOIN
                    articulos a
                ON
                    a.articulo_id = ap.articulo_id
                WHERE
                    artiprov_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        dato = self.cursor.fetchall()
        self.desconectar()
        return dato

    def buscar_proveedores_asignados(self, codigo):
        self.conectar()
        sql = """Select
                        ap.artiprov_id,
                        ap.proveedor_id,
                        p.nombre,
                        ap.costo,
                        a.existencia,
                        ap.fecha
                from articulos_proveedores ap
                inner join articulos a
                    on a.articulo_id = ap.articulo_id
                inner join proveedores p
                    on ap.proveedor_id = p.proveedor_id
                where ap.articulo_id = '%s'
                order by ap.costo
            """ % (codigo)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    def articulos_proveedores_ordenados_por_id(self):
        self.conectar()
        sql = """
                Select  a.artiprov_id,
                        a.proveedor_id,
                        p.nombre,
                        a.costo,
                        a.fecha,
                        a.articulo_id
                from articulos_proveedores a
                inner join proveedores p
                    on a.proveedor_id = p.proveedor_id
                order by artiprov_id
            """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

    #Modelo para movimientos
    def verificar_existencia_simple(self, articulo_id, cantidad, movimiento):
        self.conectar()
        a = self.buscar_id_articulo(articulo_id)
        self.desconectar()
        articulo = a[0][1]
        existencia = a[0][18]
        existencia_min = a[0][19]
        existencia_max = a[0][20]

        if movimiento == 'Entrada' or movimiento == 'Compra':
            nueva_existencia = existencia + cantidad
            if nueva_existencia <= existencia_max:
                status = 1
            elif nueva_existencia > existencia_max:
                status = 0
        else:
            nueva_existencia = existencia - cantidad
            if nueva_existencia >= 0:
                status = 1
            elif nueva_existencia < 0:
                status = 0
                info("El sistema no acepta existencia negativa, coloque una cantidad menor")
        return status

    def verificar_existencia_detallada(self, codigo, cantidad, movimiento):
        self.conectar()
        a = self.buscar_id_articulo(codigo)
        self.desconectar()
        articulo = a[0][1]
        existencia = a[0][18]
        existencia_min = a[0][19]
        existencia_max = a[0][20]

        if movimiento == 'Entrada' or movimiento == 'Compra':
            nueva_existencia = existencia + cantidad
            if nueva_existencia < existencia_max:
                status = 1
            elif nueva_existencia == existencia_max:
                status = 1
                info("Al aceptar la operación el articulo %s alcanzará su existencia máxima permitida" % articulo)
            elif nueva_existencia > existencia_max:
                status = 0
                info("No se puede sobrepasar el límite de existencias para el articulo %s" % articulo)
        else:
            nueva_existencia = existencia - cantidad
            if nueva_existencia > 0 and nueva_existencia > existencia_min:
                status = 1
            elif nueva_existencia > 0 and nueva_existencia == existencia_min:
                status = 1
                info("Al aceptar la operación el artículo %s estará con la existencia mínima permitida, agregue más existencia" % articulo)
            elif nueva_existencia > 0 and nueva_existencia < existencia_min:
                status = 1
                info("Al aceptar la operación el artículo %s estará por debajo de la existencia mínima permitida, agregue más existencia" % articulo)
            elif nueva_existencia == 0:
                status = 1
                info("Al aceptar la operación el artículo %s tendrá la existencia en cero, urgente agregue existencia" % articulo)
            elif nueva_existencia < 0:
                status = 0
                info("El sistema no acepta existencia negativa, coloque una cantidad menor")
        return status

    def agregar_movimiento(self, fecha, responsable, concepto, tipo_movimiento, operacion_id, documento, tipo_doc):
        self.conectar()
        sql = """
                INSERT INTO movimientos (fecha, responsable, concepto, tipo_movimiento, operacion_id, documento, tipo_doc )
                        VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s') returning mov_id
                """ % (fecha, responsable, concepto, tipo_movimiento, operacion_id, documento, tipo_doc)
        self.cursor.execute(sql)
        oid = self.cursor.fetchone()
        self.desconectar()
        return oid

    def actualizar_movimiento(self, mov_id):
        self.conectar()
        sql = """
            UPDATE movimientos
                SET documento = mov_id
            WHERE mov_id = '%s'""" % (mov_id)
        self.cursor.execute(sql)
        self.desconectar()

    def agregar_movimiento_detalles(self, mov_id, tipo_movimiento, cantidad, articulo_id, costo):
        if tipo_movimiento == 'Entrada':
            status = 1
        else:
            status = self.verificar_existencia_simple(articulo_id, cantidad, tipo_movimiento)
        if status == 1:
            self.conectar()
            sql = """
                INSERT INTO movimientos_detalles (movimiento_id, cantidad, articulo_id, costo )
                        VALUES(%i, %.3f, '%s', %.2f)
                """ % (mov_id,  cantidad, articulo_id, costo)
            self.cursor.execute(sql)
            insertados = self.cursor.rowcount
            self.desconectar()
            self.modificar_existencia(articulo_id, cantidad, tipo_movimiento)
            if costo != 0 or costo != Decimal('0.00') and tipo_movimiento == 'Entrada':
                self.modificar_precio(articulo_id, costo)
            return insertados

    def modificar_existencia(self, codigo, cantidad, tipo_movimiento):
        self.conectar()
        if tipo_movimiento == 'Entrada':
            sql = """UPDATE articulos
                        SET existencia = existencia + '%.3f'
                        WHERE articulo_id = '%s'""" % (cantidad, codigo)
        else:
            sql = """UPDATE articulos
                        SET existencia = existencia - '%.3f'
                        WHERE articulo_id = '%s'""" % (cantidad, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def establecer_costo(self, codigo, costo):
        self.conectar()
        sql = """
                UPDATE articulos
                    SET costo_actual = %.5f
                    WHERE articulo_id = '%s'
            """ % (costo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_precio(self, codigo, nuevo_costo):
        self.conectar()
        p = self.buscar_un_articulo(codigo)
        utilidad = punto_coma(p[14])
        iva_venta = p[10]
        neto = calcular_precio_neto(nuevo_costo, utilidad)
        venta = calcular_precio_venta(iva_venta, nuevo_costo, utilidad)
        monto_iva_venta = coma_punto(calcular_iva_venta(iva_venta, neto, venta))
        precio_neto = coma_punto(neto)
        precio_venta = coma_punto(venta)
        nuevo_costo = coma_punto(nuevo_costo)

        sql = """
                UPDATE articulos
                    SET costo_anterior = costo_actual,
                        costo_actual = '%.2f',
                        precio_neto = '%.2f',
                        precio_venta = '%.2f',
                        monto_iva_venta = '%.2f'
                    WHERE articulo_id = '%s'
            """ % (nuevo_costo, precio_neto, precio_venta, monto_iva_venta, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_movimiento(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    m.mov_id,
                    m.fecha,
                    m.responsable,
                    m.concepto,
                    m.tipo_movimiento,
                    m.operacion_id,
                    o.operacion
                FROM
                    movimientos m
                INNER JOIN
                    tipo_operacion o
                ON
                    o.operacion_id = m.operacion_id
                WHERE
                    m.mov_id = '%i'""" % (codigo)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    def buscar_id_movimiento_detalles(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    md.cantidad,
                    md.articulo_id,
                    a.nombre,
                    md.costo
                FROM
                    movimientos_detalles md
                INNER JOIN
                    movimientos m
                ON
                    md.movimiento_id = m.mov_id
                INNER JOIN
                    articulos a
                ON
                    md.articulo_id = a.articulo_id
                WHERE
                    md.movimiento_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        detalles = self.cursor.fetchall()
        self.desconectar()
        return detalles

    def buscar_tipo_movimiento(self, movimiento):
        self.conectar()
        movimiento = movimiento.upper() + '%'
        sql = """SELECT m.mov_id,
                        m.fecha,
                        m.responsable,
                        m.concepto,
                        m.tipo_movimiento,
                        m.operacion_id,
                        o.operacion,
                        m.articulo_id,
                        a.nombre,
                        m.cantidad,
                        m.costo,
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    WHERE m.tipo_movimiento LIKE '%s'""" % (movimiento)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    def buscar_fecha_movimiento(self, fecha):
        self.conectar()
        sql = """SELECT m.mov_id,
                        m.fecha,
                        m.responsable,
                        m.concepto,
                        m.tipo_movimiento,
                        m.operacion_id,
                        o.operacion,
                        m.articulo_id,
                        a.nombre,
                        m.cantidad,
                        m.costo,
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    WHERE m.fecha = '%s'""" % (fecha)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    def buscar_responsable_movimiento(self, responsable):
        self.conectar()
        responsable = responsable.upper() + '%s'
        sql = """SELECT m.mov_id,
                        m.fecha,
                        m.responsable,
                        m.concepto,
                        m.tipo_movimiento,
                        m.operacion_id,
                        o.operacion,
                        m.articulo_id,
                        a.nombre,
                        m.cantidad,
                        m.costo,
                        m.empleado_id,
                        e.nombre
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    LEFT JOIN empleados e
                        ON m.empleado_id = e.empleado_id
                    WHERE m.responsable LIKE '%s'""" % (responsable)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    def buscar_articulo_para_movimiento(self, codigo):
        self.conectar()
        sql = """
                SELECT
                    '0,00' as cantidad,
                    a.articulo_id,
                    a.nombre,
                    '0,00'
                FROM
                    articulos a
                WHERE
                    a.articulo_id = '%s'""" % (codigo)
        self.cursor.execute(sql)
        listado = self.cursor.fetchone()
        return listado

    def buscar_articulo_movimiento(self, articulo):
        self.conectar()
        articulo = articulo.upper() + '%'
        sql = """SELECT m.mov_id,
                        m.fecha,
                        m.responsable,
                        m.concepto,
                        m.tipo_movimiento,
                        m.operacion_id,
                        o.operacion,
                        m.articulo_id,
                        a.nombre,
                        m.cantidad,
                        m.costo,
                        m.empleado_id,
                        e.nombre
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    LEFT JOIN empleados e
                        ON m.empleado_id = e.empleado_id
                    WHERE upper(a.nombre) LIKE '%s'""" % (articulo)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    def movimientos_ordenados_por_id(self):
        self.conectar()
        sql = """SELECT m.mov_id,
                        m.fecha,
                        m.responsable,
                        m.concepto,
                        m.tipo_movimiento,
                        m.operacion_id,
                        o.operacion
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    ORDER BY m.mov_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

 #~ Modelo para Tarjetas de Debito
    def agregar_tarjeta_de_debito(self, codigo, tarjeta):
        self.conectar()
        sql = "INSERT INTO tarjetas_debito( debito_id, tarjeta) VALUES('%s','%s')" % (codigo, tarjeta)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_tarjeta_de_debito(self, codigo, tarjeta):
        self.conectar()
        sql = "UPDATE tarjetas_debito SET tarjeta ='%s' WHERE debito_id = '%s'" % (tarjeta, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_tarjeta_de_debito(self, codigo):
        self.conectar()
        sql = "DELETE FROM tarjetas_debito WHERE debito_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_tarjeta_de_debito(self, codigo):
        self.conectar()
        sql = "SELECT debito_id, tarjeta FROM tarjetas_debito WHERE debito_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchall()
        self.desconectar
        return nombre

    def buscar_nombre_tarjeta_de_debito(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = "SELECT debito_id, nombre FROM tarjetas_debito WHERE upper(tarjeta) LIKE '%s'" % (nombre)
        self.cursor.execute(sql)
        zonas = self.cursor.fetchall()
        self.desconectar
        return zonas

    def tarjetas_de_debito_ordenadas_por_id(self):
        self.conectar()
        sql = "SELECT debito_id, tarjeta FROM tarjetas_debito ORDER BY debito_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

 #~ Modelo para Tarjetas de Credito
    def agregar_tarjeta_de_credito(self, codigo, tarjeta):
        self.conectar()
        sql = "INSERT INTO tarjetas_credito( credito_id, tarjeta) VALUES('%s','%s')" % (codigo, tarjeta)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_tarjeta_de_credito(self, codigo, tarjeta):
        self.conectar()
        sql = "UPDATE tarjetas_credito SET tarjeta ='%s' WHERE credito_id = '%s'" % (tarjeta, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_tarjeta_de_credito(self, codigo):
        self.conectar()
        sql = "DELETE FROM tarjetas_credito WHERE credito_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_tarjeta_de_credito(self, codigo):
        self.conectar()
        sql = "SELECT credito_id, tarjeta FROM tarjetas_credito WHERE credito_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchall()
        self.desconectar
        return nombre

    def buscar_nombre_tarjeta_de_debito(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = "SELECT credito_id, tarjeta FROM tarjetas_credito WHERE upper(tarjeta) LIKE '%s'" % (nombre)
        self.cursor.execute(sql)
        zonas = self.cursor.fetchall()
        self.desconectar
        return zonas

    def tarjetas_de_credito_ordenadas_por_id(self):
        self.conectar()
        sql = "SELECT credito_id, tarjeta FROM tarjetas_credito ORDER BY credito_id"
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

 #~ Modelo para Bancos
    def agregar_banco(self, codigo, nombre, suspendido):
        self.conectar()
        sql = "INSERT INTO bancos( banco_id, nombre, suspendido) VALUES('%s', '%s', '%s')" % (codigo, nombre, suspendido)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_banco(self, codigo, nombre, suspendido):
        self.conectar()
        sql = """
                UPDATE bancos
                    SET nombre ='%s',
                        suspendido = '%s'
                WHERE banco_id = '%s'
            """ % (nombre, suspendido, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_banco(self, codigo):
        self.conectar()
        sql = "DELETE FROM bancos WHERE banco_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_banco(self, codigo):
        self.conectar()
        sql = """
                SELECT banco_id, nombre, suspendido
                FROM bancos
                WHERE banco_id = '%s'
            """ % (codigo)
        self.cursor.execute(sql)
        nombre = self.cursor.fetchall()
        self.desconectar
        return nombre

    def buscar_nombre_banco(self, nombre):
        self.conectar()
        nombre = nombre.upper() + '%'
        sql = """
                SELECT banco_id, nombre, suspendido
                FROM bancos
                WHERE upper(nombre) LIKE '%s'
            """ % (nombre)
        self.cursor.execute(sql)
        bancos = self.cursor.fetchall()
        self.desconectar
        return bancos

    def buscar_bancos_suspendidos(self):
        self.conectar()
        sql = """
                SELECT banco_id, nombre, suspendido
                FROM bancos
                WHERE suspendido = 'si'
                ORDER BY banco_id
            """
        self.cursor.execute(sql)
        zonas = self.cursor.fetchall()
        self.desconectar
        return zonas

    def bancos_ordenados_por_id(self):
        self.conectar()
        sql = """
                SELECT banco_id, nombre, suspendido
                FROM bancos
                ORDER BY banco_id
            """
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado
