"""
This module contains the main entry point for the EazyVizy package.

The `main` function is responsible for parsing command line arguments,
loading a requests plan file, and running the requests specified in the
plan. If any errors occur during this process, they will be caught and
reported to the user.

The module also includes a `_print_versions` function that prints the
versions of the package's dependencies.

Functions:
  main: The main entry point for the package.
  _print_versions: Prints the versions of the package's dependencies.
"""
# pylint: disable=broad-exception-caught, redefined-builtin
from os import system
import platform
from traceback import print_exc
from .utils.args import get_argparser
from .aws import EazyVizyAWS
from ._version import __version__
from .logger import ConsoleLogger
from .error import (
    InterruptedError,
    InvalidEazyVizyError,
    EazyVizyError,
    INVALID_EAZYVIZY,
    UNKNOWN_ERROR,
    UNKNOWN_ERROR_MSG,
)


def _print_versions():
    print(f"{__version__}")


def main():
    """
    Parses command line arguments, loads a requests plan file, and runs
    the requests specified in the plan. If any errors occur during this
    process, they will be caught and reported to the user.

    Returns:
      int: The exit code for the program.
    """
    # On windows, run shell command to enable ANSI code support
    if platform.system() == "Windows":
        system("")
    args = get_argparser().parse_args()
    if args.version:
        _print_versions()
        return 0
    logger = ConsoleLogger()

    try:
        graph = EazyVizyAWS()
        graph.initialize()
        graph.generate_html()
    except EazyVizyError as error:
        logger.error(str(error))
        return error.exit_code
    except BaseException:
        logger.close()
        logger.error(UNKNOWN_ERROR_MSG)
        print_exc()
        return UNKNOWN_ERROR

