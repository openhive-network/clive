from __future__ import annotations

from setuptools import setup

packages = ["wax"]

package_data = {"": ["*"]}

setup_kwargs = {
    "name": "wax",
    "version": "0.0.0",
    "description": "",
    "long_description": "None",
    "author": "None",
    "author_email": "None",
    "maintainer": "None",
    "maintainer_email": "None",
    "url": "https://gitlab.syncad.com/hive/clive",
    "packages": packages,
    "package_data": package_data,
    "python_requires": ">=3.10,<4.0",
}
from build import *

build(setup_kwargs)

setup(**setup_kwargs)  # type: ignore[arg-type]
