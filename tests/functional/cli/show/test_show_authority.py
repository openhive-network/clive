from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_is_authority
from clive_local_tools.data.constants import WORKING_ACCOUNT

if TYPE_CHECKING:
    from clive_local_tools.cli.testing_cli import TestingCli


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_show_authoruty_basic(testing_cli: TestingCli, authority: AuthorityType) -> None:
    # ACT
    # ASSERT
    assert_is_authority(testing_cli, WORKING_ACCOUNT.public_key, authority)
