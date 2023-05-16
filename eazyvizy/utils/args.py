from argparse import ArgumentParser
import json
import yaml
import os


def get_argparser():
    """Returns an ArgumentParser object to parse command line arguments.

    Returns:
      An ArgumentParser object.
    """
    parser = ArgumentParser()
    # parser.add_argument("eazyvizy_dir", type=str, nargs="?", help="Load a eazyvizy definition from eazyvizy directory.")
    # parser.add_argument(
    #     "-v",
    #     "--variable",
    #     action="append",
    #     dest="variables",
    #     metavar="NAME:VALUE",
    #     help=(
    #         "Define a variable to be used in the requests. "
    #         "To set multiple variables, use this argument multiple times"
    #     ),
    # )
    # parser.add_argument(
    #     "--no-animation", dest="animation", action="store_false", help="Disable progress animations in console output."
    # )
    # parser.add_argument("--no-colors", dest="colors", action="store_false", help="Disable colors in console output.")
    parser.add_argument("--version", action="store_true", help="Print version information.")

    return parser


# def parse_variables(raw_variables):
#     """Parses and returns a dictionary of variables from a list of raw variable strings.

#     Args:
#       raw_variables: A list of strings representing variables in the format "NAME:VALUE".

#     Returns:
#       A dictionary containing the parsed variables in the format {NAME: VALUE}.
#     Raises:
#       ValueError: If a variable string has an invalid format.
#     """
#     variables = {}

#     if not raw_variables:
#         return variables

#     for raw_variable in raw_variables:
#         try:
#             key, value = raw_variable.split(":", maxsplit=1)
#             variables[key] = value
#         except ValueError as exc:
#             raise ValueError(
#                 f'Variable definition "{raw_variable}" has invalid format. '
#                 "Variables should be defined as NAME:VALUE strings."
#             ) from exc

#     return variables
