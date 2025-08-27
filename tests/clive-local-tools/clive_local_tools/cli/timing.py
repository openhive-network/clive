from __future__ import annotations

import os
import subprocess
from time import perf_counter

from clive.__private.logger import logger


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
