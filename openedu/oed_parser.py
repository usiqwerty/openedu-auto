from bs4 import BeautifulSoup as bs, BeautifulSoup, Tag
from pydantic import BaseModel

from openedu.questions.choice import parse_choice_problem
from openedu.questions.freematch import parse_freematch_problem
from openedu.questions.match import parse_match_problem
from openedu.questions.question import Question
from openedu.questions.select import SelectQuestion, parse_select_question


class VerticalBlock(BaseModel):
    id: str
    title: str
    complete: bool
    type: str


class OpenEduParser:
    def parse_sequential_block_(self, sequential_block: dict):
        for item in sequential_block['items']:
            title = item['page_title']
            blk_type = item['type']
            block_id = item['id']
            try:
                complete = item['complete']
            except KeyError:
                raise Exception("Block doesn't have 'complete' field, maybe you are not authorized")
            yield VerticalBlock(id=block_id, title=title, complete=complete, type=blk_type)

    def parse_vertical_block_html(self, html_block: str) -> list[list[Question]]:
        soup = bs(html_block, "html.parser")
        total = []
        for ddd in soup.find_all("div", class_="problems-wrapper"):
            task_raw = str(ddd['data-content'])
            task = bs(task_raw, 'html.parser')
            problem = parse_problem(task)
            total.append(problem)

        return total


def parse_question(question_tag: Tag) -> Question:
    if question_tag.select_one('div.matching_table') is not None:
        if question_tag.select_one('div.matching_table').select("td.conf-text"):
            problem_type = "match"
            question = parse_match_problem(question_tag)
        else:
            problem_type = "freematch"
            question = parse_freematch_problem(question_tag)
    elif question_tag.find('select'):
        question = parse_select_question(question_tag)
    else:
        problem_type = "choice"
        question = parse_choice_problem(question_tag)
    return question


def parse_problem(problem: BeautifulSoup) -> list[Question]:
    questions = []
    mt = problem.find('div', class_='matching_table')
    # а здесь мы делаем очень смелое предположение, что если matching table есть в задаче,
    # то ничего другого там не встречается
    if mt:
        q = parse_question(problem)
        questions.append(q)
    else:
        for question_tag in problem.find_all("div", attrs={"class": "wrapper-problem-response"}):
            q = parse_question(question_tag)
            questions.append(q)
    return questions
