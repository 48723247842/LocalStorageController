from sanic import Blueprint
from sanic.response import json as json_result
from sanic import response

import json
import time
import redis

from usb_storage import USBStorage

def redis_connect():
	try:
		redis_connection = redis.StrictRedis(
			host="127.0.0.1" ,
			port="6379" ,
			db=1 ,
			#password=ConfigDataBase.self[ 'redis' ][ 'password' ]
			)
		return redis_connection
	except Exception as e:
		return False

def get_usb_config_from_redis():
	try:
		redis_connection = redis_connect()
		config = redis_connection.get( "CONFIG.LOCAL_STORAGE_CONTROLLER_SERVER" )
		config = json.loads( config )
		usb_config = config["usb"]
		return usb_config
	except Exception as e:
		print( e )
		return False

usb_blueprint = Blueprint( 'usb_blueprint' , url_prefix='/usb' )

@usb_blueprint.route( '/' )
def commands_root( request ):
	return response.text( "you are at the /usb url\n" )

@usb_blueprint.route( "/library/rebuild/all" , methods=[ "GET" ] )
def status( request ):
	result = { "message": "failed" }
	try:
		usb_config = get_usb_config_from_redis()
		usb_storage = USBStorage( usb_config )
		usb_storage.rebuild_library()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )