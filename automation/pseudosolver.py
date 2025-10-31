from automation.openedu_processor import OpenEduProcessor
from openedu.questions.question import Question


class OpenEduPseudoSolver(OpenEduProcessor):
    """OpenEduProcessor that solves problems"""
    require_incomplete = False
    mark_completion = False

    def process_problem(self, course_id: str, problem: list[Question]):
        pass

    def solve_by_url(self, url: str):
        pass
