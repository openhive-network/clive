from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_is_authority
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_show_authority_basic(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ACT
    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
