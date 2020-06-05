from sanic import Blueprint
from sanic.response import json as json_result
from sanic import response

import json
import time
import redis

from vlc_controller import VLCController

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

def get_vlc_config_from_redis():
	try:
		redis_connection = redis_connect()
		config = redis_connection.get( "CONFIG.LOCAL_STORAGE_CONTROLLER_SERVER" )
		config = json.loads( config )
		vlc_config = config["vlc"]
		return vlc_config
	except Exception as e:
		print( e )
		return False

tv_blueprint = Blueprint( 'tv' , url_prefix='/tv' )

@tv_blueprint.route( '/' )
def commands_root( request ):
	return response.text( "you are at the localstorage:11301/api/tv url\n" )

@tv_blueprint.route( "/pause" , methods=[ "GET" ] )
def pause( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.pause()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@tv_blueprint.route( "/resume" , methods=[ "GET" ] )
def resume( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.play()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@tv_blueprint.route( "/play" , methods=[ "GET" ] )
def play( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		file_path = request.args.get( "file_path" )
		vlc.add( file_path )
		time.sleep( 1 )
		vlc.fullscreen_on()
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@tv_blueprint.route( "/stop" , methods=[ "GET" ] )
def stop( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.stop()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@tv_blueprint.route( "/previous" , methods=[ "GET" ] )
def previous( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.previous()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@tv_blueprint.route( "/next" , methods=[ "GET" ] )
def next( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.next()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@tv_blueprint.route( "/status" , methods=[ "GET" ] )
def status( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )