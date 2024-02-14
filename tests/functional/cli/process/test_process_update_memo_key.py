from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.checkers import assert_memo_key, assert_no_exit_code_error
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


other_account = WATCHED_ACCOUNTS[0]
alice_memo_key = WORKING_ACCOUNT.public_key
other_memo_key = other_account.public_key


async def test_set_memo_key(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "update-memo-key",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            f"--key={alice_memo_key}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_memo_key(runner, cli, alice_memo_key)


async def test_set_memo_key_no_broadcast(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "update-memo-key",
            f"--password={WORKING_ACCOUNT.name}",
            "--no-broadcast",
            f"--key={other_memo_key}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_memo_key(runner, cli, alice_memo_key)


async def test_set_other_memo_key(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            "update-memo-key",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            f"--key={other_memo_key}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_memo_key(runner, cli, other_memo_key)
