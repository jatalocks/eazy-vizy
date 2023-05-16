"""
This module contains classes to represent templates and their parameters,
and provides methods to create instances of these classes from dictionaries.

Classes:

Parameter: A class representing a parameter.
EazyVizy: A class representing a template.
"""

import os
import importlib

class Parameter:
    """
    A class representing a parameter.

    Attributes:
        name (str): The name of the parameter.
        type (str): The type of the parameter. Can be "text", "number", "single-choice", or "multi-choice".
        default (any): The default value for the parameter.
        choices (list of any): A list of choices for the parameter
            (only used for "single-choice" and "multi-choice" types).
    """

    def __init__(self, name, param_type, default=None, choices=None):
        """
        Initializes a new instance of the Parameter class.

        Args:
            name (str): The name of the parameter.
            param_type (str): The type of the parameter. Can be "text", "number", "single-choice", or "multi-choice".
            default (any): The default value for the parameter.
            choices (list of any): A list of choices for the parameter
                (only used for "single-choice" and "multi-choice" types).
        """
        self.name = name
        self.type = param_type
        self.default = default
        self.choices = choices

    @classmethod
    def from_text(cls, name, default=""):
        """
        Creates a new instance of the Parameter class with type "text".

        Args:
            name (str): The name of the parameter.
            default (str, optional): The default value for the parameter.

        Returns:
            Parameter: A new instance of the Parameter class.
        """
        return cls(name, "text", default=default)

    @classmethod
    def from_number(cls, name, default=0):
        """
        Creates a new instance of the Parameter class with type "number".

        Args:
            name (str): The name of the parameter.
            default (int or float, optional): The default value for the parameter.

        Returns:
            Parameter: A new instance of the Parameter class.
        """
        return cls(name, "number", default=default)

    @classmethod
    def from_single_choice(cls, name, default=None, choices=None):
        """
        Creates a new instance of the Parameter class with type "single-choice".

        Args:
            name (str): The name of the parameter.
            default (any, optional): The default value for the parameter.
            choices (list of any): A list of choices for the parameter.

        Returns:
            Parameter: A new instance of the Parameter class.
        """
        if not choices:
            raise ValueError("Single choice parameter must have choices.")
        if default and default not in choices:
            raise ValueError("Single choice parameter default must be one of the choices.")
        return cls(name, "single-choice", default=default, choices=choices)

    @classmethod
    def from_multi_choice(cls, name, default=None, choices=None):
        """
        Creates a new instance of the Parameter class with type "multi-choice".

        Args:
            name (str): The name of the parameter.
            default (list of any, optional): The default value for the parameter.
            choices (list of any): A list of choices for the parameter.

        Returns:
            Parameter: A new instance of the Parameter class.
        """
        if not choices:
            raise ValueError("Multi choice parameter must have choices.")
        if default and not all(item in choices for item in default):
            raise ValueError("Multi choice parameter default must be a subset of the choices.")
        return cls(name, "multi-choice", default=default, choices=choices)

    @classmethod
    def from_dict(cls, param_dict):
        """
        Creates a Parameter object from a dictionary.

        Args:
            param_dict (dict): A dictionary representing the parameter.

        Returns:
            Parameter: A Parameter object created from the dictionary.

        Raises:
            ValueError: If the parameter type is not valid.
        """
        param_type = param_dict.get("type")
        name = param_dict.get("name")
        default = param_dict.get("default")
        choices = param_dict.get("choices")

        if param_type == "text":
            return cls.from_text(name, default=default)
        if param_type == "number":
            return cls.from_number(name, default=default)
        if param_type == "single-choice":
            return cls.from_single_choice(name, default=default, choices=choices)
        if param_type == "multi-choice":
            return cls.from_multi_choice(name, default=default, choices=choices)
        raise ValueError(f"Invalid parameter type: {param_type}")

def list_functions(mod):
    ' list of functions defined in module mod '
    return [func.__name__ for func in mod.__dict__.values()
            if is_mod_function(mod, func)]
class EazyVizy:
    """
    A class that represents a template.

    Attributes:
        name (str): The name of the template.
        template (str): The path to the Jinja2 template file.
        script (str): The path to the script file that will be executed with the rendered template.
        markdown (str): The path to the README file.
        parameters (list): A list of Parameter objects that represent the input parameters of the template.

    Raises:
        AssertionError: If the template name is missing, or if the Jinja2 or script file cannot be found.
    """

    def __init__(self, template_dict, template_file):
        self.name = template_dict.get("name")
        self.template = os.path.join(os.path.dirname(template_file), "templates", "index.html")
        code = os.path.join(os.path.dirname(template_file), "code")
        markdown_file = os.path.join(os.path.dirname(template_file), "README.md")
        if os.path.isfile(markdown_file):
            with open(markdown_file, 'r', encoding='UTF-8') as file:
                self.markdown = file.read()
        else:
            self.markdown = ""
        self.parameters = [Parameter.from_dict(param_dict) for param_dict in template_dict.get("parameters", [])]

        if not self.name:
            raise AssertionError("EazyVizy file must contain a name.")
        if not os.path.exists(self.template):
            raise AssertionError(
                f"Jinja2 file {self.template} could not be found. \
                    Provide your eazyvizy.yaml a relative path to a jinja2 file."
            )
        if not os.path.isdir(code):
            raise AssertionError(
                f"Code directory {code} could not be found. \
                    Provide your eazyvizy.yaml with a relative path to the entrypoint file of your script."
            )
        try:
            self.code = importlib.import_module(code.replace("/","."))
        except BaseException as exc:
            raise AssertionError(
                str(exc)
            ) from exc

