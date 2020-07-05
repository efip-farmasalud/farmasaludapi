#Matias Gonzalo Calvo Efip 2020
import logging
from consulta_db_efip import *
import json
import datetime



class articulos_abm():
    """ Clase Devuelve lista productos """
    def __init__(self):
        """ Constructor """
        logging.info("constructor articulos abm")
        fecha = datetime.datetime.now()
        self.fecha_hoy = fecha.strftime("%Y-%m-%d")
        logging.info("fecha hoy : " + self.fecha_hoy)

    def get_inventory(self, search):
        logging.warning("get_inventory")
        """ Lista los articulos que coincidan con search """
        sql = "SELECT articulo.idproduct, articulo.barcode, articulo.nombre, articulo.precio, articulo.descripcion, articulo.marca, IFNULL(DATE_FORMAT(inventario.fecha_venc , '%d/%m/%Y'),'-') AS fecha_venc , IFNULL(inventario.sucursales_id,'-') as sucursales_id, IFNULL(FORMAT(SUM(inventario.cantidad),0),'-') cantidad , IFNULL(sucursales.nombre,'-') as sucursal_nombre FROM efip.articulo LEFT JOIN efip.inventario ON inventario.barcode  = articulo.barcode LEFT JOIN efip.sucursales ON inventario.sucursales_id = sucursales.id WHERE  articulo.barcode  LIKE '%" + search + "%' OR articulo.nombre LIKE '%" + search + "%' GROUP BY IFNULL(fecha_venc,'-'),IFNULL(sucursales_id,'-'),nombre ORDER BY STR_TO_DATE(sucursales_id,'%d-%m-%Y') DESC"
        logging.warning(sql)
        articulos_get = mariadb_efip()
        #yaml_sql = yaml_config['sql']['sql_get_sucursales']
        salida = articulos_get.select_mariadb(sql)
        #return articulos_get.select_mariadb(sql)
        logging.info("muestro salida")
        logging.info(salida)
        return salida
    
    def add_articulos(self,barcode,nombre,precio,descripcion,marca):
        """ Agregar un nuevo articulo """
        logging.warning("add_articulos")
        logging.warning(barcode)
        logging.warning(str(barcode))
        sql = "INSERT INTO articulo (barcode, nombre, precio, descripcion, marca ) VALUES('" + str(barcode) + "','" + nombre + "','" + str(precio) + "','" + descripcion + "','" + marca + "');"
        try:
            articulos_get = mariadb_efip()
            articulos_get.insert_mariadb(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))

    def get_articulos(self, search):
        """ Lista los articulos que coincidan con search """
        logging.warning("get_articulos")
        sql = "SELECT articulo.idproduct, articulo.barcode, articulo.nombre, articulo.precio, articulo.descripcion, articulo.marca FROM efip.articulo WHERE articulo.nombre LIKE '%" + search + "%'" 
        logging.warning(sql)
        articulos_get = mariadb_efip()
        #yaml_sql = yaml_config['sql']['sql_get_sucursales']
        salida = articulos_get.select_mariadb(sql)
        #return articulos_get.select_mariadb(sql)
        return salida
    
    def add_inventario(self,sucursal,cantidad,fecha_vencimiento,barcode):
        """ Agregar un nuevo inventario a articulo """
        sql = "call add_inventario('" + str(fecha_vencimiento) + "','" + str(barcode) + "','" + str(sucursal) + "','" + str(cantidad) + "')"
        logging.info(sql)
        try:
            add_inventario = mariadb_efip()
            add_inventario.insert_mariadb(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))

    def del_inventario(self,sucursal,cantidad,fecha_vencimiento,barcode):
        """ Agregar un nuevo inventario a articulo """
        #sql = "call add_inventario('" + str(fecha_vencimiento) + "','" + str(self.fecha_hoy) + "','" + str(barcode) + "','" + str(sucursal) + "','" + str(cantidad) + "')"
        sql = "UPDATE inventario SET cantidad=cantidad-" + str(cantidad) + " WHERE barcode='" + str(barcode) + "' AND fecha_venc='" + str(fecha_vencimiento) + "' AND sucursales_id = " + str(sucursal) + " "
        logging.info(sql)
        try:
            add_inventario = mariadb_efip()
            add_inventario.update_mariadb(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))