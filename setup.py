#!/usr/bin/env python3

import re
import setuptools

with open("eazyvizy/_version.py", "r") as f:
    try:
        version = re.search(
            r"__version__\s*=\s*[\"']([^\"']+)[\"']",
            f.read()).group(1)
    except BaseException:
        raise RuntimeError("Version info not available")

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="eazyvizy",
    version=version,
    author="Jatalocks",
    description="A tiny framework for exposing python scripts as parameterized web apps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jatalocks/eazyvizy",
    packages=setuptools.find_packages(),
    scripts=["bin/eazyvizy"],
    # install_requires=[
    #     "Jinja2~=3.0",
    #     "pyyaml~=5.0",
    #     "requests~=2.0",
    # ],
    # classifiers=(
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ),
)
