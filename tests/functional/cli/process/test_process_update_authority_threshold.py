from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_weight_threshold
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_set_threshold(cli_tester: CLITester, authority: AuthorityType) -> None:
    # ARRANGE
    weight_threshold = 3

    # ACT
    cli_tester.process_update_authority(authority, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, weight_threshold)
