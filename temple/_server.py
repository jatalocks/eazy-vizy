import os
from flask import Flask, render_template, request
from threading import Thread
import sys
import importlib
from time import sleep
import ast
import inspect
import functools


class EazyVizyServer(Thread):
    def __init__(self, eazyvizy):
        super().__init__()
        self.eazyvizy = eazyvizy
        self.app = Flask(__name__, template_folder=os.path.dirname(eazyvizy.template), root_path=os.getcwd())
        code = self.eazyvizy.code

        @self.app.route("/")
        @self.app.route("/<path:path>")
        def index(path=None):
            template_params = {(param): vars(self.eazyvizy).get(param) for param in vars(self.eazyvizy)}
            if not path:
                return render_template(os.path.basename(eazyvizy.template), **template_params)
            return render_template(path, **template_params)

        funcDict = {}
        for name, obj in inspect.getmembers(code):
            if inspect.isfunction(obj):
                if has_eazyvizy_endpoint_decorator(obj):
                    funcDict[name] = obj

        @self.app.route("/code/<task>", methods=["GET", "POST"])
        def invoke_function(task):
            if funcDict.get(task):
                if request.method == "POST":
                    return funcDict.get(task)(**request.values)
                return funcDict.get(task)(**request.args)

    def run(self):
        self.app.run()

    def update_parameter(self, param_name, value):
        setattr(self.app.config, param_name, value)


def has_eazyvizy_endpoint_decorator(func):
    return getattr(func, "endpoint", False)
