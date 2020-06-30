#Matias Gonzalo Calvo | matiasgonzalocalvo@gmail.com | Efip Julio 2020

from flask import Flask, request, jsonify, json, Response, stream_with_context , g
from flask_restplus import Api, Resource, fields
import yaml
import logging
import requests

from flask_cors import CORS, cross_origin

from sucursales import *
from articulos import *

#jwt keycloack
from flask_oidc import OpenIDConnect

#debug 
logging.basicConfig(level=logging.DEBUG)


flask_app = Flask(__name__)
@property
def specs_url(self):
    return url_for(self.endpoint('specs'), _external=True, _scheme='https')
Api.specs_url = specs_url
app = Api(app = flask_app, version = "1.0", title = "Farma Salud Efip", description = "Apis desarrollada para manejar Farma Salud")



flask_app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'conf/client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'flask-demo',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

oidc = OpenIDConnect(flask_app)
#app.namespace()



sucursales = app.namespace('sucursales', description='Manejar Sucursales')
articulos = app.namespace('articulos', description='Manejar articulos')
inventory = app.namespace('inventory', description='Manejar articulos')
user = app.namespace('user', description='Manejar articulos')
login = app.namespace('login', description='login')
logout = app.namespace('logout', description='login')


#CORS(flask_app)
CORS(flask_app, supports_credentials=True)
with open(r'conf/efip_config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

agregararticulo_model = app.model('Modelo agregar articulo',
                                {
                                    'nombre_del_articulo': fields.String(required = True, description="nombre del articulo", help="no puede estar en blanco",max_length=50), 
                                    'marca_del_articulo': fields.String(required = True, description="marca del articulo", help="no puede estar en blanco",max_length=50),
                                    'precio': fields.Integer(required = True, description="Precio del articulo", help="no puede estar en blanco"),
                                    'barcode': fields.Float(required = True, description="Barcode del articulo", help="no puede estar en blanco",max_length=16,min_length=16),
                                    'descripcion': fields.String(required = True, description="Descripcion del articulo", help="no puede estar en blanco",max_length=100),
                                })

prueba_model = app.model('Modelo Search articulo',
                                {
                                    'all': fields.Boolean(required = False, description="marca del articulo", help="no puede estar en blanco",max_length=50),
                                })

updateinventario_model = app.model('Modelo agregar y eliminar inventario',
                                {
                                    'sucursal_id': fields.Integer(required = True, description="Sucursal", help="no puede estar en blanco",max_length=50), 
                                    'cantidad': fields.Integer(required = True, description="Cantidad de articulos", help="no puede estar en blanco",max_length=50),
                                    'fecha_vencimiento': fields.DateTime(required = True, description="fecha de vencimiento del articulo", help="no puede estar en blanco"),
                                    'barcode': fields.String(required = True, description="Barcode del articulo", help="no puede estar en blanco",max_length=16,min_length=16),
                                })



@login.route("/")
class MainClass(Resource):
    def get(self):
        if oidc.user_loggedin : 
            #Logeado
            print("if")
        else:
            #No logeado
            print("else")
            login_url = "http://localhost:8080/auth/realms/FarmaSalud/protocol/openid-connect/auth?client_id=flask-app&scope=openid+email+profile&access_type=offline&response_type=code&openid.realm=flask-demo&redirect_uri=http://localhost:9080/success"
            articulos.abort(401, status = "Could not save information" , statusCode = "401", url_login = login_url)
        #return '{"url" : "http:"}'
        #oidc.redirect_to_auth_server

@flask_app.route('/success/<path:url_callback>')
@oidc.require_login
def login_web(url_callback):
    return '<script>window.location.assign("http://' + url_callback +'")</script>'

@flask_app.route('/logout/<path:url_callback>')
@oidc.require_login
def logout_web  (url_callback):
    try:
        logging.warning("antes de logout")
        oidc.logout()
        logging.warning("despues de logout")
        logout_url = 'http://localhost:8080/auth/realms/FarmaSalud/protocol/openid-connect/logout?redirect_uri=http://' + url_callback 
    except KeyError as e:
        sucursales.abort(500, e.__doc__, status = "Hubo un error en el server" + str(e), statusCode = "500")
    except Exception as e:
        articulos.abort(400, e.__doc__, status = "No pude borrar la session" + str(e), statusCode = "400")
    else:
        return '<script>window.location.assign("' + logout_url +'")</script>'


@sucursales.route("/")
class MainClass(Resource):
    @oidc.require_login
    @sucursales.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' },)
    def get(self):
        info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])
        username = info.get('preferred_username')
        email = info.get('email')
        user_id = info.get('sub')
        print (username,user_id,email)
        try:
            sucu_abm = sucursales_abm()
            out = sucu_abm.get_sucursales()
        except KeyError as e:
            sucursales.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            articulos.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")
        else:
            return json.dumps(out)

