import logging

from yalse_core.common.constants import DOCUMENTS_INDEX, ES


def search_documents(query):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name^5", "content"]
            }
        }
    }
    return ES.search(body=body, index=DOCUMENTS_INDEX)


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
    return ES.search(body=body, index=DOCUMENTS_INDEX)


def index_stats():
    return ES.indices.stats()


def document_exist(path):
    body = {
        "query": {
            "match": {
                "path": path
            }
        }
    }
    r = ES.search(body=body, index=DOCUMENTS_INDEX)
    return r['hits']['total']['value'] > 0


def get_all_documents(pagesize=250, scroll_timeout="2m", **kwargs):
    is_first = True
    while True:
        if is_first:  # Initialize scroll
            result = ES.search(index=DOCUMENTS_INDEX, scroll=scroll_timeout, **kwargs, body={
                "size": pagesize
            })
            is_first = False
        else:
            result = ES.scroll(body={
                "scroll_id": scroll_id,
                "scroll": scroll_timeout
            })
        scroll_id = result["_scroll_id"]
        hits = result["hits"]["hits"]
        if not hits:
            break
        yield from (hit for hit in hits)


def get_stats_extensions():
    body = {
        "aggs": {
            "extensions": {
                "terms": {
                    "field": "extension",
                    "size": 1000
                }
            }
        },
        "size": 0
    }
    return ES.search(body=body, index=DOCUMENTS_INDEX)


def get_stats_extensions_size():
    body = {
        "size": 0,
        "aggs": {
            "extensions": {
                "terms": {
                    "field": "extension",
                    "size": 1000
                },
                "aggs": {
                    "size": {
                        "sum": {
                            "field": "size"
                        }
                    }
                }
            }
        }
    }
    return ES.search(body=body, index=DOCUMENTS_INDEX)
