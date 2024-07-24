from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

from clive.__private.core.constants.setting_identifiers import DATA_PATH, SECRETS_NODE_ADDRESS
from clive.__private.settings import clive_prefixed_envvar, safe_settings
from clive_local_tools.helpers import get_transaction_id_from_output

if TYPE_CHECKING:
    import test_tools as tt
    from click.testing import Result

from clive.__private.core.date_utils import timedelta_to_int_hours
from clive.__private.core.shorthand_timedelta import shorthand_timedelta_to_timedelta
from clive.__private.models.schemas import (
    RecurrentTransferOperation,
    RecurrentTransferPairIdExtension,
    RecurrentTransferPairIdRepresentation,
)


def get_transaction_id_from_result(result: Result) -> str:
    return get_transaction_id_from_output(result.stdout)


def run_clive_in_subprocess(command: list[str]) -> str:
    env = os.environ.copy()
    env[clive_prefixed_envvar(DATA_PATH)] = str(safe_settings.data_path)
    secret_node_address = safe_settings.secrets.node_address
    assert secret_node_address is not None, "Secrets node address is not set"
    env[clive_prefixed_envvar(SECRETS_NODE_ADDRESS)] = str(secret_node_address)

    try:
        completed_process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=True
        )
    except subprocess.CalledProcessError as error:
        output_string = error.output.decode() if isinstance(error.output, bytes) else error.output
        message = f"error executing command {command}:\n{output_string}"
        raise AssertionError(message) from error
    return completed_process.stdout.decode()


def get_prepared_recurrent_transfer_operation(  # noqa: PLR0913
    from_: str,
    to: str,
    amount: tt.Asset.HiveT | tt.Asset.HbdT,
    memo: str,
    pair_id: int,
    recurrence: str,
    executions: int,
) -> RecurrentTransferOperation:
    if pair_id != 0:
        recurrent_transfer_extension = RecurrentTransferPairIdExtension(pair_id=pair_id)
        representation = RecurrentTransferPairIdRepresentation(
            type=recurrent_transfer_extension.get_name(), value=recurrent_transfer_extension
        )
        extensions = [representation.dict(by_alias=True)]
    else:
        extensions = []
    return RecurrentTransferOperation(
        from_=from_,
        to=to,
        amount=amount,
        memo=memo,
        recurrence=timedelta_to_int_hours(shorthand_timedelta_to_timedelta(recurrence)),
        executions=executions,
        extensions=extensions,
    )
