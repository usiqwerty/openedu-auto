import json
import os
import re

import config
from automation.autosolver import OpenEduAutoSolver
from config import set_config
from errors import WrongAnswer, GenericOpenEduError
from images.image_describer import ImageDescriber
from openedu.course import Course
from openedu.ids import CourseID
from solvers.abstract_solver import AbstractSolver


def parse_course_by_any_link(link: str):
    uni, course, run = None, None, None
    info_r = re.search(r"https://openedu.ru/course/(\w+)/(\w+)/\?session=([\w_]+)", link)
    if info_r:
        uni, course, run = info_r.groups()
    home_r = re.search(r"https://apps.openedu.ru/learning/course/course-v1:(\w+)\+(\w+)\+([\w_]+)/home", link)
    if home_r:
        uni, course, run = home_r.groups()
    if uni is None:
        raise ValueError
    return f"{uni}+{course}+{run}"


def input_course_id():
    print("Вставьте ссылку на курс. Она может иметь следующий вид:")
    print("1) https://openedu.ru/course/urfu/HIST/?session=spring_2025")
    print("2) https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/home")
    link = input("Ссылка: ")
    return parse_course_by_any_link(link)


def get_course_id(app: OpenEduAutoSolver) -> CourseID:
    last_course = config.config.get("last-course")
    if last_course is not None:
        try:
            course = app.app.get_course_info(last_course)
            print(f"Продолжаем решать курс {course.name}?")
            continue_course = input("y/n: ") == "y"
        except GenericOpenEduError as e:
            if e.error_code == 'enrollment_required':
                continue_course = False
            else:
                raise e from None

        if continue_course:
            course_id = last_course
        else:
            course_id = input_course_id()
    else:
        course_id = input_course_id()

    set_config("last-course", str(course_id))
    return CourseID.parse(course_id)


def solve(solver: AbstractSolver, describer: ImageDescriber, course: Course):
    app = OpenEduAutoSolver(solver, describer)
    print(f"Будем решать курс {course.name}")
    if input("Нажимте Enter, чтобы начать, иначе выйдем "):
        return
    try:
        app.process_course(course.id)
    except WrongAnswer as e:
        print(f"Неправильный ответ на задачу {e.id}: {e.answer}")
        exit(1)


def get_solution_filepath(course_id):
    solutions_dir = os.path.join("userdata", "solutions")
    files = os.listdir(solutions_dir)
    solution_path = None

    for i, fn in enumerate(files):
        filepath = os.path.join(solutions_dir, fn)
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
            file_course_id = data['course']
            if CourseID.parse(file_course_id).same_course(course_id):
                solution_path = filepath
                break
    return solution_path
