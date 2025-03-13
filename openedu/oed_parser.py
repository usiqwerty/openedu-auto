from bs4 import BeautifulSoup as bs, BeautifulSoup, Tag
from pydantic import BaseModel
import logging

from errors import LayoutError, UnsupportedProblemType
from images.image_describer import ImageDescriber
from openedu.questions.choice import parse_choice_question
from openedu.questions.freematch import parse_freematch_question
from openedu.questions.match import parse_match_question
from openedu.questions.question import Question
from openedu.questions.select import parse_select_question


class VerticalBlock(BaseModel):
    id: str
    title: str
    complete: bool
    type: str


class OpenEduParser:
    describer: ImageDescriber

    def __init__(self, describer: ImageDescriber | None):
        self.describer = describer

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
            try:
                problem = self.parse_problem(task)
                total.append(problem)
            except UnsupportedProblemType as e:
                logging.error(f"Unsupported problem type: {e}")
        return total

    def parse_problem(self, problem: BeautifulSoup) -> list[Question]:
        questions = []
        mt = problem.find('div', class_='matching_table')
        map = problem.find("div", class_="historical-path-container")
        if map:
            raise UnsupportedProblemType("historical-path-container")
        # а здесь мы делаем очень смелое предположение, что если matching table есть в задаче,
        # то ничего другого там не встречается
        if mt:
            q = self.parse_question(problem)
            questions.append(q)
        else:
            wrappers = problem.find_all("div", attrs={"class": "wrapper-problem-response"})
            if len(wrappers) > 1:
                if not all(w.select("legend, p") for w in wrappers):
                    raise LayoutError("Can't parse non-separated questions")

            for question_tag in problem.find_all("div", attrs={"class": "wrapper-problem-response"}):
                q = self.parse_question(question_tag)
                questions.append(q)
        return questions

    def parse_question(self, question_tag: Tag) -> Question:
        if question_tag.select_one('div.matching_table') is not None:
            if question_tag.select_one('div.matching_table').select("td.conf-text"):
                problem_type = "match"
                question = parse_match_question(question_tag)
            else:
                problem_type = "freematch"
                question = parse_freematch_question(question_tag, self.describer)
        elif question_tag.find('select'):
            question = parse_select_question(question_tag)
        else:
            problem_type = "choice"
            question = parse_choice_question(question_tag)
        return question
