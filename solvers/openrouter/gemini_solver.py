from solvers.openrouter.openrouter_solver import OpenRouterSolver


class GeminiSolver(OpenRouterSolver):
    model = "google/gemini-2.0-flash-lite-preview-02-05:free"
    cache_fn = "gemini-cache.json"
