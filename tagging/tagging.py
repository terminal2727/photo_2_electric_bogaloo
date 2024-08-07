from database.file_handling import FileHandler
from utils.message_logging import log
from utils.file_manipulation import remove_line_from_file
import os

TAG_DIR = 'tags'
        
def tag(tag, handler, logger, create_new_tag=True):
    if not isinstance(tag, str) or not isinstance(handler, FileHandler) :
        log(logger, f'Tag: {tag}, Handler: {handler}')
        return

    tag = tag.lower().strip()
    
    if os.path.exists(f'{TAG_DIR}/{tag}.txt'):
        with open(f'{TAG_DIR}/{tag}.txt', 'r') as f:
            lines = f.readlines()
            
            for l in lines:
                if handler.id in l:
                    log(logger, f'file {handler.file_path} already tagged with {tag}')
                    return
    elif not create_new_tag:
        log(logger, f'Tag: {tag} does not exist')
        return
    
    with open(f'{TAG_DIR}/{tag}.txt', 'a') as f:
        f.write(f'{handler.id}\n')
    
    if not os.path.exists(f'{TAG_DIR}/files'):
        os.makedirs(f'{TAG_DIR}/files')
    
    with open(f'{TAG_DIR}/files/{handler.id}.txt', 'a') as f:
        f.write(f'{tag}\n')
    
    untag('untagged', handler, logger, delete_tag=False)
    
    log(logger, f'file {handler.file_path} tagged with {tag}')

def untag(tag, handler, logger, delete_tag=True):
    if not isinstance(tag, str) or not isinstance(handler, FileHandler):
        log(logger, f'Tag: {tag}, Handler: {handler}')
        return
    
    tag = tag.lower().strip()
    
    if os.path.exists(f'{TAG_DIR}/{tag}.txt'):
        remove_line_from_file(handler.id, f'{TAG_DIR}/{tag}.txt')
        
    with open(f'{TAG_DIR}/files/{handler.id}.txt', 'r') as f:
        empty = len(f.readlines()) == 1 # We don't consider file type tags as tags - because every file has them
    
    if empty:
        with open(f'{TAG_DIR}/files/{handler.id}.txt', 'w') as f:
            f.write('untagged')
    
    if not delete_tag: # If we don't want to delete the tag, we're done, we don't need to check if the tag file is empty
        return
    
    empty = False
    with open(f'{TAG_DIR}/{tag}.txt', 'r') as f:
        empty = not f.readlines()
    
    if empty:
        os.remove(f'{TAG_DIR}/{tag}.txt')
        
def remove_file(id, logger):
    tags = [file for file in os.listdir(TAG_DIR) if file.endswith('.txt')]
    for tag in tags:
        name, _ = os.path.splitext(tags)
        untag(name, id, logger, delete_tag=False)

    os.remove(f'{TAG_DIR}/files/{id}.txt')
    
    log(logger, f'file {id} removed from tags')