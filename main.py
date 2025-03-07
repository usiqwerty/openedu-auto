import logging

from autosolver import OpenEduAutoSolver
from solvers.mistral_solver import MistralSolver
from solvers.openrouter.gemini_solver import GeminiSolver

logging.getLogger().setLevel(logging.DEBUG)
solver = GeminiSolver()
describer = None

course_id = "spbstu+PHYLOS+spring_2024_4"
app = OpenEduAutoSolver(solver, describer)
app.solve_course(course_id)
# course_id = "urfu+HIST+spring_2025"
