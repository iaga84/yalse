import os

import requests
from flask import send_file
from redis import Redis
from rq import Queue
from yalse_core.common.constants import DOCUMENTS_DIR
from yalse_core.elasticsearch.read import (get_all_documents, get_all_missing_documents, get_document,
                                           get_stats_extensions, get_stats_extensions_size,
                                           index_stats, library_size, search_documents,)
from yalse_core.elasticsearch.write import (delete_document_copies, get_duplicate_files, get_similar_documents,
                                            index_document, index_document_content, index_document_metadata,
                                            initialize_indexes, remove_document_from_index,
                                            reset_documents_index, reset_duplicates_index, reset_exists,)
from yalse_core.persistence.records import create_file, get_all_files


def scan_library():
    initialize_indexes()
    reset_exists()
    q = Queue(connection=Redis('redis'))
    files = []
    for r, d, f in os.walk(DOCUMENTS_DIR):
        for file in f:
            files.append(os.path.join(r, file))

    for f in files:
        q.enqueue(index_document, str(f), job_timeout=1200)
    return {'message': "scan in progress"}


def scan_library_metadata():
    q = Queue(connection=Redis('redis'))

    for entry in get_all_documents():
        q.enqueue(index_document_metadata, entry['_id'], entry['_source']['path'])

    return {'message': 'scan in progress'}


def scan_library_content():
    q = Queue(connection=Redis('redis'))

    for entry in get_all_documents():
        q.enqueue(index_document_content, entry['_id'], entry['_source']['path'])

    return {'message': 'scan in progress'}


def delete_duplicate_files():
    result = []
    hashes = get_duplicate_files()
    for h in hashes:
        result.append(delete_document_copies(h))

    return {'deleted': result}


def delete_missing_documents():
    removed = []
    for doc in get_all_missing_documents():
        if not doc['_source']['exists']:
            remove_document_from_index(doc['_source']['path'])
            removed.append(doc['_source']['path'])
    return removed


def find_duplicates():
    reset_duplicates_index()

    q = Queue(connection=Redis('redis'))

    for entry in get_all_documents():
        q.enqueue(get_similar_documents, entry['_source']['hash'])

    return {'message': 'scan in progress'}


def reset_library():
    reset_documents_index()


def search(query):
    return search_documents(query)


def download(id):
    return send_file(get_document(id)['_source']['path'], as_attachment=True)


def get_queue_stats():
    return requests.get('http://redis-dashboard:9181/queues.json').json()


def get_workers_stats():
    return requests.get('http://redis-dashboard:9181/workers.json').json()


def get_library_stats():
    return index_stats()


def get_library_stats_extensions():
    return get_stats_extensions()


def get_library_stats_extensions_size():
    return get_stats_extensions_size()


def get_library_size():
    return library_size()


def create_database():
    create_file('aaaa1111')


def get_database_records():
    return get_all_files()
