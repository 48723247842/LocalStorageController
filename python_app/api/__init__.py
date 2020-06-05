from sanic import Blueprint

from .tv import tv_blueprint
from .movies import movies_blueprint
from .music import music_blueprint
from .odyssey import odyssey_blueprint
from .audiobooks import audiobooks_blueprint

api_blueprint = Blueprint.group(
	tv_blueprint , movies_blueprint , music_blueprint ,
	odyssey_blueprint , audiobooks_blueprint ,
	url_prefix='/api'
	)