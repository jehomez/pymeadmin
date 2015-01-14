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
from comunes import calcular_precio_neto, calcular_precio_venta, calcular_iva_venta, coma_punto, punto_coma
import sys


class Model:

    def conectar(self):
        self.cnn = connect("dbname='admin0' user='postgres' password='root' host='169.254.196.48' port='5432'");
        self.cursor = self.cnn.cursor()

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


    #~ Modelo para Empresas
    def agregar_empresa(self, codigo, rif, empresa, direccion, telefonos, fax, email, web, contacto):
        self.conectar()
        empresa = empresa.upper()
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
        empresa = empresa + '%'
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
            WHERE empresa LIKE '%s'
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
        codigo = codigo.upper()
        sql = "SELECT deposito_id, nombre FROM depositos WHERE upper(deposito_id) = '%s'" % (codigo)
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

    def buscar_tipo_proveedor(self, tipo):
        self.conectar()
        tipo = tipo.upper()+'%'
        sql = "SELECT tipo_id, nombre FROM proveedores_tipos WHERE upper(tipo) LIKE '%s'" % (tipo)
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

    def buscar_tipo_cliente(self, tipo):
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
    def agregar_proveedor(self, codigo, nombre, tipo_id, zona_id, direccion, telefono, email):
        self.conectar()
        sql = """Insert into proveedores (proveedor_id, nombre, tipo_id, zona_id, direccion, telefono, email)
        Values('%s','%s','%s','%s','%s','%s','%s')""" % (codigo, nombre, tipo_id, zona_id, direccion, telefono, email)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_proveedor(self, codigo, nombre, tipo_id, zona_id, direccion, telefono, email):
        self.conectar()
        sql = """Update proveedores set nombre = '%s',
                                    tipo_id = '%s',
                                    zona_id = '%s',
                                    direccion = '%s',
                                    telefono = '%s',
                                    email = '%s'
                    where proveedor_id = '%s'""" % (nombre, tipo_id, zona_id, direccion, telefono, email, codigo)
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
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
                        p.email
                    FROM proveedores p
                    inner join proveedores_tipos t
                        on p.tipo_id = t.tipo_id
                    inner join zonas z
                        on p.zona_id = z.zona_id
                    order by p.proveedor_id"""
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        self.desconectar()
        return listado

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

    # Modelo para empleado
    def agregar_empleado(self, codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona_id, telefono, celular, email, tipo, turno, cargo, sueldo):
        self.conectar()
        sql = """
                Insert into empleados
                        (empleado_id,
                        nombre,
                        nacionalidad,
                        cedula,
                        nacimiento
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
                        saldo,
                        observaciones)
                Values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s','%s','%s','%s','%s','%.2f')
                """ % (codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona_id, telefono, celular, email, tipo, turno, cargo, sueldo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_empleado(self, codigo, nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona_id, telefono, celular, email, tipo, turno, cargo, sueldo):
        self.conectar()
        sql = """Update empleados
                    set nombre = '%s',
                        nacionalidad = '%s',
                        cedula = '%s',
                        nacimiento = '%s'
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
                        saldo = '%.2f',
                        observaciones = '%s'
                    where empleado_id = '%s'
               """ % (nombre, nacionalidad, cedula, nacimiento, ingreso, estado_civil, direccion, zona_id, telefono, celular, email, tipo, turno, cargo, sueldo, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_empleado(self, codigo):
        self.conectar()
        sql = "DELETE FROM empleados WHERE empleado_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_empleado(self, codigo):
        self.conectar()
        codigo = codigo.upper()
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
                        e.sueldo
                    FROM empleados e
                    INNER JOIN zonas z
                        on e.zona_id = z.zona_id
                    INNER JOIN empleados_tipos t
                        on e.tipo_empleado_id = t.tipo_empleado_id
                    INNER JOIN turnos u
                        on e.turno_id = u.turno_id
                    WHERE e.empleado_id = '%s'""" % (codigo)
        self.cursor.execute(sql)
        vendedor = self.cursor.fetchall()
        self.desconectar
        return vendedor

    def buscar_id_para_empleado(self, codigo):
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
                    WHERE e.empleado_id LIKE '%s'""" % (codigo)
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
                        a.salida
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
                        a.salida
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE e.nombre LIKE '%s'
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
                        a.salida
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
                        a.salida
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
                        a.salida
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
                        a.salida
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                WHERE a.dia = '%s' and a.empleado_id = '%s' and a.entrada = a.salida
                """ % (dia, empleado)
        self.cursor.execute(sql)
        dato = self.cursor.rowcount
        self.desconectar()
        return dato

    def calcular_horas(self, codigo):
        self.conectar()
        sql = """
                SELECT age(salida, entrada)
                FROM asistencias
                WHERE asistencia_id = %i
            """
        self.cursor.execute(sql)
        horas = self.cursor.fetchone()
        self.desconectar()
        return horas

    def asistencias_ordenadas_por_id(self):
        self.conectar()
        sql = """
                SELECT a.asistencia_id,
                        e.nombre,
                        a.entrada,
                        a.salida
                FROM asistencias a
                inner join empleados e
                    on a.empleado_id = e.empleado_id
                order by asistencia_id
            """
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
                    WHERE upper(p.cliente_id) = '%s'""" % (codigo)
        self.cursor.execute(sql)
        proveedor = self.cursor.fetchall()
        self.desconectar
        return proveedor

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
    def agregar_articulo(self, articulo_id, nombre, grupo_id, deposito_id, marca,
                                        descripcion, unidad, iva,
                                        costo_anterior, costo_actual, utilidad,
                                        precio_neto, iva_venta,precio_venta,
                                        existencia, existencia_min, existencia_max,
                                        usa_existencia, exento_iva,uso_interno, foto):
        self.conectar()
        if sys.platform == "win32":
            rfoto = "'%s'" % foto
            rf = rfoto.replace("'", "$$")
            sql = """Insert into articulos (articulo_id, nombre, grupo_id, deposito_id, marca,
                                        descripcion, unidad, iva,
                                        costo_anterior, costo_actual, utilidad,
                                        precio_neto, iva_venta, precio_venta,
                                        existencia, existencia_min, existencia_max,
                                        usa_existencia, exento_iva, uso_interno,foto)
                    Values('%s','%s',
                            '%s','%s','%s',
                            '%s','%s','%.2f',
                            '%.2f','%.2f', '%.2f',
                            '%.2f', '%.2f','%.2f',
                            '%.3f', '%.3f', '%.3f',
                            '%s', '%s','%s', %s)""" % (articulo_id, nombre,
                                            grupo_id, deposito_id, marca,
                                            descripcion, unidad, iva,
                                            costo_anterior, costo_actual, utilidad,
                                            precio_neto, iva_venta,precio_venta,
                                            existencia, existencia_min, existencia_max,
                                            usa_existencia, exento_iva, uso_interno, rf)
        else:
            sql = """Insert into articulos (articulo_id, nombre,
                                        grupo_id, deposito_id, marca,
                                        descripcion, unidad, iva,
                                        costo_anterior, costo_actual, utilidad,
                                        precio_neto, iva_venta, precio_venta,
                                        existencia, existencia_min, existencia_max,
                                        usa_existencia, exento_iva, uso_interno,foto)
                    Values('%s','%s',
                            '%s','%s','%s',
                            '%s','%s','%.2f',
                            '%.2f','%.2f', '%.2f',
                            '%.2f', '%.2f','%.2f',
                            '%.3f', '%.3f', '%.3f',
                            '%s', '%s','%s', '%s')""" % (articulo_id, nombre,
                                            grupo_id, deposito_id, marca,
                                            descripcion, unidad, iva,
                                            costo_anterior, costo_actual, utilidad,
                                            precio_neto, iva_venta,precio_venta,
                                            existencia, existencia_min, existencia_max,
                                            usa_existencia, exento_iva, uso_interno, foto)

        self.cursor.execute(sql)
        self.desconectar()

    def modificar_articulo(self,articulo_id, nombre,
                                        grupo_id, deposito_id, marca,
                                        descripcion, unidad, iva,
                                        costo_anterior, costo_actual, utilidad,
                                        precio_neto, iva_venta,precio_venta,
                                        existencia_min, existencia_max,
                                        usa_existencia, exento_iva,uso_interno, foto):
        self.conectar()
        if sys.platform == "win32":
            rfoto = "'%s'" % foto
            rf = rfoto.replace("'", "$$")
            sql = """Update articulos set nombre = '%s',
                                        grupo_id = '%s',
                                        deposito_id = '%s',
                                        marca = '%s',
                                        descripcion = '%s',
                                        unidad = '%s',
                                        iva = '%.2f',
                                        costo_anterior = '%.2f',
                                        costo_actual = '%.2f',
                                        utilidad = '%2f',
                                        precio_neto = '%.2f',
                                        iva_venta = '%.2f',
                                        precio_venta = '%.2f',
                                        existencia_min = '%.3f',
                                        existencia_max = '%.3f',
                                        usa_existencia = '%s',
                                        exento_iva = '%s',
                                        uso_interno = '%s',
                                        foto = %s
                        where articulo_id = '%s'""" % (nombre,
                                            grupo_id, deposito_id, marca,
                                            descripcion, unidad, iva,
                                            costo_anterior, costo_actual, utilidad,
                                            precio_neto, iva_venta,precio_venta,
                                            existencia_min, existencia_max,
                                            usa_existencia, exento_iva,uso_interno, rf, articulo_id)
        else:
            sql = """Update articulos set nombre = '%s',
                            grupo_id = '%s',
                            deposito_id = '%s',
                            marca = '%s',
                            descripcion = '%s',
                            unidad = '%s',
                            iva = '%.2f',
                            costo_anterior = '%.2f',
                            costo_actual = '%.2f',
                            utilidad = '%2f',
                            precio_neto = '%.2f',
                            iva_venta = '%.2f',
                            precio_venta = '%.2f',
                            existencia_min = '%.3f',
                            existencia_max = '%.3f',
                            usa_existencia = '%s',
                            exento_iva = '%s',
                            uso_interno = '%s',
                            foto = '%s'
            where articulo_id = '%s'""" % (nombre,
                                grupo_id, deposito_id, marca,
                                descripcion, unidad, iva,
                                costo_anterior, costo_actual, utilidad,
                                precio_neto, iva_venta,precio_venta,
                                existencia_min, existencia_max,
                                usa_existencia, exento_iva,uso_interno, foto, articulo_id)
        self.cursor.execute(sql)
        self.desconectar()

    def eliminar_articulo(self, codigo):
        self.conectar()
        sql = "DELETE FROM articulos WHERE articulo_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

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
                        a.iva,
                        a.costo_anterior,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.iva_venta,
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
                    WHERE upper(a.articulo_id) = '%s'""" % (codigo)
        self.cursor.execute(sql)
        articulo = self.cursor.fetchall()
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
                        a.iva,
                        a.costo_anterior,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.iva_venta,
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
                    WHERE upper(a.nombre) LIKE '%s'""" % (nombre)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

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
                        a.iva,
                        a.costo_anterior,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.iva_venta,
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
                    WHERE upper(d.nombre) like '%s'""" % (deposito)
        self.cursor.execute(sql)
        poliza = self.cursor.fetchall()
        self.desconectar
        return poliza

    def buscar_grupo_articulo(self, grupo):
        self.conectar()
        grupo = grupo.upper() + '%'
        sql = """SELECT a.articulo_id,
                        a.nombre,
                        a.grupo_id,
                        g.nombre,
                        a.deposito_id,
                        d.nombre,
                        a.marca,
                        a.descripcion,
                        a.unidad,
                        a.iva,
                        a.costo_anterior,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.iva_venta,
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
                        a.iva,
                        a.costo_anterior,
                        a.costo_actual,
                        a.utilidad,
                        a.precio_neto,
                        a.iva_venta,
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

    #Modelo para articulos_proveedores
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

    def eliminar_proveedor_de_articulo(self, codigo):
        self.conectar()
        sql = "delete from articulos_proveedores where artiprov_id = '%s'" % (codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_artiprov(self, codigo):
        self.conectar()
        sql = """
                Select artiprov_id, proveedor_id, costo, fecha
                from articulos_proveedores
                where artiprov_id = '%s'
            """ % codigo
        self.cursor.execute(sql)
        dato = self.cursor.fetchall()
        self.desconectar()
        return dato

    def buscar_proveedores_asignados(self, codigo):
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
                where articulo_id = '%s'
                order by artiprov_id
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
    def verificar_existencia(self, codigo, cantidad, movimiento):
        self.conectar()
        a = self.buscar_id_articulo(codigo)
        self.desconectar()
        articulo = a[0][1]
        existencia = a[0][16]
        existencia_min = a[0][17]
        existencia_max = a[0][18]

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
                info("El artículo %s no posee existencia" % articulo)
        return status

    def agregar_movimiento(self, fecha, responsable, concepto, tipo_movimiento, operacion_id, articulo_id,
    cantidad, costo):
        status = self.verificar_existencia(articulo_id, cantidad, tipo_movimiento)
        if status == 1:
            self.conectar()
            sql = """
                INSERT INTO movimientos (fecha, responsable,
                                        concepto, tipo_movimiento,
                                        operacion_id, articulo_id,
                                        cantidad, costo)
                        VALUES('%s', '%s',
                               '%s', '%s',
                               '%s', '%s',
                               '%.3f', '%.2f')
                """ % (fecha, responsable, concepto, tipo_movimiento, operacion_id, articulo_id, cantidad, costo)
            self.cursor.execute(sql)
            self.desconectar()
            self.modificar_existencia(articulo_id, cantidad, tipo_movimiento)
            if (costo != Decimal('0.00') or costo != Decimal('0.000')) and tipo_movimiento == 'Entrada':
                self.modificar_precio(articulo_id, costo)

    def modificar_existencia(self, codigo, cantidad, tipo_movimiento):
        self.conectar()
        if tipo_movimiento == 'Entrada' or tipo_movimiento == 'Compra':
            sql = """UPDATE articulos
                        SET existencia = existencia + '%.3f'
                        WHERE articulo_id = '%s'""" % (cantidad, codigo)
        else:
            sql = """UPDATE articulos
                        SET existencia = existencia - '%.3f'
                        WHERE articulo_id = '%s'""" % (cantidad, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def modificar_precio(self,codigo,nuevo_costo):
        self.conectar()
        p = self.buscar_id_articulo(codigo)
        utilidad = punto_coma(p[0][14])
        iva = punto_coma(p[0][11])
        neto = calcular_precio_neto(nuevo_costo, utilidad)
        venta = calcular_precio_venta(iva, nuevo_costo, utilidad)
        iva_venta = coma_punto(calcular_iva_venta(iva, neto, venta))
        precio_neto = coma_punto(neto)
        precio_venta = coma_punto(venta)
        nuevo_costo = coma_punto(nuevo_costo)

        sql = """
                UPDATE articulos
                    SET costo_anterior = costo_actual,
                        costo_actual = '%.2f',
                        precio_neto = '%.2f',
                        precio_venta = '%.2f',
                        iva_venta = '%.2f'
                    WHERE articulo_id = '%s'
            """ % (nuevo_costo, precio_neto, precio_venta, iva_venta, codigo)
        self.cursor.execute(sql)
        self.desconectar()

    def buscar_id_movimiento(self, codigo):
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
                        m.costo
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    WHERE m.mov_id = '%i'""" % (codigo)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

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
                        m.costo
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
                        m.costo
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
                        m.costo
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    WHERE m.responsable LIKE '%s'""" % (responsable)
        self.cursor.execute(sql)
        listado = self.cursor.fetchall()
        return listado

    def buscar_articulo_movimiento(self, articulo_id):
        self.conectar()
        articulo_id = articulo_id.upper() + '%'
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
                        m.costo
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
                    WHERE m.articulo_id LIKE '%s'""" % (articulo_id)
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
                        o.operacion,
                        m.articulo_id,
                        a.nombre,
                        m.cantidad,
                        m.costo
                    FROM movimientos m
                    INNER JOIN tipo_operacion o
                        ON o.operacion_id = m.operacion_id
                    INNER JOIN articulos a
                        ON a.articulo_id = m.articulo_id
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
        nombre = nombre + '%'
        sql = """
                SELECT banco_id, nombre, suspendido
                FROM bancos
                WHERE upper(nombre) = '%s'
            """ % (nombre)
        self.cursor.execute(sql)
        zonas = self.cursor.fetchall()
        self.desconectar
        return zonas

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
