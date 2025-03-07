from images.openrouter.openrouter_describer import OpenRouterImageDescriber


class QwenImageDescriber(OpenRouterImageDescriber):
    model = "qwen/qwen-vl-plus:free"
