from yalse_core.common.constants import DOCUMENTS_INDEX, ES


def search_documents(query):
    q = query['q']
    body = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["name^5", "content"]
            }
        },
        "size": 1000

    }
    return ES.search(body=body, index=DOCUMENTS_INDEX)
