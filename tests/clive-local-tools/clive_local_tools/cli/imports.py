from __future__ import annotations

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
