from __future__ import annotations

import os
import subprocess
from pathlib import Path
from time import perf_counter

from clive.__private.logger import logger
from clive.main import __file__ as path_to_clive_main
from clive_local_tools.cli.imports import _get_imports_tree


def get_cli_help_imports_time(env: dict[str, str] | None = None) -> float:
    env_ = os.environ.copy()
    env_["TIMEFORMAT"] = "%R"
    if env is not None:
        env_.update(env)
    output = _get_imports_tree(Path(path_to_clive_main), "--help", env=env_, with_time=True)
    import_time = float(output.strip().splitlines()[-1].replace(",", "."))
    logger.info(f"Cumulative import time: {import_time:.6f}s")
    return import_time


def get_autocompletion_time() -> float:
    return get_cli_help_imports_time(env={"_CLIVE_COMPLETE": "1"})


def get_command_execution_time(command: str, env: dict[str, str] | None = None) -> float:
    env_ = os.environ.copy()
    if env is not None:
        env_.update(env)

    logger.info(f"Running command:\n{command}")

    start_time = perf_counter()
    subprocess.run(command, shell=True, check=True, env=env_)
    end_time = perf_counter()

    actual_execution_time = end_time - start_time
    logger.info(f"Command execution time: {actual_execution_time:.6f}s")
    return actual_execution_time


def get_cli_help_execution_time(env: dict[str, str] | None = None) -> float:
    return get_command_execution_time("clive --help", env=env)
