from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_is_authority, assert_no_exit_code_error
from clive_local_tools.data.constants import WORKING_ACCOUNT

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_show_authoruty_basic(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(cli, ["show", f"{authority}-authority"])

    # ASSERT
    assert_no_exit_code_error(result)
    assert_is_authority(runner, cli, WORKING_ACCOUNT.public_key, authority)
