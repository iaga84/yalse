from yalse_core.common.constants import DOCUMENTS_INDEX, ES


def initialize_index():
    body_documents = {
        "settings": {
            "number_of_shards": 5
        },
        "mappings": {
            "_source": {
                "enabled": True
            },
            "properties": {
                "name": {"type": "text", "term_vector": "yes"},
                "content": {"type": "text", "term_vector": "yes"},
                "extension": {"type": "keyword"},
            }
        }
    }
    ES.indices.create(index=DOCUMENTS_INDEX, body=body_documents, ignore=400)


def reset_index():
    ES.indices.delete(index=DOCUMENTS_INDEX, ignore=404)
    initialize_index()
