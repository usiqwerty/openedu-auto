import logging
import sys
from types import TracebackType


def handle_exception(exc_type: type[BaseException], exception: BaseException, tb: TracebackType | None):
    if isinstance(exception, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exception, tb)
        logging.debug("Keyboard interrupt")
        return
    logging.critical("Unhandled exception", exc_info=(exc_type, exception, tb))


def setup_logging():
    logging.getLogger().setLevel(logging.DEBUG)

    simple_formatter = logging.Formatter(fmt="{levelname}: {message}", style='{')
    named_formatter = logging.Formatter(fmt="{levelname} ({name}): {message}", style='{')

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(simple_formatter)

    file_handler = logging.FileHandler(filename="userdata/last.log", mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(named_formatter)

    logging.getLogger().addHandler(console_handler)
    logging.getLogger().addHandler(file_handler)

    sys.excepthook = handle_exception
