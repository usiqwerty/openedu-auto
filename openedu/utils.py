import re
import urllib

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
