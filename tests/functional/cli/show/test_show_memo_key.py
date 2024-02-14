from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_memo_key, assert_no_exit_code_error
from clive_local_tools.data.constants import WORKING_ACCOUNT

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


async def test_show_memo_key_basic(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(cli, ["show", "memo-key"])

    # ASSERT
    assert_no_exit_code_error(result)
    assert_memo_key(runner, cli, WORKING_ACCOUNT.public_key)
