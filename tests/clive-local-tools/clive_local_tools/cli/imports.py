from __future__ import annotations

import os
import subprocess
from pathlib import Path

from clive.__private.logger import logger
from clive.main import __file__ as path_to_clive_main


def _get_imports_tree(file_path: Path, *args: str, env: dict[str, str] | None = None, with_time: bool = False) -> str:
    time_prefix = "time " if with_time else ""
    command = f"/bin/bash -c '{time_prefix}python3 -X importtime {file_path.absolute().as_posix()}"
    if args:
        command += f" {' '.join(args)}'"

    logger.info(f"Running command:\n{command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False, env=env)

    stderr = result.stderr
    assert result.returncode == 0, f"Failed to get imports tree:\n{stderr}"
    logger.info(f"Output:\n{stderr}")
    return stderr


def get_cli_help_imports_tree(env: dict[str, str] | None = None) -> str:
    return _get_imports_tree(Path(path_to_clive_main), "--help", env=env)


def get_cli_help_imports_time(env: dict[str, str] | None = None) -> float:
    env_ = os.environ.copy()
    env_["TIMEFORMAT"] = "%U"
    if env is not None:
        env_.update(env)
    output = _get_imports_tree(Path(path_to_clive_main), "--help", env=env_, with_time=True)
    import_time = float(output.strip().splitlines()[-1].replace(",", "."))
    logger.info(f"Cumulative import time: {import_time:.6f}s")
    return import_time


def get_autocompletion_time() -> float:
    return get_cli_help_imports_time(env={"_CLIVE_COMPLETE": "1"})
