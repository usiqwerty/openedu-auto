import logging
import re

import config
from ans_saver import AnswersSaver
from autosolver import OpenEduAutoSolver
from config import set_config
from errors import WrongAnswer
from images.openrouter.qwen_describer import QwenImageDescriber
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

while True:
    print("1. Решить через нейросеть")
    print("2. Решить из файла")
    print("3. Сохранить решение в файл")
    cmd = input("Ввод: ")
    if cmd == "1":
        last_course = config.config.get("last-course")

        if last_course is not None:
            course = app.app.get_course_info(last_course)
            print(f"Продолжаем решать курс {course.name}?")
            continue_course = input("y/n: ") == "y"
            if continue_course:
                course_id = last_course
            else:
                last_course = None
        if last_course is None:
            try:
                course_id = input_course_id()
            except ValueError:
                print("Не удалось распознать ссылку")
                continue

        set_config("last-course", course_id)
        course = app.app.get_course_info(course_id)
        print(f"Будем решать курс {course.name}")
        if input("Нажимте Enter, чтобы начать, иначе выйдем "):
            break
        try:
            app.process_course(course_id)
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
    else:
        continue
    break
