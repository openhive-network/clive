from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLINoProfileUnlockedError
from clive_local_tools.testnet_block_log import (
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester


async def test_unlocked_profile(cli_tester: CLITester) -> None:
    # ACT
    result = cli_tester.show_profile()

    # ASSERT
    assert f"Profile name: {WORKING_ACCOUNT_NAME}" in result.output


async def test_negative_no_unlocked_profile(cli_tester_locked: CLITester) -> None:
    # ARRANGE
    expected_error = CLINoProfileUnlockedError.MESSAGE

    # ACT
    with pytest.raises(AssertionError) as exception_info:
        cli_tester_locked.show_balances()

    # ASSERT
    assert expected_error in str(exception_info.value)
