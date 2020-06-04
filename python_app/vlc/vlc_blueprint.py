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

vlc_blueprint = Blueprint( 'vlc_blueprint' , url_prefix='/vlc' )

@vlc_blueprint.route( '/' )
def commands_root( request ):
	return response.text( "you are at the /tv url\n" )

@vlc_blueprint.route( "/status" , methods=[ "GET" ] )
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

@vlc_blueprint.route( "/add" , methods=[ "GET" ] )
def add( request ):
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

@vlc_blueprint.route( "/fullscreen/on" , methods=[ "GET" ] )
def fullscreen_on( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.fullscreen_on()
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/fullscreen/off" , methods=[ "GET" ] )
def fullscreen_off( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.fullscreen_off()
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/volume/set" , methods=[ "GET" ] )
def volume_set( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		level = request.args.get( "level" )
		vlc.volume_set( level )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/volume/up" , methods=[ "GET" ] )
def volume_up( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		step = request.args.get( "step" )
		if step == False or step == None:
			step = 1
		vlc.volume_up( step )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/volume/down" , methods=[ "GET" ] )
def volume_down( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		step = request.args.get( "step" )
		if step == False or step == None:
			step = 1
		vlc.volume_down( step )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/seek" , methods=[ "GET" ] )
def seek( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		seconds = request.args.get( "seconds" )
		if seconds == False or seconds == None:
			seconds = 1
		vlc.seek( seconds )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/play" , methods=[ "GET" ] )
def play( request ):
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

@vlc_blueprint.route( "/pause" , methods=[ "GET" ] )
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

@vlc_blueprint.route( "/stop" , methods=[ "GET" ] )
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

@vlc_blueprint.route( "/rewind" , methods=[ "GET" ] )
def rewind( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.rewind()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/next" , methods=[ "GET" ] )
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

@vlc_blueprint.route( "/previous" , methods=[ "GET" ] )
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

@vlc_blueprint.route( "/clear" , methods=[ "GET" ] )
def clear( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.clear()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/loop" , methods=[ "GET" ] )
def loop( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.loop()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/repeat" , methods=[ "GET" ] )
def repeat( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.repeat()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )

@vlc_blueprint.route( "/random" , methods=[ "GET" ] )
def random( request ):
	result = { "message": "failed" }
	try:
		vlc_config = get_vlc_config_from_redis()
		vlc = VLCController( vlc_config )
		vlc.random()
		time.sleep( 1 )
		result["status"] = vlc.get_common_info()
		result["message"] = "success"
	except Exception as e:
		print( e )
		result["error"] = str( e )
	return json_result( result )
