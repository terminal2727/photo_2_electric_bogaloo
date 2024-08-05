from flask import Blueprint, render_template, request

views = {
    'home': 'home.html',
    'tag': 'tag.html',
    'album': 'album.html',
    'settings': 'settings.html'
}

client_view_blueprint = Blueprint('client_view', __name__)

def render_home():
    return switch_view('home')

def switch_view(view):
    mobile = 'Mobile' in request.headers.get('User-Agent')
    
    if view in views:
        # flask automatically looks in the templates directory, so we don't need to specify the path for the desktop views
        return render_template('templates/mobile/' + views[view] if mobile else views[view])
    
    print (f'View {view} not found')