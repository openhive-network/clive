from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.core.constants.authority import AUTHORITY_LEVELS_REGULAR
from clive_local_tools.cli.checkers import assert_is_authority
from clive_local_tools.testnet_block_log import WORKING_ACCOUNT_DATA

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_show_authority_basic(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT
    # ASSERT
    assert_is_authority(cli_tester, WORKING_ACCOUNT_DATA.account.public_key, authority)
