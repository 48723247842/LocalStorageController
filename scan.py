import subprocess
import shellescape
import time
from pathlib import Path
import base64
from pprint import pprint

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

ALLOWED_VIDEO_FILE_EXTENSIONS = [ ".mkv" , "mp4" , "avi" ]

def scan_posix_path( posix_path ):
	posix_paths = list( posix_path.rglob( '**/*' ) )
	posix_paths = [ x for x in posix_paths if x.is_file() ]
	posix_paths = [ x for x in posix_paths if x.suffix in ALLOWED_VIDEO_FILE_EXTENSIONS ]
	return posix_paths

def find_tv_shows( base_path_string ):
	tv_shows = scan_posix_path( Path( base_path_string ) )
	tv_shows_map = {}
	for index , posix_episode in enumerate( tv_shows ):
		items = str( posix_episode ).split( base_path_string )[ 1 ].split( "/" )
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
		show_name_b64 = base64_encode( show_name )
		season_name_b64 = base64_encode( season_name )
		episode_name_b64 = base64_encode( episode_name )
		if show_name_b64 not in tv_shows_map:
			tv_shows_map[ show_name_b64 ] = {}
		if season_name_b64 not in tv_shows_map[ show_name_b64 ]:
			tv_shows_map[ show_name_b64 ][ season_name_b64 ] = []
		tv_shows_map[ show_name_b64 ][ season_name_b64 ].append( episode_name_b64 )
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
	return tv_shows_map_organized

def mount_usb_drive( uuid ):

	desired_mount_point = f"/media/{uuid}"

	device_path = subprocess.getoutput( f"lsblk -o UUID,PATH | grep {uuid}" + " | awk '{print $2}'" )
	current_mount_point = subprocess.getoutput( f"lsblk -o UUID,MOUNTPOINT | grep {uuid}" + " | awk '{print $2}'" )

	if current_mount_point == desired_mount_point:
		print( f"Already Mounted at Desired Mount Point: {desired_mount_point}" )
		return desired_mount_point

	if len( current_mount_point ) < 3:
		print( f"{device_path} Not Mounted Anywhere" )
	else:
		print( f"Ubuntu Auto Mounted Drive ... Unmounting {current_mount_point}" )
		subprocess.getoutput( f"sudo umount {current_mount_point}" )

	subprocess.getoutput( f"sudo mkdir {desired_mount_point}" )
	print( f"Mounting at {desired_mount_point}" )
	subprocess.getoutput( f"sudo mount {device_path} {desired_mount_point}" )
	time.sleep( 3 )
	return desired_mount_point

if __name__ == '__main__':
	usb_drive_path = mount_usb_drive( "187A29A07A297B9E" )
	tv_shows = find_tv_shows( f"{usb_drive_path}/MEDIA_MANAGER/TVShows/" )
	pprint( tv_shows )