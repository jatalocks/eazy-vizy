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
    parser.add_argument("eazyvizy_dir", type=str, nargs="?", help="Load a eazyvizy definition from eazyvizy directory.")
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


def load_eazyvizy_file(filename):
    """Loads and returns a JSON or YAML file containing a requests plan.

    Args:
      eazyvizy_ir: A string representing the eazyvizy_dir of the plan file.

    Returns:
      A dictionary containing the requests plan.
    Raises:
      ValueError: If filename is empty or if the file extension is not ".json", ".yaml", or ".yml".
    """
    if not filename:
        raise ValueError("No input file given.")

    with open(filename, "r", encoding="UTF-8") as f:
        if filename.endswith(".json"):
            plan = json.load(f)
        elif filename.endswith(".yaml") or filename.endswith(".yml"):
            plan = yaml.load(f, Loader=yaml.SafeLoader)
        else:
            raise ValueError("Failed to recognize file type. " "File extension must be json, yaml, or yml.")

    return plan


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
