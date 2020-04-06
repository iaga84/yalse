import os

import requests
from redis import Redis
from rq import Queue
from yalse_core.common.constants import DOCUMENTS_DIR
from yalse_core.elasticsearch.read import get_all_documents, index_stats, library_size, search_documents, get_stats_extensions, get_stats_extensions_size
from yalse_core.elasticsearch.write import (get_similar_documents, index_document, initialize_indexes,
                                            reset_documents_index, reset_duplicates_index, index_document_metadata, index_document_content)


def scan_library():
    initialize_indexes()

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
