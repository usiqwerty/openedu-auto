class FormatError(Exception):
    pass


class NoSolutionFoundError(Exception):
    pass


class UnsupportedProblemType(Exception):
    pass


class LayoutError(Exception):
    pass


class WrongAnswer(Exception):
    def __init__(self, prob_id: str, ans):
        self.id = prob_id
        self.answer = ans


class ConfigError(Exception):
    pass
