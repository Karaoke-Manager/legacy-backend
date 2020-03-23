from karman.models import db


class Song(db.Model):
    class Meta:
        info = {"test": "dwf"}
        something = "Test"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
