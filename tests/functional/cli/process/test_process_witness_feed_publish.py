from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.constants.node import NULL_ACCOUNT_KEY_VALUE
from clive.models import Asset
from clive_local_tools.cli.checkers import assert_no_exit_code_error
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_DATA, WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester


EXAMPLE_URL: Final[str] = "http://url.html"
SIGNING_KEY = WORKING_ACCOUNT_DATA.account.public_key
FEE: Final[Asset.Hive] = Asset.hive(5)
ACCOUNT_CREATION_FEE: Final[Asset.Hive] = Asset.hive(50)
OTHER_ACCOUNT: Final[tt.Account] = WATCHED_ACCOUNTS_DATA[0].account


@pytest.fixture()
async def prepare_witness(cli_tester: CLITester) -> None:
    # PREPARE
    cli_tester.process_witness_create(
        url=EXAMPLE_URL,
        block_signing_key=SIGNING_KEY,
        fee=FEE,
        account_creation_fee=ACCOUNT_CREATION_FEE,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )



async def test_feed_publish(prepare_witness: None, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_feed_publish(
        exchange_rate=1.5, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )

    # ASSERT
    assert_no_exit_code_error(result)
