import json
from string import digits

import requests
from unidecode import unidecode
from yalse_core.common.constants import PUNCTUATION


def get_tika_content(path):
    r = unidecode(requests.put("http://tika:9998/tika", data=open(path, 'rb')).content.decode('utf-8')).lower()
    no_digit = r.translate(str.maketrans('', '', digits))
    no_pun = no_digit.translate(str.maketrans(PUNCTUATION, ' ' * len(PUNCTUATION)))
    return " ".join(sorted(set(no_pun.split())))


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
