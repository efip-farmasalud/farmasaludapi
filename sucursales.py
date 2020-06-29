#Matias Gonzalo Calvo Efip 2020
import logging
from consulta_db_efip import *

with open(r'conf/efip_config.yaml') as file:
    yaml_config = yaml.load(file, Loader=yaml.FullLoader)

class sucursales_abm():
    """ Clase Devuelve lista sucursales """
    def get_sucursales(self):
        try:
            sucu = mariadb_efip()
            return sucu.select_mariadb(yaml_config['sql']['sql_get_sucursales'])
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))