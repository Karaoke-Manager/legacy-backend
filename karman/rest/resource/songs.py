from flask_restful import Resource


class SongResource(Resource):
    def get(self, id):
        return {
            "type": "Song",
            "title": "Some Title"
        }
