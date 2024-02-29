from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_weight_threshold
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_set_threshold(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ARRANGE
    weight_threshold = 3

    # ACT
    testing_cli.process_update_authority(
        authority, password=WORKING_ACCOUNT.name, sign=WORKING_ACCOUNT_KEY_ALIAS, threshold=weight_threshold
    ).fire()

    # ASSERT
    assert_weight_threshold(testing_cli, authority, weight_threshold)
