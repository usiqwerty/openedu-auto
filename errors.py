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


class HashMismatch(Exception):
    pass


class Unauthorized(Exception):
    pass


class GenericOpenEduError(Exception):
    error_code: str
    message: str

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message


class ReloginReceived(Exception):
    pass
