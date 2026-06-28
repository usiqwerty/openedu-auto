from src import config
from src.solvers.abstract_solver import AbstractSolver
from src.solvers.consensus import ConsensusSolver
from src.solvers.openai_solver import GenericOpenAISolver


def pick_solver_from_config() -> AbstractSolver:
    solver: AbstractSolver
    if config.config.get('consensus-models'):
        solver = ConsensusSolver([
            GenericOpenAISolver(model=consensus_model)
            for consensus_model in config.config.get('consensus-models')
        ], negotiation="most-common")
    elif config.config.get('openai-model'):
        solver = GenericOpenAISolver()
    else:
        solver = GenericOpenAISolver(model='gpt-5-nano')
    return solver
