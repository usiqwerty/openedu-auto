from solvers.openrouter.openrouter_solver import OpenRouterSolver


class GeminiSolver(OpenRouterSolver):
    model = "google/gemini-2.0-flash-exp:free"
    cache_fn = "gemini-cache.json"
