from flask import Blueprint, jsonify, request, send_from_directory
from datetime import datetime
import os

album_interface_blueprint = Blueprint('album_interface', __name__)

class Album():
    def __init__(self, name : str, files : list) -> None:
        self.name = name
        self.files = files
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()

CurrentAlbum : Album = None

@album_interface_blueprint.route('/album/get_photos', methods=['GET'])
def get_photos():        
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_photos = CurrentAlbum.files[start:end]
    
    has_more = end < len(CurrentAlbum.files)
    
    return jsonify({
        'photos': paginated_photos,
        'has_more': has_more
    })

@album_interface_blueprint.route('/file/<file_name>')
def get_file(file_name):
    name, ext = os.path.splitext(file_name)
    length = len(name) - 1 if len(name) - 1 < 127 else 127
    return send_from_directory(f'uploaded_files/{length}', file_name)