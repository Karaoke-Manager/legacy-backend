from karman.rest.api import api
from karman.rest.resource import AuthResource, SongResource

api.add_resource(AuthResource, '/login')
# api.add_resource(UserResource, '/users/<int:id>')
# api.add_resource(UserResource, '/users/<string:username>')
api.add_resource(SongResource, '/songs/<int:id>')
