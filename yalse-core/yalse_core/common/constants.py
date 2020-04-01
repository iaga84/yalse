from elasticsearch import Elasticsearch
from filehash import FileHash

PUNCTUATION = r"""!"#$%&'()*+,-./'’“”—:;<=>–?«»@[\]^_`©‘…{|}~"""
DOCUMENTS_DIR = '/documents'
DOCUMENTS_INDEX = 'library'
DUPLICATES_INDEX = 'duplicates'

ES = Elasticsearch(['elasticsearch:9200'])
MD5 = FileHash('md5')
