from typing import NoReturn
from loguru import logger


def handle_exception(
    e: Exception, exc_class: type[Exception], message: str
) -> NoReturn:
    """
    Handle exceptions by logging the error and raising a custom exception.

    :param e: The original exception that was raised.
    :param exc_class: The custom exception class to raise.
    :param message: The message to log and include in the custom exception.

    :raises exc_class: The custom exception with the provided message.

    """
    logger.exception(f"[{exc_class.__name__}] {message}")
    raise exc_class(message) from e
