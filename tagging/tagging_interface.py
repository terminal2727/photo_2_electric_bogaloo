from flask import Blueprint, send_file, request
from utils.message_logging import log, MessageLogger
from utils.file_manipulation import get_file_blob
from tagging.tagging import tag, remove_file, TAG_DIR
import os
import random

tagging_interface_blueprint = Blueprint('tagging_interface', __name__)

VALID_NAMES = [
    'favorites',
    'all'
]

CurrentTag = None
Favorites = None
Random = False

class Tag():
    def __init__(self, tag : str, files : list):
        self.tag = tag
        self.files = files
        self.random_files = random.shuffle(files)
        self.current_file = files[0]

@tagging_interface_blueprint.route('/tag_file', methods=['POST'])
def tag_file():
    _tag = request.data.decode('utf-8')
    
    if _tag is None:
        return 'no tag'
    
    logger = MessageLogger()
    tag(_tag, CurrentTag.files[CurrentTag.current_file], logger)
    
    return logger.get_message()

@tagging_interface_blueprint.route('/load_tag', methods=['POST'])
def load_tag():
    global CurrentTag, Favorites
    
    tag = request.data.decode('utf-8')
    
    if tag is None:
        return 'no tag'
    
    if tag not in VALID_NAMES or not os.path.exists(f'{TAG_DIR}/{tag}.txt'):
        return 'tag does not exist'
    
    if tag in VALID_NAMES:
        if tag == 'favorites':
            CurrentTag = Favorites
        elif tag == 'all':
            raise NotImplementedError('all tag not implemented')
        else:
            raise NotImplementedError(f'tag {tag} not implemented')
    else:   
        with open(f'{TAG_DIR}/{tag}.txt', 'r') as f:
            files = f.readlines()
            
        tag = Tag(tag, files)
        CurrentTag = tag
    
    return _get_file_at(CurrentTag.current_file)

@tagging_interface_blueprint.route('/next_file', methods=['POST'])
def get_file():
    global CurrentTag, Random
    dir = request.args.get('dir')
    
    if dir is None:
        return 'no dir'
    
    index = CurrentTag.files.index(CurrentTag.current_file) if not Random else CurrentTag.random_files.index(CurrentTag.current_file)
    if dir == 'next':
        index = (index + 1) % len(CurrentTag.files)
    elif dir == 'prev':
        index = (index - 1) % len(CurrentTag.files)
    elif isinstance(dir, int):
        index = int(dir)
    else:
        return 'invalid dir'
    
    return _get_file_at(index)

@tagging_interface_blueprint.route('/name', methods=['POST'])
def name():
    global CurrentTag
    return CurrentTag.current_file.file_path

@tagging_interface_blueprint.route('/randomize', methods=['POST'])
def randomize():
    global Random
    Random = not Random
    if not Random:
        CurrentTag.random_files = random.shuffle(CurrentTag.files)

@tagging_interface_blueprint.route('/favorite', methods=['POST'])
def favorite():
    global Favorites, CurrentTag
    
    if Favorites is None:
        Favorites = Tag('favorites', [CurrentTag.current_file])
    else:
        if CurrentTag.current_file not in Favorites.files:
            Favorites.files.append(CurrentTag.current_file)
        else:
            Favorites.files.remove(CurrentTag.current_file)

@tagging_interface_blueprint.route('/is_favorited', methods=['POST'])
def is_favorited():
    global Favorites
    file = CurrentTag.current_file
    return file in Favorites.files

@tagging_interface_blueprint.route('/tag_length', methods=['POST'])
def tag_length():
    return len(CurrentTag.files)

@tagging_interface_blueprint.route('/tag_list', methods=['POST'])
def tag_list():
    return [file[0] for file in os.listdir(TAG_DIR) if file.endswith('.txt')]

@tagging_interface_blueprint.route('/tag_startup', methods=['POST'])
def startup():
    load_tag('untagged')
    return _get_file_at(0)

def tag_new_upload(handler, logger):
    if not os.path.exists(TAG_DIR):
        os.mkdir(TAG_DIR)
        
    _, ext = os.path.splitext(handler.file_path)
    
    if ext.lower() in ['.png', '.jpg', '.jpeg']:
        tag('image', handler, logger)
    elif ext.lower() in ['.gif', '.webp']:
        tag('gif', handler, logger)
    elif ext.lower() in ['.mp4', '.mov', '.avi']:
        tag('video', handler, logger)
        
    with open(f'{TAG_DIR}/untagged.txt', 'a') as f:
        f.write(f'{handler.id}\n')
    
    with open(f'{TAG_DIR}/files/{handler.id}.txt', 'w') as f:
        f.write('untagged')
        
    log(logger, f'file {handler.file_path} added to untagged')

def On_File_Deletion(identifier : str):
    id, _, _ = identifier.split(':')
    remove_file(id, MessageLogger())

def _get_file_at(index, random=False):
    global CurrentTag
    
    file = CurrentTag.files[index] if not random else CurrentTag.random_files[index]
    CurrentTag.current_file = file
    
    blob = get_file_blob(file)
    
    return send_file(blob['filename'], blob['mimetype'])