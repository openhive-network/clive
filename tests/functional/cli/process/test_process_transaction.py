from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS, WORKING_ACCOUNT_PASSWORD
from clive_local_tools.testnet_block_log.constants import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from pathlib import Path

    from clive_local_tools.cli.cli_tester import CLITester


EXAMPLE_OBJECT: Final[str] = '{"foo": "bar"}'
EXAMPLE_STRING: Final[str] = '"somestring"'
EXAMPLE_NUMBER: Final[str] = "123456.789"


@pytest.mark.parametrize("json_", [EXAMPLE_OBJECT, EXAMPLE_STRING, EXAMPLE_NUMBER])
async def test_load_custom_json_rom_file(cli_tester: CLITester, tmp_path: Path, json_: str) -> None:
    """Regression test for problem with parsing json field in CustomJsonOpetation saved in file."""
    # ARRANGE
    trx_file = tmp_path / "full_trx.json"
    cli_tester.process_custom_json(
        authorize=WORKING_ACCOUNT_DATA.account.name,
        id_="some_id",
        json_=json_,
        broadcast=False,
        save_file=trx_file,
    )

    # ACT
    # ASSERT
    cli_tester.process_transaction(
        password=WORKING_ACCOUNT_PASSWORD,
        sign=WORKING_ACCOUNT_KEY_ALIAS,
        already_signed_mode="multisign",
        from_file=trx_file,
    )
