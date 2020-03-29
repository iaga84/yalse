#!/usr/bin/env python3

import json
import logging
import os
from datetime import datetime

import connexion
import requests
from elasticsearch import Elasticsearch
from filehash import FileHash
from redis import Redis
from rq import Queue

DOCUMENTS_DIR = '/documents'
DOCUMENTS_INDEX = 'test-index'
PUNCTUATION = r"""!"#$%&'()*+,-./'’“”—:;<=>–?«»@[\]^_`©‘…{|}~"""

es = Elasticsearch(['elasticsearch:9200'])
md5hasher = FileHash('md5')


def get_file_name_and_extension(path):
    base = os.path.basename(path)
    split = os.path.splitext(base)
    file_name = split[0].lower().translate(str.maketrans(PUNCTUATION, ' ' * len(PUNCTUATION))).strip()
    try:
        extension = split[1].lower().strip().replace(".", "")
    except:
        extension = "N/A"
    return file_name, extension


def get_tika_meta(path):
    headers = {'Accept': 'application/json'}
    result = json.loads(requests.put("http://tika:9998/meta", headers=headers, data=open(path, 'rb')).content)
    result.pop('X-Parsed-By', None)
    result.pop('pdf:charsPerPage', None)
    result.pop('pdf:unmappedUnicodeCharsPerPage', None)
    result.pop('access_permission:assemble_document', None)
    result.pop('access_permission:can_modify', None)
    result.pop('access_permission:can_print', None)
    result.pop('access_permission:can_print_degraded', None)
    result.pop('access_permission:extract_content', None)
    result.pop('access_permission:extract_for_accessibility', None)
    result.pop('access_permission:fill_in_form', None)
    result.pop('access_permission:modify_annotations', None)
    result.pop('pdf:encrypted', None)
    result.pop('pdf:hasMarkedContent', None)
    result.pop('pdf:hasXFA', None)
    result.pop('pdf:hasXMP', None)

    return result


def get_tika_content(path):
    r = requests.put("http://tika:9998/tika", data=open(path, 'rb')).content.decode('utf-8').lower()
    no_pun = r.translate(str.maketrans(PUNCTUATION, ' ' * len(PUNCTUATION)))
    return " ".join(sorted(set(no_pun.split())))


def search_documents(query):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^5", "content"]
            }
        }
    }
    return es.search(body=body, index='test-index')


def library_size():
    body = {
        "query": {
            "match_all": {}
        },
        "size": 0,
        "aggs": {
            "library_size": {"sum": {"field": "size"}}
        }
    }
    return es.search(body=body, index='test-index')


def index_stats():
    return es.indices.stats()


def document_exist(file_hash):
    body = {
        "query": {
            "match": {
                "hash": file_hash
            }
        }
    }
    return es.count(body=body, index='test-index')['count'] > 0


def search_duplicates():
    body = {
        "query": {
            "match": {
                "name": "quantum"
            }
        }
    }
    original = es.search(body=body, index='test-index')
    original_id = original['hits']['hits'][0]['_id']
    original_name = original['hits']['hits'][0]['_source']['name']
    original_content = original['hits']['hits'][0]['_source']['content']

    body = {
        "query": {
            "match": {
                "content": {
                    "query": original_content[0:5000]
                }
            }
        },
        "sort": [
            "_score"
        ]
    }

    match = es.search(body=body, index='test-index')

    score_max = match['hits']['max_score']
    score_threshold = score_max - (score_max / 100 * 20)
    results = {}
    for r in match['hits']['hits']:
        if r['_score'] > score_threshold:
            results[r['_id']] = [r['_source']['name'], r['_score']]
    return {"original": [original_id, original_name],
            "results": results,
            "raw": match}


def create_index():
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
                "hash": {"type": "keyword"}
            }
        }
    }
    return es.indices.create(index='test-index', body=body, ignore=400)


def index_document(path):
    file_name, extension = get_file_name_and_extension(path)
    file_hash = md5hasher.hash_file(path)

    if not document_exist(file_hash):
        doc = {
            'path': path,
            'name': file_name,
            'extension': extension,
            'hash': file_hash,
            'size': os.stat(path).st_size,
            'timestamp': datetime.now(),
            'meta': get_tika_meta(path),
            'content': get_tika_content(path)
        }
        es.index(index="test-index", body=doc)


def get_all_documents():
    q = Queue(connection=Redis('redis'))
    files = []
    for r, d, f in os.walk(DOCUMENTS_DIR):
        for file in f:
            files.append(os.path.join(r, file))

    for f in files:
        q.enqueue(index_document, str(f))
    return {'files': files}


def queue_stats():
    return requests.get('http://redis-dashboard:9181/queues.json').json()


def reset_index():
    es.indices.delete(index='test-index', ignore=400)
    result = create_index()

    return {"result": result}


logging.basicConfig(level=logging.INFO)

app = connexion.App(__name__)
app.add_api('../swagger.yml')


def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


app.app.after_request(after_request)

application = app.app
