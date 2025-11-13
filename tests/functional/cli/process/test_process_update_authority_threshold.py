from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.cli.exceptions import CLINoChangesTransactionError
from clive.__private.core.constants.authority import AUTHORITY_LEVELS_REGULAR
from clive_local_tools.cli.checkers import assert_weight_threshold
from clive_local_tools.cli.exceptions import CLITestCommandError
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevelRegular
    from clive_local_tools.cli.cli_tester import CLITester


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_set_threshold(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ARRANGE
    weight_threshold = 3

    # ACT
    cli_tester.process_update_authority(
        authority, sign_with=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold
    ).fire()

    # ASSERT
    assert_weight_threshold(cli_tester, authority, weight_threshold)


@pytest.mark.parametrize("authority", AUTHORITY_LEVELS_REGULAR)
async def test_negative_do_nothing_command(cli_tester: CLITester, authority: AuthorityLevelRegular) -> None:
    # ACT & ASSERT
    with pytest.raises(CLITestCommandError, match=CLINoChangesTransactionError.MESSAGE):
        cli_tester.process_update_authority(authority, sign_with=WORKING_ACCOUNT_KEY_ALIAS).fire()
