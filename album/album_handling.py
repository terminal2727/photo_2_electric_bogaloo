import os

ALBUM_DIR = 'albums'

#TODO: add upload deletion event
#TODO: add album deletion event

def create_album(name, files):
    if not os.path.exists(ALBUM_DIR):
        os.makedirs(ALBUM_DIR)
    
    if os.path.exists(f'{ALBUM_DIR}/{name}.txt'):
        print(f'Album: {name} already exists')
        return
    
    with open(f'{ALBUM_DIR}/{name}.txt', 'w') as f:
        for file in files:
            f.write(f'{file}\n')

def add_files_to_album(name, files):
    if not os.path.exists(ALBUM_DIR):
        os.makedirs(ALBUM_DIR)
    
    if not os.path.exists(f'{ALBUM_DIR}/{name}.txt'):
        print(f'Album: {name} does not exist')
        return
    
    with open(f'{ALBUM_DIR}/{name}.txt', 'a') as f:
        for file in files:
            f.write(f'{file}\n')

def remove_files_from_album(name, files):
    if not os.path.exists(ALBUM_DIR):
        os.makedirs(ALBUM_DIR)
        
    if not os.path.exists(f'{ALBUM_DIR}/{name}.txt'):
        print(f'Album: {name} does not exist')
        return
    
    lines = []
    with open(f'{ALBUM_DIR}/{name}.txt', 'r') as f:
        lines = f.readlines()
    
    with open(f'{ALBUM_DIR}/{name}.txt', 'w') as f:
        for line in lines:
            if line not in files:
                f.write(line)

def delete_album(name):
    os.move(f'{ALBUM_DIR}/{name}.txt', f'{ALBUM_DIR}/deleted/{name}.txt')