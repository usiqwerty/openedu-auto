from images.openrouter.openrouter_describer import OpenRouterImageDescriber


class GeminiImageDescriber(OpenRouterImageDescriber):
    model = "google/gemini-2.0-flash-lite-preview-02-05:free"
