from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.constants.node import NULL_ACCOUNT_KEY_VALUE
from clive.models import Asset
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


async def test_no_default_account(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        owner=WORKING_ACCOUNT_DATA.account.name, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_account_creation_fee(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        account_creation_fee=ACCOUNT_CREATION_FEE, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_maximum_block_size(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        maximum_block_size=100000, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_hbd_interest_rate(prepare_witness: None, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        hbd_interest_rate=43, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_account_subsidy_budget(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        account_subsidy_budget=1, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_account_subsidy_decay(
    prepare_witness: None, node: tt.RawNode, cli_tester: CLITester, tmp_path: Path
) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        account_subsidy_decay=64, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_hbd_exchange_rate(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        hbd_exchange_rate=1.5, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_url(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        url=EXAMPLE_URL, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_new_signing_key(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        new_signing_key=SIGNING_KEY, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )


async def test_null_new_signing_key(prepare_witness: None, node: tt.RawNode, cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.process_witness_update(
        new_signing_key=NULL_ACCOUNT_KEY_VALUE, password=WORKING_ACCOUNT_PASSWORD, sign=WORKING_ACCOUNT_KEY_ALIAS
    )
