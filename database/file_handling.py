from threading import Thread
from typing import Callable
from utils.message_logging import log
from werkzeug.datastructures import FileStorage
import inspect
import os
import secrets

# TODO: Break deletion functionality into its own, separate module
# TODO: Setup async startup file validation in its own, separate module
# TODO: Consider instead of saving the id:path:modified to the individual file mappings, just saving the id, since the mfm will have the id:path:modified

UPLOAD_PATH = f'uploaded_files'
CHUNK_SIZE = 500 # Initial uploads will be fairly large, but subsequent ones will be smaller... Saving files after the initial upload was never a problem, so this is probably ok 
DELETED_FOLDER_SIZE = 1024 # Arbitrary number, but we need to start actually deleting files at some point
FileDeletedEvent = None

class FileHandler():
    def __init__(self, id, file_path, modified):
        self.id = id 
        self.file_path = file_path
        self.modified = modified

class FileDeletionEvent():
    def __init__(self):
        self.events = {}
     
def upload_files(files : list, modifieds : list, logger) -> list:    
    for i in range(0, 128):
        if not os.path.exists(f'{UPLOAD_PATH}/{i}'):
            os.makedirs(f'{UPLOAD_PATH}/{i}')
    
    preexisting_files = []
    
    for i in range(len(files)):
        #/guard clauses
        if not isinstance(files[i], FileStorage) or not isinstance(modifieds[i], str) or files[i].filename == '':
            log(logger, f'{not isinstance(files[i], FileStorage)} \n 
                          {not isinstance(modifieds[i], str)} \n 
                          {files[i].filename == ''} \n'
            )
            continue
        #/end guard clauses
        
        name, ext = os.path.splitext(files[i].filename)
        length = len(name) - 1 if len(name) - 1 < 127 else 127
        
        if os.path.exists(f'{UPLOAD_PATH}/{length}/{files[i].filename}'):
            preexisting_files.append(files[i].filename)
            continue
        
        if len(os.path.abspath(f'{UPLOAD_PATH}/{length}/{files[i].filename}')) > 260:
            log(logger, f'File name too long for Windows: {files[i].filename}, trunacting...')
            
            length = 260 - len(os.path.abspath(f'temp')) - len(ext)
            files[i].filename = files[i].filename[:length] + ext
            
            log(logger, f'New file name: {files[i].filename}')
    
    valid_files = [files[i] for i in range(len(files)) if files[i].filename not in preexisting_files]
    
    chunks = []
    for i in range(0, len(valid_files), CHUNK_SIZE):
        chunks.append(valid_files[i:i + CHUNK_SIZE])
    
    def process_chunk(chunk : list, handlers : list, modified : list):
        for i, file in enumerate(chunk):
            name, _ = os.path.splitext(file.filename)
            length = len(name) - 1 if len(name) - 1 < 127 else 127
            
            fp = f'{UPLOAD_PATH}/{length}/{file.filename}'
            
            file.save(fp)
            
            handlers.append(FileHandler(_generate_id(file.filename.split('.')[0]), fp, modifieds[i]))
    
    t = []
    handlers = []
    for i, chunk in enumerate(chunks):
        handlers[i] = []
        t.append(
            Thread(
                target=process_chunk, 
                args=(chunk, handlers[i], modifieds)
            )
            .start()
        )
    
    for val in t:
        val.join()
    
    # possible optimization: chunking files by length dirs and writing them all at once
    def update_file_mappings(handlers : list, modifieds : list):
        for i, file in enumerate(handlers):
            name = os.path.basename(file.file_path).split('.')[0]
            length = len(name) if len(name) < 128 else 127
            
            encoded = _encode_file(file, modifieds[i])
            
            with open(f'{UPLOAD_PATH}/{length}/file_mappings.txt', 'a') as f:
                f.write(f'{encoded} \n')
    
    for handle in handlers:
        for file in handle:
            update_file_mappings(file, modifieds[files.index(file)])

    with open(f'{UPLOAD_PATH}/master_file_mappings.txt', 'a') as f:
        for handle in handlers:
            for file in handle:
                encoded = _encode_file(file, modifieds[files.index(file)])
                f.write(f'{encoded} \n')
    
    return handlers

def _generate_id(file : str):
    random_value = secrets.token_hex(4)
    name = os.path.splitext(file)[0]
    hex_length = hex(len(name))[2:].zfill(2)
    
    print(random_value, hex_length, f'Generated ID for {file}')
    
    return hex_length + random_value 

