# Описание кода

## Класс OpenEdu

Это - класс, через который должно происходить взаимодействие с OpenEdu.
Внутри он делает вызовы API и работает с кэшем.

| Метод                     | Аргументы                                         | Значение                | Описание                             | 
|---------------------------|---------------------------------------------------|-------------------------|--------------------------------------| 
| get_sequential_block      | course_id: str, block_id: str                     | Iterable[VerticalBlock] | Получить sequential блок             |
| is_block_solved           | block_id: str                                     | bool                    | Проверить, решён ли блок             |
| mark_block_as_completed   | block_id: str                                     | None                    | Отметить блок как пройденный         |
| get_problems_for_vertical | block_id: str                                     | list[list[Question]]    | Получить задачи на странице          |
| login                     | username: str, password: str                      | {'auth': 1}             | Авторизоваться на сайте              |
| logout                    |                                                   | None                    | Сбросить авторизацию                 |
| get_course_info           | course_id: CourseID                               |                         | Получить информацию о курсе          |
| get_vertical_block        | block_id: str                                     | VerticalBlock           | Получить vertical блок               |
| skip_forever              | block_id: str                                     | None                    | Игнорировать блок                    |
| save                      |                                                   | None                    | Сохранить всё                        |
| get_vertical_page_html    | block_id: str                                     | str                     | Получить HTML страницу               |
| publish_completion        | course_id: str, block_id_str: str                 | None                    | Пометить блок как просмотренный      |
| submit_answers            | course_id: str, blk: str, answers: dict[str, str] | tuple                   | Отправить ответы                     |
| inject_csrf               | csrftoken: str                                    | tuple                   | Установить значение куки `csrftoken` |

## Класс OpenEduProcessor
Построен поверх `OpenEdu`.

Автоматизирует работу с курсом, то есть позволяет выполнять операции над каждым заданием каждой темы.

Запускается через метод `process_course(course_id: str)`.
Тот перебирает все части (chapter) и sequential блоки, для каждого вертикального блока запуская `process_vertical`.

И дальше для каждой задачи срабатывает абстрактный метод **process_problem** - он принимает вопросы из задачи и выполняет над ними действия.
Например, `OpeEduAutoSolver` решает задачи и отправляет ответы, а `AnswersSaver` сохраняет уже имеющиеся ответы.

