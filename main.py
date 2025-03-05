import logging
import time

from cached_requests import CacheContext
from openedu.oed_parser import VerticalBlock
from openedu.openedu import OpenEdu
from solvers.mistral_solver import MistralSolver

logging.getLogger().setLevel(logging.DEBUG)


def solve_block(api: OpenEdu, blkid: str, block: VerticalBlock):
    logging.debug(blkid)
    logging.debug(f"Block '{block.title}' (complete={block.complete}) of type '{block.type}'")
    if block.type == 'other':
        print(blkid, block)
        api.tick_page(blkid)
        time.sleep(5)
        api.publish_completion(blkid)
    elif block.type == "problem":
        for problem in api.get_problems(blkid):
            for question in problem:
                print(question.query())
                continue
                try:
                    answers = {}
                    k, v = solver.solve(question)
                    answers[k] = v
                    quest_id = api.extract_quest_id(k)
                    new_block_id = f"block-v1:{course_id}+type@problem+block@{quest_id}"

                    got, total = api.problem_check(new_block_id, answers)
                    logging.info(f"Solved ({got}/{total})")
                    if got < total:
                        logging.critical("Wrong answer!")
                        exit(1)
                except KeyError as e:
                    print("Error:", e)
        return


def main():
    solver = MistralSolver()
    ("https://apps.openedu.ru/learning/course/"
     "course-v1:spbstu+PHYLOS+spring_2024_4/"
     "block-v1:spbstu+PHYLOS+spring_2024_4+type@sequential+block@db110fe478f0461e85e7ecba2f02293f"
     "/block-v1:spbstu+PHYLOS+spring_2024_4+type@vertical+block@339323acbef2401caa352bcf502187c2")
    # ("https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/"
    #  "block-v1:urfu+HIST+spring_2025+type@sequential+block@55b86722df2445dd958566d725199d00/block-v1:urfu+HIST+spring_2025+type@vertical+block@ee4bd86f2fb0493cae7f326685469638")
    # course_id = "urfu+HIST+spring_2025"
    course_id = "spbstu+PHYLOS+spring_2024_4"
    block_id = "db110fe478f0461e85e7ecba2f02293f"
    # block_id = "55b86722df2445dd958566d725199d00"
    # block_id = "38b80605065a407499e4928b053df9f2"
    # block_id = "5c28e0b90c5945f2ba60985a646da113"
    logging.debug(f"Course: {course_id}")
    logging.debug(f"Starting at block {block_id}")
    url = (f"https://courses.openedu.ru/api/courseware/sequence/"
           f"block-v1:{course_id}+type@sequential"
           f"+block@{block_id}")

    api = OpenEdu(course_id)
    api.parse_and_save_sequential_block(url)

    for blkid, block in api.iterate_incomplete_blocks():
        solve_block(api, blkid, block)


with CacheContext():
    main()
# publish_completion("zsd")
# save_cache()
# save_blocks()
