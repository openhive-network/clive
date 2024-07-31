from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from clive.__private.core.constants.setting_identifiers import DATA_PATH, SECRETS_NODE_ADDRESS
from clive.__private.settings import clive_prefixed_envvar, safe_settings
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    from click.testing import Result


def get_transaction_id_from_result(result: Result) -> str:
    return get_transaction_id_from_output(result.stdout)


def run_clive_in_subprocess(command: list[str]) -> str:
    env = os.environ.copy()
    env[clive_prefixed_envvar(DATA_PATH)] = str(safe_settings.data_path)
    secret_node_address = safe_settings.secrets.node_address
    assert secret_node_address is not None, "Secrets node address is not set"
    env[clive_prefixed_envvar(SECRETS_NODE_ADDRESS)] = str(secret_node_address)

    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=True)
    return completed_process.stdout.decode()
