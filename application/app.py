# venv\scripts\activate
#  & "c:/Users/amwsz/Documents/seweryn/REST API/.venv/Scripts/Activate.ps1"

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

from services import *

api = Api(app)

api.add_resource(SongsService, "/songs") #get, post
api.add_resource(SongService, "/songs/<sid>") #get, put, delete
api.add_resource(UsersService, "/users") #get, post
api.add_resource(UserService, "/users/<uid>") #get, put, delete
api.add_resource(PlaylistsService, "/users/<uid>/playlists") #get, post
api.add_resource(PlaylistService, "/users/<uid>/playlists/<pid>") #get, patch, delete
api.add_resource(PlaylistSongsService, "/users/<uid>/playlists/<pid>/songs") #get, post
api.add_resource(PlaylistSongService, "/users/<uid>/playlists/<pid>/songs/<sid>") #get, delete
api.add_resource(MergeService,"/users/<uid>/playlists/merges") #post, get

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def main():
    return "Welcome to the music service main page!"


if __name__ == "__main__":
    app.run(debug=True)
