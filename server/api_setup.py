from flask import Flask
from album.album_interface import album_interface_blueprint
from server.client_view import client_view_blueprint
from tagging.tagging_interface import tagging_interface_blueprint
from database.upload_interface import upload_interface_blueprint

# age old question: should I invert the dependency?
# I'm too lazy and the difference is negligible
# so I'll just import the blueprints here even if that means I have to edit this file every time I add a new blueprint

def register_blueprints(app):
    if not isinstance(app, Flask):
        raise TypeError('app must be a Flask instance')
    
    app.register_blueprint(album_interface_blueprint)
    app.register_blueprint(client_view_blueprint)
    app.register_blueprint(tagging_interface_blueprint)
    app.register_blueprint(upload_interface_blueprint)