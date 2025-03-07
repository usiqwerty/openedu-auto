import logging
import re
import urllib.parse

from autosolver import OpenEduAutoSolver
from images.openrouter.gemini_describer import GeminiImageDescriber
from solvers.openrouter.gemini_solver import GeminiSolver


logging.getLogger().setLevel(logging.DEBUG)
solver = GeminiSolver()
describer = GeminiImageDescriber()

url = 'https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/block-v1:urfu+HIST+spring_2025+type@sequential+block@55b86722df2445dd958566d725199d00/block-v1:urfu+HIST+spring_2025+type@vertical+block@ee4bd86f2fb0493cae7f326685469638'
app = OpenEduAutoSolver(solver, describer)
app.solve_course(url)
