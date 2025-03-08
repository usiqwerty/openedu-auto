import logging

from autosolver import OpenEduAutoSolver

from images.openrouter.qwen_describer import QwenImageDescriber
from solvers.openrouter.gemini_solver import GeminiSolver


logging.getLogger().setLevel(logging.DEBUG)
solver = GeminiSolver()
describer = QwenImageDescriber()

url = 'https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/block-v1:urfu+HIST+spring_2025+type@sequential+block@5c28e0b90c5945f2ba60985a646da113/block-v1:urfu+HIST+spring_2025+type@vertical+block@35f476ee43964e95a5a805a8be8845c4'
app = OpenEduAutoSolver(solver, describer)
app.solve_course(url)
