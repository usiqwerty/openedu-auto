import logging
import re
import time
import traceback
import urllib

from cached_requests import CacheContext
from images.image_describer import ImageDescriber
from openedu.oed_parser import VerticalBlock
from openedu.openedu import OpenEdu
from solvers.abstract_solver import AbstractSolver



def parse_page_url(url: str):
    parsed_url = urllib.parse.urlparse(url)
    url_path = parsed_url.path.split('/')
    assert url_path[0] == ''
    assert url_path[1] == 'learning'
    assert url_path[2] == 'course'

    course_id = re.search(r"course-v1:([\w+_]+)", url_path[3]).group(1)
    seq_block_id = re.search(r"block-v1:[\w+_]+\+type@sequential\+block@([\w\W]+)", url_path[4]).group(1)
    vert_block_id = re.search(r"block-v1:[\w+_]+\+type@vertical\+block@([\w\W]+)", url_path[5]).group(1)

    return course_id, seq_block_id, vert_block_id

class OpenEduAutoSolver:
    solver: AbstractSolver
    describer: ImageDescriber

    def __init__(self, solver: AbstractSolver, describer: ImageDescriber):
        self.solver = solver
        self.describer = describer

    def solve_course(self, url: str):
        course_id, seq, ver = parse_page_url(url)
        # block_id = "db110fe478f0461e85e7ecba2f02293f"

        logging.debug(f"Course: {course_id}")
        logging.debug(f"Starting at block {seq}")
        url = (f"https://courses.openedu.ru/api/courseware/sequence/"
               f"block-v1:{course_id}+type@sequential"
               f"+block@{seq}")

        with CacheContext():
            api = OpenEdu(course_id)
            api.parse_and_save_sequential_block(url)

            for blkid, block in api.iterate_incomplete_blocks():
                self.solve_block(api, blkid, block, course_id)

    def solve_block(self, api: OpenEdu, blkid: str, block: VerticalBlock, course_id: str):
        logging.debug(blkid)
        logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")
        if block.type == 'other':
            return
            print(blkid, block)
            api.tick_page(blkid)
            time.sleep(5)
            api.publish_completion(blkid)
        elif block.type == "problem":
            for problem in api.get_problems(blkid, self.describer):
                answers = {}
                for question in problem:
                    # print(question.query())
                    try:
                        input_id, input_value = self.solver.solve(question)
                        answers[input_id] = input_value
                    except KeyError as e:
                        print("Error:", e)
                        traceback.print_exc()
                        exit(1)
                quest_id = api.extract_quest_id(input_id)
                print(f"{answers=}")
                new_block_id = f"block-v1:{course_id}+type@problem+block@{quest_id}"
                got, total = api.problem_check(new_block_id, answers)
                logging.info(f"Solved ({got}/{total})")
                if got < total:
                    logging.critical("Wrong answer!")
                    exit(1)
            return
