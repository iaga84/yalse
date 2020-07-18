from elasticsearch import Elasticsearch
from filehash import FileHash

PUNCTUATION = r"""!"#$%&'()*+,-./'’“”—:;<=>–?«»@[\]^_`©‘…{|}~"""
DOCUMENTS_DIR = '/documents'
DOCUMENTS_INDEX = 'library'

ES = Elasticsearch(['elasticsearch:9200'])
SHA256 = FileHash('sha256')
