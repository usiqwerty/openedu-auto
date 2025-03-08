import re
import urllib

from errors import FormatError
from openedu.ids import SequentialBlockID, VerticalBlockID


def parse_page_url(url: str):
    parsed_url = urllib.parse.urlparse(url)
    url_path = parsed_url.path.split('/')
    assert url_path[0] == ''
    assert url_path[1] == 'learning'
    assert url_path[2] == 'course'

    course_id = re.search(r"course-v1:([\w+_]+)", url_path[3]).group(1)
    seq_block_id = SequentialBlockID.parse(url_path[4])
    vert_block_id = VerticalBlockID.parse(url_path[5])
    return course_id, seq_block_id, vert_block_id


def ensure_ids_same(ids, selector=lambda x: x):
    prev = None
    for input_id in map(selector, ids):
        r = re.search(r"input_([\w\d]+)_\d+_\d+", input_id)
        if not r:
            raise ValueError(f"Not a valid input id: {input_id}")
        id_ = r.groups(1)
        if prev is None:
            prev = id_
        else:
            if id_ != prev:
                raise FormatError(f"IDs differ: {ids}")
