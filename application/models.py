from sqlalchemy import Table

from app import db


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    etag = db.Column(db.Integer, nullable=False)

    def __init__(self, n, a):
        self.name = n
        self.author = a
        self.etag = 0

    def etagInc(self):
        self.etag += 1

    def toJSON(self):
        return {"id": self.id,
                "name": self.name,
                "author": self.author}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    playlists = db.relationship('Playlist', backref='user')
    etag = db.Column(db.Integer, nullable=False)

    def __init__(self, n, s):
        self.name = n
        self.surname = s
        self.etag = 0

    def etagInc(self):
        self.etag += 1

    def toJSON(self):
        plnames = {}
        i = 1
        for playlist in self.playlists:
            plnames["Playlist #" + str(i)] = playlist.name
            i = i+1
        return {"id": self.id,
                "name": self.name,
                "surname": self.surname,
                "playlists": plnames}


song_playlist = db.Table('song_playlist',
                         db.Column('song_id', db.Integer, db.ForeignKey('song.id')),
                         db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')))


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    length = db.Column(db.Integer, nullable=False)
    songs = db.relationship('Song', secondary=song_playlist)
    etag = db.Column(db.Integer, nullable=False)

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner.id
        self.length = 0
        self.etag = 0

    def etagInc(self):
        self.etag += 1

    def toJSON(self):
        return {"id": self.id,
                "name": self.name,
                "owner id": self.owner,
                "length": self.length
                }

class Merge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    from_playlist_id = db.Column(db.Integer, nullable=False) 
    to_playlist_id = db.Column(db.Integer, nullable=False)
    from_playlist_name = db.Column(db.String(100), nullable = False)
    to_playlist_name = db.Column(db.String(100), nullable = False)

    def __init__(self, from_playlist, to_playlist):
        self.owner_id = from_playlist.owner
        self.from_playlist_id = from_playlist.id
        self.to_playlist_id = to_playlist.id
        self.from_playlist_name = from_playlist.name
        self.to_playlist_name = to_playlist.name

    def toJSON(self):
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "from_playlist_id": self.from_playlist_id,
            "to_playlist_id": self.to_playlist_id,
            "from_playlist_name": self.from_playlist_name,
            "to_playlist_name": self.to_playlist_name
        }
