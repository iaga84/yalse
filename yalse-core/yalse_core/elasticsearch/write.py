import logging
import os
from datetime import datetime

from yalse_core.common.constants import DOCUMENTS_INDEX, DUPLICATES_INDEX, ES, MD5
from yalse_core.elasticsearch.read import document_exist
from yalse_core.system.files import get_file_name_and_extension
from yalse_core.tika.extractor import get_tika_content, get_tika_meta


def initialize_indexes():
    body = {
        "settings": {
            "number_of_shards": 1
        },
        "mappings": {
            "_source": {
                "enabled": True
            },
            "properties": {
                "name": {"type": "text", "term_vector": "yes"},
                "content": {"type": "text", "term_vector": "yes"},
                "hash": {"type": "keyword"},
                "path": {"type": "keyword"}
            }
        }
    }
    ES.indices.create(index=DOCUMENTS_INDEX, body=body, ignore=400)
    ES.indices.create(index=DUPLICATES_INDEX, ignore=400)


def reset_documents_index():
    ES.indices.delete(index=DOCUMENTS_INDEX, ignore=404)
    initialize_indexes()


def reset_duplicates_index():
    ES.indices.delete(index=DUPLICATES_INDEX, ignore=404)
    initialize_indexes()


def index_document(path):
    if not document_exist(path):
        file_hash = MD5.hash_file(path)
        file_name, extension = get_file_name_and_extension(path)

        doc = {
            'path': path,
            'name': file_name,
            'extension': extension,
            'hash': file_hash,
            'size': os.stat(path).st_size,
            'timestamp': datetime.now()
        }
        ES.index(index=DOCUMENTS_INDEX, body=doc)


def index_document_metadata(id, path):
    try:
        file_meta = get_tika_meta(path)
    except:
        file_meta = {}
    ES.update(index=DOCUMENTS_INDEX, id=id, body={"doc": {"meta": file_meta}})


def index_document_content(id, path):
    try:
        file_content = get_tika_content(path)
    except:
        file_content = ""
    ES.update(index=DOCUMENTS_INDEX, id=id, body={"doc": {"content": file_content}})


def get_similar_documents(file_hash):
    body = {
        "query": {
            "term": {
                "hash": {
                    "value": file_hash,
                    "boost": 1.0
                }
            }
        }
    }
    doc = ES.search(body=body, index=DOCUMENTS_INDEX)['hits']['hits'][0]
    original_content = doc['_source']['content']
    original_name = doc['_source']['name']
    original_hash = doc['_source']['hash']
    if len(original_content) > 0:
        body = {
            "query": {
                "match": {
                    "content": {
                        "query": " ".join(sorted(original_content.split()[:500]))
                    }
                }
            },
            "sort": [
                "_score"
            ]
        }
        match = ES.search(body=body, index=DOCUMENTS_INDEX)

        score_max = match['hits']['max_score']
        score_threshold = score_max - (score_max / 100 * 5)
        results = {original_hash: original_name}
        for r in match['hits']['hits']:
            if r['_score'] > score_threshold:
                results[r['_source']['hash']] = r['_source']['name']
        if len(results) > 1:
            ES.index(index=DUPLICATES_INDEX, body=results)
