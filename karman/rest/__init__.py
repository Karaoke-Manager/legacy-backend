from flask_restful import Api

from karman.rest.resources.auth import AuthResource
from karman.rest.resources.songs import SongResource

api = Api()
api.add_resource(SongResource, '/songs/<int:id>')
api.add_resource(AuthResource, '/login')
