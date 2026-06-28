import logging

from bs4 import BeautifulSoup as bs, BeautifulSoup, Tag
from pydantic import BaseModel

from errors import UnsupportedProblemType
from images.image_describer import ImageDescriber
from openedu.ids import VerticalBlockID, BlockID
from openedu.questions.choice import ChoiceQuestion
from openedu.questions.crossword import Crossword
from openedu.questions.fill import FillQuestion
from openedu.questions.match.freematch import FreeMatchQuestion
from openedu.questions.match.fixed_match import FixedMatchQuestion
from openedu.questions.match.new_match import NewMatchQuestion
from openedu.questions.question import Question
from openedu.questions.select import SelectQuestion
from openedu.questions.unsupported import UnsupportedQuestion


class VerticalBlock(BaseModel):
    id: VerticalBlockID
    title: str
    complete: bool
    type: str
    graded: bool


class OpenEduParser:
    describer: ImageDescriber | None

    def __init__(self, describer: ImageDescriber | None):
        self.describer = describer

    def parse_sequential_block_(self, sequential_block: dict):
        if sequential_block['is_proctored']:
            logging.info("Skipped proctoring block")
            return
        if sequential_block['gated_content']['prereq_id']:
            logging.info("Prerequisite found")
        for item in sequential_block['items']:
            title = item['page_title']
            blk_type = item['type']
            block_id = BlockID.parse(item['id'])
            graded = item['graded']
            try:  # why not get()
                complete = item['complete']
            except KeyError:
                raise Exception("Block doesn't have 'complete' field, maybe you are not authorized")
            yield VerticalBlock(id=block_id, title=title, complete=complete, type=blk_type, graded=graded)

    def parse_vertical_block_html(self, html_block: str) -> list[list[Question]]:
        soup = bs(html_block, "html.parser")
        total = []
        for ddd in soup.find_all("div", class_="problems-wrapper"):
            task_raw = str(ddd['data-content'])
            task = bs(task_raw, 'html.parser')

            problem_header_tag = task.select_one(".problem-header")
            if problem_header_tag is not None:
                problem_header = problem_header_tag.text.strip()
            else:
                problem_header = None

            problem = self.parse_problem(task, problem_header)
            total.append(problem)

        return total

    def parse_problem(self, problem: BeautifulSoup, problem_header: str | None = None) -> list[Question]:
        questions: list[Question] = []
        mt = problem.select_one('div.matching_table, div.adv-app')
        is_crossword = problem.select_one("#crossword_container")

        map = problem.find("div", class_="historical-path-container")
        if map:
            map_input = map.parent.find('input')
            questions.append(UnsupportedQuestion(id=map_input['id'], correct_answer=map_input['value'], text=''))
            return questions
            # raise UnsupportedProblemType("historical-path-container")

        if problem_header is not None and len(problem_header.strip()) > 1:
            default_prepend = [problem_header]
        else:
            default_prepend = []
        # а здесь мы делаем очень смелое предположение, что если matching table есть в задаче,
        # то ничего другого там не встречается
        if mt:
            prepend = default_prepend.copy()
            for question_tag in problem.select("div.wrapper-problem-response, .problem p, table"): #, div.matching_table
                if question_tag in mt.descendants:
                    continue
                if question_tag.name == 'p':
                    p_text = question_tag.text.strip()
                    if p_text:
                        prepend.append(p_text)
                else:
                    break
            q = self.parse_question(mt, prepend, has_mt=True)
            questions.append(q)
        elif is_crossword:
            q = Crossword.parse(problem)
            questions.append(q)
        else:
            prepend = default_prepend.copy()

            for question_tag in problem.select("div.wrapper-problem-response, .problem p"):
                if question_tag.name == 'div':
                    q = self.parse_question(question_tag, prepend)
                    questions.append(q)
                    prepend = default_prepend.copy()
                elif question_tag.name == 'p':
                    p_text = question_tag.text.strip()
                    if p_text:
                        prepend.append(p_text)

        return questions

    def parse_question(self, question_tag: Tag, prepend_lines: list[str] | None = None, has_mt=False) -> Question:
        if has_mt: #question_tag.select_one('div.matching_table, div.adv-app') is not None
            if "adv-app" in question_tag.get('class', ""):
                return NewMatchQuestion.parse(question_tag, prepend_lines)
            elif "matching_table" in question_tag.get('class', "") and question_tag.select("td.conf-text"):
                return FixedMatchQuestion.parse(question_tag, prepend_lines)
            else:
                return FreeMatchQuestion.parse(question_tag, prepend_lines, self.describer)
        elif question_tag.find('select'):
            return SelectQuestion.parse(question_tag, prepend_lines)
        elif question_tag.select_one('input[type=text]'):
            return FillQuestion.parse(question_tag, prepend_lines)
        elif question_tag.select_one('input.input-radio, input.input-checkbox'):
            return ChoiceQuestion.parse(question_tag, prepend_lines)
        else:
            raise UnsupportedProblemType
