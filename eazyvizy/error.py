"""
A package for making HTTP requests from YAML files.

The package provides an interface for defining HTTP requests in YAML files
and making those requests with Python. The package raises several custom
exceptions, including:

- NoEazyVizyError: raised when no requests eazyvizy file is provided.
- InvalidEazyVizyError: raised when a requests eazyvizy file is invalid.
- InterruptedError: raised when the user interrupts the program.

The package defines several constants:

- NO_EAZYVIZY: exit code indicating that no requests eazyvizy file was provided.
- INVALID_EAZYVIZY: exit code indicating that a requests eazyvizy file was invalid.
- INTERRUPTED: exit code indicating that the user interrupted the program.
- UNKNOWN_ERROR: exit code indicating an unexpected error occurred.

If an unexpected error occurs, the package will catch the error and display
a message instructing the user to create a bug report on the package's GitHub
repository.
"""
# pylint: disable=redefined-builtin
NO_EAZYVIZY = 251
NO_SCRIPT = 252
INVALID_EAZYVIZY = 253
INTERRUPTED = 254
UNKNOWN_ERROR = 255


UNKNOWN_ERROR_MSG = (
    "Caught unexpected error, see traceback and description below. "
    "If this seems like a bug to you, please consider creating a issue in "
    "https://github.com/jatalocks/eazyvizy/issues.\n"
)


class EazyVizyError(Exception):
    """
    Base class for exceptions raised by the EazyVizy package.

    Args:
      message (str): A message describing the error.
      exit_code (int): An exit code indicating the type of error.
    """

    def __init__(self, message, exit_code):
        super().__init__(message)
        self.exit_code = exit_code


class NoEazyVizyError(EazyVizyError):
    """
    Exception raised when no requests eazyvizy file is provided.

    Args:
      path (str, optional): The path to the missing eazyvizy file.
    """

    def __init__(self, path=None):
        if not path:
            super().__init__("No requests eazyvizy file provided.", NO_EAZYVIZY)
        else:
            super().__init__(f"Did not find eazyvizy file in {path}.", NO_EAZYVIZY)


class NoScriptError(EazyVizyError):
    """
    Exception raised when no requests eazyvizy file is provided.

    Args:
      path (str, optional): The path to the missing eazyvizy file.
    """

    def __init__(self, path=None):
        if not path:
            super().__init__("No script file provided.", NO_SCRIPT)
        else:
            super().__init__(f"Did not find script file in {path}.", NO_SCRIPT)


class InvalidEazyVizyError(EazyVizyError):
    """
    Exception raised when a requests eazyvizy file is invalid.

    Args:
      message (str): A message describing the error.
    """

    def __init__(self, message):
        super().__init__(message, INVALID_EAZYVIZY)


class InterruptedError(EazyVizyError):
    """
    Exception raised when the user interrupts the program.

    Args:
      None
    """

    def __init__(self):
        super().__init__("", INTERRUPTED)
