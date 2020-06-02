import subprocess
import shellescape
import time
from pathlib import Path
import base64
from pprint import pprint
import redis

def base64_encode( string ):
	string_bytes = string.encode( "utf-8" )
	base64_bytes = base64.b64encode( string_bytes )
	base64_string = base64_bytes.decode( "utf-8" )
	return base64_string

def base64_decode( string ):
	string_bytes = string.encode( "utf-8" )
	base64_bytes = base64.b64decode( string_bytes )
	message = base64_bytes.decode( "utf-8" )
	return message

class USBStorage:

	def __init__( self , options={} ):

		self.options = options
		if "uuid" not in self.options:
			print( "you have to pass a uuid" )
			return False
		if "desired_mount_point" not in self.options:
			self.options["desired_mount_point"] = f"/media/{self.options['uuid']}"
		if "allowed_video_types" not in self.options:
			self.options["allowed_video_types"] = [ ".mkv" , "mp4" , "avi" ]

		self.mount_usb_drive()
		self.paths = { "usb": Path( self.options["desired_mount_point"] ) }
		self.paths["media_manager"] = self.paths["usb"].joinpath( "MEDIA_MANAGER" )
		self.paths["tv_shows"] = self.paths["media_manager"].joinpath( "TVShows" )
		self.paths["movies"] = self.paths["media_manager"].joinpath( "Movies" )
		self.paths["music"] = self.paths["media_manager"].joinpath( "Music" )
		self.paths["audio_books"] = self.paths["media_manager"].joinpath( "AudioBooks" )
		self.paths["odyssey"] = self.paths["media_manager"].joinpath( "Odyssey" )
		self.redis = self.redis_connect()
		self.library_valid = self.redis.get( "STATE.USB_STORAGE.LIBRARY.VALID" )
		if self.library_valid == False or self.library_valid == None or self.library_valid == "":
			self.rebuild_library()

	def redis_connect( self ):
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

	def scan_posix_path( self , posix_path ):
		posix_paths = list( posix_path.rglob( '**/*' ) )
		posix_paths = [ x for x in posix_paths if x.is_file() ]
		posix_paths = [ x for x in posix_paths if x.suffix in self.options["allowed_video_types"] ]
		return posix_paths

	def mount_usb_drive( self ):

		device_path = subprocess.getoutput( f"lsblk -o UUID,PATH | grep {self.options['uuid']}" + " | awk '{print $2}'" )
		current_mount_point = subprocess.getoutput( f"lsblk -o UUID,MOUNTPOINT | grep {self.options['uuid']}" + " | awk '{print $2}'" )

		if current_mount_point == self.options["desired_mount_point"]:
			print( f"Already Mounted at Desired Mount Point: {self.options['desired_mount_point']}" )
			return self.options['desired_mount_point']

		if len( current_mount_point ) < 3:
			print( f"{device_path} Not Mounted Anywhere" )
		else:
			print( f"Ubuntu Auto Mounted Drive ... Unmounting {current_mount_point}" )
			subprocess.getoutput( f"sudo umount {current_mount_point}" )

		subprocess.getoutput( f"sudo mkdir {self.options['desired_mount_point']}" )
		print( f"Mounting at {self.options['desired_mount_point']}" )
		subprocess.getoutput( f"sudo mount {device_path} {self.options['desired_mount_point']}" )
		time.sleep( 3 )

	def rebuild_library( self ):
		print( "Library Invalid" )
		self.rebuild_tv_shows()

	def rebuild_tv_shows( self ):
		print( "Rebuilding TV Shows" )
		# Testing Delete All via CLI
		# redis-cli -n 1 --raw keys "STATE.USB_STORAGE.LIBRARY.*" | xargs redis-cli -n 1 del
		tv_shows = self.scan_posix_path( self.paths["tv_shows"] )
		tv_shows_map = {}
		for index , posix_episode in enumerate( tv_shows ):
			items = str( posix_episode ).split( str( self.paths["tv_shows"] ) + "/" )[ 1 ].split( "/" )
			if len( items ) == 3:
				show_name = items[ 0 ]
				season_name = items[ 1 ]
				episode_name = items[ 2 ]
			elif len( items ) == 2:
				show_name = items[ 0 ]
				season_name = items[ 1 ]
				episode_name = items[ 2 ]
			elif len( items ) == 1:
				show_name = "SINGLES"
				season_name = "000"
				episode_name = items[ 0 ]
			else:
				print( "wadu" )
				print( items )
				continue

			# Don't Ask
			show_name_b64 = base64_encode( show_name )
			season_name_b64 = base64_encode( season_name )
			episode_name_b64 = base64_encode( episode_name )
			if show_name_b64 not in tv_shows_map:
				tv_shows_map[ show_name_b64 ] = {}
			if season_name_b64 not in tv_shows_map[ show_name_b64 ]:
				tv_shows_map[ show_name_b64 ][ season_name_b64 ] = []
			tv_shows_map[ show_name_b64 ][ season_name_b64 ].append( episode_name_b64 )

		# Also Don't Ask
		tv_shows_map_organized = {}
		show_names_b64 = tv_shows_map.keys()
		show_names = [ base64_decode( x ) for x in show_names_b64 ]
		show_names.sort()
		for index , show_name in enumerate( show_names ):
			season_names_b64 = tv_shows_map[ base64_encode( show_name ) ].keys()
			tv_shows_map_organized[ show_name ] = [ base64_decode( x ) for x in season_names_b64 ]
			tv_shows_map_organized[ show_name ].sort()
			for season_index , season in enumerate( tv_shows_map_organized[ show_name ] ):
				episode_names_b64 = tv_shows_map[ base64_encode( show_name ) ][ base64_encode( season ) ]
				episode_names = [ base64_decode( x ) for x in episode_names_b64 ]
				episode_names.sort()
				tv_shows_map_organized[ show_name ][ season_index ] = episode_names

		# Finally Store into Redis

		# 1.) Store All Shows into Circular List
		show_keys = tv_shows_map_organized.keys()
		show_names_b64 = [ base64_encode( x ) for x in show_keys ]
		for x in show_names_b64:
			self.redis.rpush( "STATE.USB_STORAGE.LIBRARY.TV_SHOWS" , x )

		for show_index , show in enumerate( show_keys ):
			for season_index , season in enumerate( tv_shows_map_organized[ show ] ):
				# 2.) Store All Seasons into Circular List
				season_key_part = str( str( season_index ).zfill( 2 ) )
				self.redis.rpush( f"STATE.USB_STORAGE.LIBRARY.TV_SHOWS.{show_names_b64[show_index]}.SEASONS" , season_key_part )
				for episode_index , episode in enumerate( tv_shows_map_organized[ show ][ season_index ] ):
					list_key = f"STATE.USB_STORAGE.LIBRARY.TV_SHOWS.{show_names_b64[show_index]}.SEASONS.{season_key_part}"
					# 2.) Store Episode into Circular List
					self.redis.rpush( list_key , base64_encode( episode ) )



if __name__ == '__main__':
	usb_storage = USBStorage({
			"uuid": "187A29A07A297B9E"
		})
	# tv_shows = find_tv_shows( f"{usb_drive_path}/MEDIA_MANAGER/TVShows/" )
	# pprint( tv_shows )