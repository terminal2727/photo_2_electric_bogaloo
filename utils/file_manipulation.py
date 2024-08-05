from database.file_handling import FileHandler
import os

def get_file_blob(file):
    if isinstance(file, FileHandler):
        _, ext = os.path.splitext(file.file_path)
    elif isinstance(file, str):
        _, ext = os.path.splitext(file)
    else:
        raise ValueError('file must be a FileHandler or a string')
    
    if ext.lower() in ['.png', '.jpg', '.jpeg']:
        mime_type = f'image/{ext[1:].lower()}'
    elif ext.lower() in ['.gif', '.webp']:
        mime_type = f'image/{ext[1:].lower()}'
    elif ext.lower() in ['.mov', '.avi', '.mp4']:
        mime_type = f'video/{ext[1:].lower()}'
    
    return {
        'filename': file,
        'mimetype': mime_type
    }
    
def remove_line_from_file(line, file_path : str):    
    if not os.path.exists(file_path):
        print (f'File {file_path} does not exist')
        return
    
    l = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line != l:
                l.append(line)
    
    with open(file_path, 'w') as f:
        for line in l:
            f.write(line)