import connexion

from yalse_core.elasticsearch.search import search_documents
from yalse_core.library.download import download_file
from yalse_core.library.reset import reset_library
from yalse_core.library.scan import scan_files


def public_files_scan_post():
    return scan_files(connexion.request.json)


def public_library_stats_get():
    pass


def public_library_search_post():
    return search_documents(connexion.request.json)


def public_file_get(file_hash):
    return download_file(file_hash)


def private_library_delete():
    return reset_library()
