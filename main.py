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
    # app.app.api.auth.refresh()
    app.app.login(config.config["username"], config.config["password"])
    app.app.api.auth.save()

app.solve_course('urfu+HIST+spring_2025')
# with app.cache_context:
#     app.app.api.auth.refresh()