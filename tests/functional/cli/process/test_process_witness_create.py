from __future__ import annotations

from typing import TYPE_CHECKING, Final

import test_tools as tt

from clive.models import Asset
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


SIGNING_KEY = WORKING_ACCOUNT_DATA.account.public_key
FEE: Final[Asset.Hive] = Asset.hive(5)
ACCOUNT_CREATION_FEE: Final[Asset.Hive] = Asset.hive(50)


async def test_create_new(node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_create(
        url="http://url.html",
        block_signing_key=SIGNING_KEY,
        fee=FEE,
        account_creation_fee=ACCOUNT_CREATION_FEE,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )


async def test_enable(node: tt.RawNode, cli_tester: CLITester) -> None:
    # PREPARE
    cli_tester.process_witness_create(
        url="http://url.html",
        block_signing_key=SIGNING_KEY,
        fee=FEE,
        account_creation_fee=ACCOUNT_CREATION_FEE,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
    cli_tester.process_witness_disable(password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS)

    # ACT
    result = cli_tester.process_witness_create(
        url="http://url.html",
        block_signing_key=SIGNING_KEY,
        fee=FEE,
        account_creation_fee=ACCOUNT_CREATION_FEE,
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
    )
