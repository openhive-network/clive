from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from clive.__private.core.constants.setting_identifiers import DATA_PATH
from clive.__private.core.constants.terminal import TERMINAL_WIDTH
from clive.__private.settings import clive_prefixed_envvar, safe_settings
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str:
    return get_transaction_id_from_output(result.stdout)


def run_clive_in_subprocess(command: list[str]) -> str:
    env = os.environ.copy()
    env[clive_prefixed_envvar(DATA_PATH)] = str(safe_settings.data_path)
    env["COLUMNS"] = f"{TERMINAL_WIDTH}"

    try:
        completed_process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=True
        )
    except subprocess.CalledProcessError as error:
        output_string = error.output.decode() if isinstance(error.output, bytes) else error.output
        message = f"error executing command {command}:\n{output_string}"
        raise AssertionError(message) from error
    return completed_process.stdout.decode()
