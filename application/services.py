
import flask
from flask_restful import Resource
from flask import request, make_response
from models import *
from app import db
import json


class SongsService(Resource):
    def get(self):
        resp = flask.make_response()
        page_size = int(request.args.get('size'))
        if page_size <= 0:
            return "Invalid page size.", 404
        page_number = int(request.args.get('page'))
        if page_number <= 0:
            return "Invalid page number.", 404

        songs = Song.query.paginate(int(page_number),int(page_size),error_out=False).items
        list = []
        if songs:
            for song in songs:
                list.append(song.toJSON())
        else:
            return "No data.", 404
        resp.mimetype = "application/json"
        resp.response = json.dumps(list)
        header_content = ""
        if db.session.query(Song).count() > page_size*page_number:
            header_content += "<localhost:5000/songs?size=" + str(page_size) + "&page=" + str(page_number + 1) + ">;rel=prev;"
        if page_number != 1:
            header_content += "<localhost:5000/songs?size=" + str(page_size) + "&page=" + str(page_number - 1) + ">;rel=next;"
        resp.headers['Link'] = header_content
        return resp

    def post(self):
        #post exatcly once -> empty post
        song = Song("", "")
        db.session.add(song)
        db.session.commit()
        return song.toJSON(), 201


class SongService(Resource):
    def get(self, sid):
        song = Song.query.get_or_404(sid)
        etag = request.headers.get("If-None-Match")
        resp = flask.make_response()
        if etag is None or int(etag) != song.etag:
            resp.mimetype = "application/json"
            resp.response = json.dumps(song.toJSON())
            resp.status_code = 200
            resp.headers["Etag"] = song.etag
        else:
            resp.response = "Not modified."
            resp.status_code = 304
        return resp

    def put(self, sid):
        content = request.json
        song = Song.query.get_or_404(sid)
        etag = request.headers.get("If-Match")
        if etag is None:
            resp = flask.make_response()
            resp.response = "Precondition required."
            resp.status_code = 428
            return resp
        if int(etag) != song.etag:
            resp = flask.make_response()
            resp.response = "Precondition failed."
            resp.status_code = 412
            return resp

        if content["name"] == "" or content["author"] == "":
            return "Invalid name or author.", 400
        song.name = content["name"]
        song.author = content["author"]
        db.session.commit()
        return "Update succesful."

    def delete(self, sid):
        song = Song.query.get_or_404(sid)
        db.session.delete(song)
        db.session.commit()
        return song.name + " is no more."


class UsersService(Resource):
    def get(self):
        users = User.query.all()
        list = []
        if users:
            for user in users:
                list.append(user.toJSON())
            return list
        else:
            return "No data.", 204

    def post(self):
        content = request.json
        user = User(content["name"], content["surname"])
        db.session.add(user)
        db.session.commit()
        return "User added successfully.", 201

class UserService(Resource):
    def get(self, uid):
        user = User.query.get_or_404(uid)
        etag = request.headers.get("If-None-Match")
        resp = flask.make_response()
        if etag is None or int(etag) != user.etag:
            resp.mimetype = "application/json"
            resp.response = json.dumps(user.toJSON())
            resp.status_code = 200
            resp.headers["Etag"] = user.etag
        else:
            resp.response = "Not modified."
            resp.status_code = 304
        return resp

    def put(self, uid):
        content = request.json
        user = User.query.get_or_404(uid)
        etag = request.headers.get("If-Match")
        if etag is None:
            resp = flask.make_response()
            resp.response = "Precondition required."
            resp.status_code = 428
            return resp
        if int(etag) != user.etag:
            resp = flask.make_response()
            resp.response = "Precondition failed."
            resp.status_code = 412
            return resp
        user.etagInc()
        user.name = content["name"]
        user.surname = content["surname"]
        db.session.commit()
        return "Update successful."

    def delete(self, uid):
        user = User.query.get_or_404(uid)
        db.session.delete(user)
        db.session.commit()
        return user.name + " is no more."


class PlaylistsService(Resource):
    def get(self, uid):
        user = User.query.get_or_404(uid)
        if user.playlists:
            content = []
            for playlist in user.playlists:
                content.append(playlist.toJSON())
            return content
        else:
            return "No playlists found.", 404

    def post(self, uid):
        body = request.json
        owner = User.query.get_or_404(uid)
        pl = Playlist(body["name"], owner)
        db.session.add(pl)
        db.session.commit()
        return "Playlist added successfully.", 201


