from src.automation.openedu_processor import OpenEduProcessor
from src.openedu.ids import CourseID
from src.openedu.questions.question import Question


class OpenEduPseudoSolver(OpenEduProcessor):
    """OpenEduProcessor that solves problems"""
    require_incomplete = False
    mark_completion = False

    def process_problem(self, course_id: CourseID, problem: list[Question], *, process_solved):
        pass

    def solve_by_url(self, url: str):
        pass
