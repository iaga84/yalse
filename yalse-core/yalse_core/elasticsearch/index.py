from yalse_core.common.constants import DOCUMENTS_INDEX, ES
from yalse_core.filesystem.files import get_file_name_and_extension


def index_document(file_hash, file_path):
    if not ES.exists(index=DOCUMENTS_INDEX, id=file_hash):
        file_name, file_extension = get_file_name_and_extension(file_path)
        doc = {
            'name': file_name,
            'extension': file_extension,
        }
        ES.index(index=DOCUMENTS_INDEX, body=doc, id=file_hash)