class PlaylistService(Resource):
    def get(self, uid, pid):
        user = User.query.get(uid)
        if user is None:
            return "No such user found.", 404
        playlist = Playlist.query.get_or_404(pid)
        if int(user.id) != int(playlist.owner):
            return "This user doesn't own this playlist.", 400
        etag = request.headers.get("If-None-Match")
        resp = flask.make_response()
        if etag is None or int(etag) != playlist.etag:
            resp.mimetype = "application/json"
            resp.response = json.dumps(playlist.toJSON())
            resp.status_code = 200
            resp.headers["Etag"] = playlist.etag
        else:
            resp.response = "Not modified."
            resp.status_code = 304
        return resp

    def delete(self, uid, pid):
        user = User.query.get(uid)
        if user is None:
            return "No such user found.", 404
        playlist = Playlist.query.get_or_404(pid)
        db.session.delete(playlist)
        db.session.commit()
        return playlist.name + " is no more."

    def patch(self, uid, pid):
        user = User.query.get(uid)
        if user is None:
            return "No such user found.", 404
        playlist = Playlist.query.get_or_404(pid)
        content = request.json
        etag = request.headers.get("If-Match")
        if etag is None:
            resp = flask.make_response()
            resp.response = "Precondition required."
            resp.status_code = 428
            return resp
        if int(etag) != user.etag:
            resp = flask.make_response()
            resp.response = "Precondition failed."
            resp.status_code = 412
            return resp

        if "name" in content:
            playlist.etagInc()
            playlist.name = content["name"]
            db.session.commit()
            return "Playlist name changed successfully to " + content["name"] + ".\n"

class PlaylistSongsService(Resource):
    def post(self, uid, pid):
        user = User.query.get(uid)
        if user==None:
            return "No such user found.", 404
        playlist = Playlist.query.get(pid)
        if playlist==None:
            return "No such playlist.", 404
        if user.id != playlist.owner:
            return "This user doesn't own this playlist.", 400

        content = request.json
        song = Song.query.get(content["song_id"])
        if song==None:
            return "No such song.", 404

        for song_p in playlist.songs:
            if song_p.id == song.id:
                return "This song is already on a playlist.\n", 304

        playlist.songs.append(song)
        playlist.length += 1
        db.session.commit()
        return("Song " + str(content["song_id"]) + " added to playlist " + str(playlist.id) + ".\n") 

    def get(self, uid, pid):
        user = User.query.get(uid)
        if user==None:
            return "No such user found.", 404
        playlist = Playlist.query.get(pid)
        if playlist==None:
            return "No such playlist.", 404
        if user.id != playlist.owner:
            return "This user doesn't own this playlist.", 400

        list = []
        if playlist.songs:
            for song in playlist.songs:
                list.append(song.toJSON())
            return list
        else:
            return "No data.", 204

class PlaylistSongService(Resource):
    def get(self, uid, pid, sid):
        user = User.query.get(uid)
        if user==None:
            return "No such user found.", 404
        playlist = Playlist.query.get(pid)
        if playlist==None:
            return "No such playlist.", 404
        if user.id != playlist.owner:
            return "This user doesn't own this playlist.", 404
        song = Song.query.get(sid)
        if song is None:
            return "No such song.", 404
        return song.toJSON()
    
    def delete(self, uid, pid, sid):
        user = User.query.get(uid)
        if user is None:
            return "No such user found.", 404
        playlist = Playlist.query.get(pid)
        if playlist==None:
            return "No such playlist.", 404
        if user.id != playlist.owner:
            return "This user doesn't own this playlist.", 400
        song = Song.query.get(sid)
        if song is None:
            return "No such song.", 404
        playlist.remove(song)
        playlist.length -= 1
        db.session.commit()
        return "This song has been removed from the playlist."

class MergesService(Resource):
    def get(self):
        merges = Merge.query.all()
        list = []
        if merges:
            for merge in merges:
                list.append(merge.toJSON())
            return list
        else:
            return "No data.", 204

class MergeService(Resource):
    def get(self,uid):
        merges = Merge.query.filter_by(owner_id=uid)
        list = []
        if merges:
            for merge in merges:
                list.append(merge.toJSON())
            return list
        else:
            return "No data.", 204

    def post(self,uid):
        user = User.query.get(uid)
        if user is None:
            return "No such user found.", 404

        content = request.json
        if content["from"]:
            from_playlist = Playlist.query.get(content["from"])
            if from_playlist is None:
                return "There is no playlist with id " + content["from"], 404
            else:
                if int(from_playlist.owner) != int(uid):
                    return "At least one of the playlists doesn't belong to this user.", 400
        else:
            return "Incomplete json.", 400

        if content["to"]:
            to_playlist = Playlist.query.get(content["to"])
            if to_playlist is None:
                return "There is no playlist with id " + content["from"], 404
            else:
                if int(to_playlist.owner) != int(uid):
                    return "At least one of the playlists doesn't belong to this user.", 400
        else:
            return "Incomplete json.", 400

        merge = Merge(from_playlist, to_playlist)
        db.session.add(merge)
        db.session.commit()

        to_playlist.name += " & " + from_playlist.name

        duplicates_count = 0
        for song_from in from_playlist.songs:
            duplicate = False
            for song_to in to_playlist.songs:
                if song_from.id == song_to.id:
                    duplicate = True
                    duplicates_count += 1
                    break
            if not duplicate:
                to_playlist.songs.append(song_from)
        to_playlist.length += from_playlist.length - duplicates_count

        db.session.delete(from_playlist)
        db.session.commit()
        return "Merge successful."

