from sanic import Blueprint
from sanic.response import json as json_result
from sanic import response

import json
import time
from datetime import datetime , timedelta
from pytz import timezone
eastern_time_zone = timezone( "US/Eastern" )
# datetime.now( eastern_tz ) - timedelta(minutes=59)
from pprint import pprint
import redis
import redis_circular_list

from vlc_controller import VLCController

import utils

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

def get_current_episode( file_path_b64=None ):
	try:
		redis = redis_connect()
		if file_path_b64 is None:
			current_tv_show_name_b64 = redis_circular_list.current( redis , "STATE.USB_STORAGE.LIBRARY.TV_SHOWS" )
			current_tv_show_name = utils.base64_decode( current_tv_show_name_b64 )
			file_path_b64 = redis_circular_list.current( redis , f"STATE.USB_STORAGE.LIBRARY.TV_SHOWS.{current_tv_show_name_b64}" )

		file_path = utils.base64_decode( file_path_b64 )
		meta_data_key = f"STATE.USB_STORAGE.LIBRARY.META_DATA.{file_path_b64}"
		meta_data = redis.get( meta_data_key )
		if meta_data is None:
			meta_data = {
				"current_time": 0 ,
				"duration": 0 ,
				"last_watched_time": 0 ,
				"last_completed_time": 0 ,
				"file_path": file_path
			}
			redis.set( meta_data_key , json.dumps( meta_data ) )
		else:
			meta_data = json.loads( meta_data )
		return meta_data
	except Exception as e:
		print( e )
		return False

def is_episode_over( episode ):
	if "duration" not in episode:
		return False
	if "current_time" not in episode:
		return False
	if episode["current_time"] == 0:
		return False
	if episode["duration"] == 0:
		return False
	if ( episode["duration"] - episode["current_time"] ) < 3:
		return True
	else:
		return False

def get_next_episode( file_path=None ):
	redis = redis_connect()
	if file_path is not None:
		file_path = utils.base64_encode( file_path )

	episode = get_current_episode( file_path )
	while is_episode_over( episode ) == True:
		current_tv_show_name_b64 = redis_circular_list.current( redis , "STATE.USB_STORAGE.LIBRARY.TV_SHOWS" )
		current_tv_show_name = utils.base64_decode( current_tv_show_name_b64 )
		file_path_b64 = redis_circular_list.next( redis , f"STATE.USB_STORAGE.LIBRARY.TV_SHOWS.{current_tv_show_name_b64}" )
		print( file_path_b64 )
		episode = get_current_episode( file_path_b64 )

	return episode


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
		next_episode = get_next_episode( file_path )
		pprint( next_episode )
		vlc.add( next_episode["file_path"] )
		time.sleep( 1 )
		if next_episode["current_time"] > 0:
			vlc.seek( next_episode["current_time"] )
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