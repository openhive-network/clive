from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

import pytest

from clive.__private.core.constants.env import ENVVAR_PREFIX
from clive.__private.core.constants.setting_identifiers import DATA_PATH, SECRETS_NODE_ADDRESS
from clive.__private.core.validate_schema_field import validate_schema_field
from clive.__private.settings import safe_settings
from clive.models.aliased import TransactionId

if TYPE_CHECKING:
    from click.testing import Result


def clive_prefixed_envvar(setting_name: str) -> str:
    underscored_setting_name = setting_name.replace(".", "__")
    return f"{ENVVAR_PREFIX}_{underscored_setting_name}"


def get_transaction_id_from_output(output: str) -> str:
    for line in output.split("\n"):
        transaction_id = line.partition('"transaction_id":')[2]
        if transaction_id:
            transaction_id_field = transaction_id.strip(' "')
            validate_schema_field(TransactionId, transaction_id_field)
            return transaction_id_field
    pytest.fail(f"Could not find transaction id in output {output}")


def get_transaction_id_from_result(result: Result) -> str:
    return get_transaction_id_from_output(result.stdout)


def run_clive_in_subprocess(command: list[str]) -> str:
    env = os.environ.copy()
    env["CLIVE_DATA_PATH"] = str(safe_settings.data_path)
    # env["CLIVE_SECRETS__NODE_ADDRESS"] = settings.get(SECRETS_NODE_ADDRESS)
    secret_node_address = safe_settings.secrets.node_address
    assert secret_node_address is not None, "Secrets node address is not set"
    env["CLIVE_SECRETS__NODE_ADDRESS"] = str(secret_node_address)

    completed_process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=True)
    return completed_process.stdout.decode()
