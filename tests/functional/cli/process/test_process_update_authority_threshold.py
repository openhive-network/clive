from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import assert_no_exit_code_error, assert_weight_threshold
from clive_local_tools.data.constants import WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_set_threshold(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner
    weight_threshold = 3

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            f"--threshold={weight_threshold}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_weight_threshold(runner, cli, authority, weight_threshold)
