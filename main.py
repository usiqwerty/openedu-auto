import logging

import config
from autosolver import OpenEduAutoSolver

from images.openrouter.qwen_describer import QwenImageDescriber
from openedu.api import OpenEduAPI
from solvers.openrouter.gemini_solver import GeminiSolver


logging.getLogger().setLevel(logging.DEBUG)
solver = GeminiSolver()
describer = QwenImageDescriber()


app = OpenEduAutoSolver(solver, describer)
if not app.app.api.session.cookies:
    app.app.login(config.config["username"], config.config["password"])
    app.app.api.auth.save()

# app.solve_course('urfu+HIST+spring_2025')
app.solve_by_url('https://apps.openedu.ru/learning/course/course-v1:urfu+HIST+spring_2025/block-v1:urfu+HIST+spring_2025+type@sequential+block@f7198dd3456e4f44a5e169b6e4023d2b/block-v1:urfu+HIST+spring_2025+type@vertical+block@2e74d4a0ae194937b43819abbb359cf6')
# with app.cache_context:
#     app.app.api.auth.refresh()