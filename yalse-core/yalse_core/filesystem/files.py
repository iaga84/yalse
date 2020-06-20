import os

from yalse_core.common.constants import PUNCTUATION


def get_file_name_and_extension(path):
    base = os.path.basename(path)
    split = os.path.splitext(base)
    file_name = split[0].lower().translate(str.maketrans(PUNCTUATION, ' ' * len(PUNCTUATION))).strip()
    try:
        extension = split[1].lower().strip().replace(".", "")
    except:
        extension = "N/A"
    return file_name, extension