@inventory.route("/<string:search>")
class MainClass(Resource):
    @oidc.require_login
    @inventory.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' },)
    def get(self, search):
        try:
            logging.warning(search)
            art_abm = articulos_abm()
            out = art_abm.get_inventory(search)
        except KeyError as e:
            articulos.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            logging.warning(e)
            articulos.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")
            #articulos.response
        else:
            logging.warning(json.dumps(out))
            return json.dumps(out)

@inventory.route("/agregarinventario")
class MainClass(Resource):
    @oidc.require_login
    @articulos.expect(updateinventario_model,validate=True)
    @inventory.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' },)
    def post(self):
        try:
            content = request.get_json()
            logging.warning(content)
            art_abm = articulos_abm()
            #{'sucursal_id': 1, 'cantidad': 10, 'fecha_vencimiento': '2020-07-04', 'barcode': '8888888888888887'}
            #logging.info(content["sucursal_id"],content["cantidad"],content["fecha_vencimiento"],content["barcode"])
            art_abm.add_inventario(content["sucursal_id"],content["cantidad"],content["fecha_vencimiento"],content["barcode"])
            #art_abm.add_inventorio(content["sucursal_id"],content["cantidad"],content["fecha_vencimiento"],content["barcode"])
        except KeyError as e:
            articulos.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            articulos.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")
            articulos.response
        else:
            x =  '{ "status": "ok", "statusCode":200, "message":"ok"}'
            logging.warning(json.dumps(x))
            return json.loads(x)

@inventory.route("/eliminarinventario")
class MainClass(Resource):
    @oidc.require_login
    @articulos.expect(updateinventario_model,validate=True)
    @inventory.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' },)
    def post(self):
        try:
            content = request.get_json()
            logging.warning(content)
            art_abm = articulos_abm()
            art_abm.del_inventario(content["sucursal_id"],content["cantidad"],content["fecha_vencimiento"],content["barcode"])
        except KeyError as e:
            articulos.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            articulos.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")

        else:
            x =  '{ "status": "ok", "statusCode":200, "message":"ok"}'
            logging.warning(json.dumps(x))
            return json.loads(x)



@articulos.route("/agregararticulo")
class MainClass(Resource):
    @oidc.require_login
    @articulos.expect(agregararticulo_model,validate=True)
    @articulos.doc(responses={ 200: 'OK', 400: 'Argumento no valido', 500: 'Error procesando la solicitud' },)
    #@app.expect(agregararticulo_model,validate=True)	
    def post(self):
        try:
            content = request.get_json()
            art_abm = articulos_abm() 
            art_abm.add_articulos(content["barcode"],content["nombre_del_articulo"],content["precio"],content["descripcion"],content["marca_del_articulo"])
            #return json.loads(articulos.response(200, app.__doc__, status = "status ok", statusCode = "200") )
        except KeyError as e:
            articulos.abort(500, e.__doc__, status = "CRITICAL no agregue el articulo : " + str(e), statusCode = "500")
        except Exception as e:
            articulos.abort(400, e.__doc__, status = "CRITICAL no agregue el articulo : " + str(e), statusCode = "400")
        else:
            x =  '{ "status": "ok", "statusCode":200, "message":"ok"}'
            return json.loads(x)
    def options(self):
        x = '{"options": "options"}'
        return json.loads(x)


@articulos.route("/<string:search>")
class MainClass(Resource):
    @oidc.require_login
    #@app.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' },)
    def get(self, search):
        try:
            logging.warning(search)
            art_abm = articulos_abm()
            out = art_abm.get_articulos(search)
        except KeyError as e:
            articulos.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            logging.warning(Exception)
            articulos.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")
            articulos.response
        else:
            return json.dumps(out)

@user.route("/")
class MainClass(Resource):
    @oidc.require_login
    def get(self):
        try:
            #logging.warning("todos los datos de user")
            #logging.warning(oidc.user_getinfo())
            #logging.warning(oidc.user_getfield('sub')) 
            info = oidc.user_getinfo(['preferred_username', 'email', 'sub'])
            #user_info = oidc.user_getinfo(["name", "nickname", "sub", "email", "zoneinfo", "cla", "groups",])
            #logging.warning("user_info")
            #logging.warning(user_info)
            #logging.warning(user_info.get('groups'))
            #logging.warning(oidc.user_getfield('cla'))
            username = info.get('preferred_username')
            email = info.get('email')
            user_id = info.get('sub')
            #logging.warning(oidc.user_getfield())
            #logging.warning(info.get('prueba'))
            x = '{"username" : "' + username + '", "email" : "' + email + '", "sub" : "' + user_id + '"}'
            return json.loads(x)
        except KeyError as e:
            articulos.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            articulos.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")
            articulos.response
        else:
            return json.dumps(out)
        
        


if __name__ == '__main__':
    #app.secret_key = os.urandom(12)
    print(config['host']['host'],config['host']['port'])
    flask_app.run(debug=True,host=config['host']['host'],port=config['host']['port'])