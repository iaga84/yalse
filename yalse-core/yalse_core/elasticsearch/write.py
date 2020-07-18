import logging
import os
from datetime import datetime
from pathlib import Path

from yalse_core.common.constants import DOCUMENTS_INDEX, ES, SHA256
from yalse_core.elasticsearch.read import document_exist, get_all_documents
from yalse_core.filesystem.files import get_file_name_and_extension
from yalse_core.tika.extractor import get_tika_content, get_tika_meta


def initialize_indexes():
    body_documents = {
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
                "path": {"type": "keyword"},
                "extension": {"type": "keyword"},
                "exists": {"type": "boolean"}
            }
        }
    }
    body_duplicates = {
        "settings": {
            "number_of_shards": 1
        },
        "mappings": {
            "_source": {
                "enabled": True
            },
            "properties": {
                "name": {"type": "text", "term_vector": "yes"},
                "hash": {"type": "keyword"},
                "path": {"type": "keyword"}
            }
        }
    }
    ES.indices.create(index=DOCUMENTS_INDEX, body=body_documents, ignore=400)


def reset_documents_index():
    ES.indices.delete(index=DOCUMENTS_INDEX, ignore=404)
    initialize_indexes()


def index_document(path):
    if not document_exist(path):
        file_hash = SHA256.hash_file(path)
        file_name, extension = get_file_name_and_extension(path)

        doc = {
            'path': path,
            'name': file_name,
            'extension': extension,
            'hash': file_hash,
            'size': os.stat(path).st_size,
            'timestamp': datetime.now(),
            'exists': True
        }
        ES.index(index=DOCUMENTS_INDEX, body=doc)


def remove_document_from_index(path):
    body = {
        "query": {
            "term": {
                "path": {
                    "value": path,
                    "boost": 1.0
                }
            }
        }
    }
    try:
        doc = ES.search(body=body, index=DOCUMENTS_INDEX)['hits']['hits'][0]
        ES.delete(id=doc['_id'], index=DOCUMENTS_INDEX)
    except:
        logging.error("Can't remove {}".format(path))


def reset_exists():
    for doc in get_all_documents():
        ES.update(index=DOCUMENTS_INDEX, id=doc['_id'], body={"doc": {"exists": False}})


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


def get_duplicate_files():
    body = {
        "size": 0,
        "aggs": {
            "duplicate_hashes": {
                "terms": {
                    "field": "hash",
                    "size": 5000,
                    "min_doc_count": 2
                }
            }
        }
    }
    hashes = ES.search(body=body, index=DOCUMENTS_INDEX)['aggregations']['duplicate_hashes']['buckets']
    result = []
    for h in hashes:
        result.append(h['key'])

    return result


def delete_document_copies(hash):
    body = {
        "query": {
            "term": {
                "hash": {
                    "value": hash,
                    "boost": 1.0
                }
            }
        }, "sort": [
            {"timestamp": {"order": "asc"}}
        ]
    }
    all_copies = ES.search(body=body, index=DOCUMENTS_INDEX)['hits']['hits']
    for copy in all_copies:
        assert Path(copy['_source']['path']).exists()
    result = []
    if len(all_copies) > 1:
        for copy in all_copies[1:]:
            path = copy['_source']['path']
            try:
                os.remove(path)
                remove_document_from_index(path)
                result.append(path)
            except:
                logging.error("Can't delete file {}".format(path))

    return result


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
