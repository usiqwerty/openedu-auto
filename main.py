import json
import logging
import os
import re

import config
from ans_saver import AnswersSaver
from autosolver import OpenEduAutoSolver
from config import set_config
from errors import WrongAnswer
from images.openrouter.qwen_describer import QwenImageDescriber
from openedu.course import Course
from openedu.ids import CourseID
from solvers.localsolver import LocalSolver
from solvers.openrouter.gemini_solver import GeminiSolver

logging.getLogger().setLevel(logging.DEBUG)
solver = GeminiSolver()
describer = QwenImageDescriber()


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


app = OpenEduAutoSolver(solver, describer)
if not app.app.api.session.cookies:
    print("Нужно ввести данные формы, чтобы авторизоваться")
    username = input("Имя пользователя: ")
    password = input("Пароль: ")
    app.app.login(username, password)
    app.app.api.auth.save()


def get_course_id() -> CourseID:
    last_course = config.config.get("last-course")
    if last_course is not None:
        course = app.app.get_course_info(last_course)
        print(f"Продолжаем решать курс {course.name}?")
        continue_course = input("y/n: ") == "y"
        if continue_course:
            course_id = last_course
        else:
            course_id = input_course_id()
    else:
        course_id = input_course_id()

    set_config("last-course", str(course_id))
    return CourseID.parse(course_id)


def solve(course: Course):
    print(f"Будем решать курс {course.name}")
    if input("Нажимте Enter, чтобы начать, иначе выйдем "):
        return
    try:
        app.process_course(course_id)
    except WrongAnswer as e:
        print(f"Неправильный ответ на задачу {e.id}: {e.answer}")
        exit(1)


while True:
    print("1. Решить через нейросеть")
    print("2. Решить из файла")
    print("3. Сохранить решение в файл")
    print("4. Сбросить куки")
    print("5. Сбросить кеш")
    cmd = input("Ввод: ")
    if cmd == "1":
        try:
            course_id = get_course_id()
        except ValueError:
            print("Не удалось распознать ссылку")
            continue
        course = app.app.get_course_info(course_id)
        solve(course)
    elif cmd == '2':
        try:
            course_id = get_course_id()
        except ValueError:
            print("Не удалось распознать ссылку")
            continue

        solutions_dir = os.path.join("userdata", "solutions")
        files = os.listdir(solutions_dir)
        filepath = None
        for i, fn in enumerate(files):
            filepath = os.path.join(solutions_dir, fn)
            with open(filepath, encoding='utf-8') as f:
                data = json.load(f)
                file_course_id = data['course']
                if CourseID.parse(file_course_id).same_course(course_id):
                    solution_path = filepath
                    break
        if filepath is None:
            print("Не удалось найти файл с решением для этого курса")
            continue
        solver = LocalSolver(filepath)
        app = OpenEduAutoSolver(solver, describer)

        set_config("last-course", str(course_id))
        course = app.app.get_course_info(course_id)
        print(f"Будем решать курс {course.name}")
        if input("Нажимте Enter, чтобы начать, иначе выйдем "):
            break
        try:
            app.process_course(str(course_id))
        except WrongAnswer as e:
            print(f"Неправильный ответ на задачу {e.id}: {e.answer}")
            exit(1)

    elif cmd == '3':
        saver = AnswersSaver()
        try:
            course_id = input_course_id()
        except ValueError:
            print("Не удалось распознать ссылку")
            continue
        saver.pull_answers(course_id)
    elif cmd == '4':
        with app.cache_context:
            app.app.api.auth.drop()
    elif cmd == '5':
        if os.path.exists(config.cache_fn):
            os.remove(config.cache_fn)
    else:
        continue
    break
