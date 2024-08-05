from flask import Blueprint, request
import utils.message_logging as ml
import file_handling as fh
import tagging.tagging_interface as tag_interface

upload_interface_blueprint = Blueprint('upload_interface', __name__)
fh.subscribe_to_deletion_event('tag_removal', tag_interface.On_File_Deletion)

@upload_interface_blueprint.route('/upload', methods=['POST'])
def upload():
    logger = ml.MessageLogger()
    handlers = fh.upload_files(request.files.getlist('files'), request.form.getlist('modifieds'), logger)
    
    for handler in handlers:
        tag_interface.tag_new_upload(handler, logger)
    
    return logger.get_message()

@upload_interface_blueprint.route('/delete', methods=['POST'])
def delete():
    file_name = request.data.decode('utf-8')
    
    f_handler = fh.get_handler(file_name)
    if isinstance(f_handler, fh.FileHandler):
        fh.delete_file(f_handler.id)
        return 'deleted'

    print(f'File {file_name} not found')

    return 'no file'