def delete_file(identifer : str):    
    file_to_be_deleted = ''
    files = []
    with open(f'{UPLOAD_PATH}/master_file_mappings.txt', 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            if identifer in line:
                file_to_be_deleted = line.strip()
                continue
            
            files.append(line)
    
    with open(f'{UPLOAD_PATH}/master_file_mappings.txt', 'w') as f:
        f.writelines(files)
    
    id, path, _ = file_to_be_deleted.split(':')
    
    length = int(id[:2], 16)
    
    with open(f'{UPLOAD_PATH}/{length}/file_mappings.txt', 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            if id in line or path in line:
                continue
            
            files.append(line)
    
    with open(f'{UPLOAD_PATH}/{length}/file_mappings.txt', 'w') as f:
        f.writelines(files)
    
    # we'll move files to a different directory so the file can be recovered if needed
    os.rename(path, f'{UPLOAD_PATH}/deleted/{os.path.basename(path)}')
    
    # if there's an arbitary (but large) number of files already in the delete folder, we'll start deleting the oldest ones
    # if the user doesn't recover the file after, like, 1024 files are in the deleted folder, that's on them
    # and if they're deleting more than 1024 files, they probably don't care about the files in the deleted folder
    deleted_files = os.listdir(f'{UPLOAD_PATH}/deleted')
    deleted_files.sort(key=lambda x: os.path.getctime(os.path.join(f'{UPLOAD_PATH}/deleted', x)))
    
    if len(deleted_files) > DELETED_FOLDER_SIZE:
            os.remove(os.path.join(f'{UPLOAD_PATH}/deleted', deleted_files[0]))
    
    # bad practice blah blah blah
    # I don't need to nor want to code an entirely separate event module just to handle a single event
    global FileDeletedEvent
    
    for event_handlers in FileDeletedEvent.events.values():
        for handler in event_handlers:
            handler(identifer)

def validate_files(file : str):
    pass

# This function is so large because we also handle the possibility that the file is not in the master_file_mappings.txt
# I'm not sure how that happens, but it does. So we deal with it here when it's attempted to be retrieved.
# TODO: check the deleted folder as well, so if the file handler is still floating around somehow it can be dealt with
def get_handler(file_or_id : str, skip_subsequent_checks=False) -> FileHandler:
    with open(f'{UPLOAD_PATH}/master_file_mappings.txt', 'r') as f:
        lines = f.readlines()
        
        for line in lines:
            if file_or_id in line:
                return _decode_file(line)
    
    if not skip_subsequent_checks:
        return None
    
    # If the file is not in the master_file_mappings.txt, we need to check if it's a file path or an ID
    # here we check if it's a file path and handle it accordingly
    if '/' in file_or_id:
        file_name = os.path.basename(file_or_id)
        name = os.path.splitext(file_name)[0]
        length = len(name) if len(name) < 128 else 127
        
        if not os.path.exists(f'{UPLOAD_PATH}/{length}/{file_name}'):
            print('File does not exist: ', file_or_id)
            return None
        else:
            print('File "', file_or_id, '" was found, but not in master_file_mappings.txt, adding...')
            with open(f'{UPLOAD_PATH}/master_file_mappings.txt', 'a') as f:
                fp = f'{_generate_id(name)}:{file_name}:{os.path.getmtime(file_or_id)}'
                f.write(f'{fp} \n')
                return _decode_file(fp)

    # here we check if it's an ID and handle it accordingly
    if len(file_or_id) == 10 and file_or_id.isalnum():
        print('Possible ID found: ', file_or_id, 'but was not in master_file_mapping.txt. Attempting to find...')
        
        hex_id = file_or_id[:2]
        
        try:
            length = int(hex_id, 16)
        except ValueError:
            print('Invalid ID found: ', file_or_id)
            return None
        
        if length >= 128:
            print('Invalid ID found: ', file_or_id)
            return None
        
        with open(f'{UPLOAD_PATH}/{length}/file_mappings.txt', 'r') as f:
            lines = f.readlines()
            
            for line in lines:
                if file_or_id not in line:
                    continue
                
                print('Valid ID file found: ', line.strip(), '. Adding to master_file_mappings.txt...')
                
                with open(f'{UPLOAD_PATH}/master_file_mappings.txt', 'a') as mfm:
                    mfm.write(line)
                
                return _decode_file(line)
        
        print(f'Could not find ID {file_or_id} in mappings.')
        
        return None
    
    print('File not found in master_file_mappings.txt: ', file_or_id)

def _encode_file(file : FileHandler, modified : str) -> str:
    return f'{file.id}:{file.file_path}:{modified}'

def _decode_file(file : str) -> FileHandler:
    id, path, modified = file.split(':')
    return FileHandler(id, path, modified)

def subscribe_to_deletion_event(event_id : str, handler : Callable[[str], None]):
    global FileDeletedEvent
    
    if FileDeletedEvent is None:
        FileDeletedEvent = FileDeletionEvent()
    
    sig = inspect.signature(handler)
    if len(sig.parameters) != 1:
        raise ValueError('Handler must only take one parameter (str)')
    
    if event_id not in FileDeletedEvent.events:
        FileDeletedEvent.events[event_id] = []
    
    FileDeletedEvent.events[event_id].append(handler)

def unsubscribe_from_deletion_event(event_id : str, handler : Callable[[str], None]):
    global FileDeletedEvent
    
    if FileDeletedEvent is None:
        return
    
    if event_id not in FileDeletedEvent.events:
        return
    
    if handler in FileDeletedEvent.events[event_id]:
        FileDeletedEvent.events[event_id].remove(handler)
        del FileDeletedEvent.events[event_id]