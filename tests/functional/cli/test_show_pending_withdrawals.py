from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


async def test_show_pending_withdrawals_none(
    cli_with_runner: tuple[CliveTyper, CliRunner],
) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ASSERT
    result = runner.invoke(cli, ["show", "pending", "withdrawals", "--profile-name=alice", "--account-name=alice"])
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0
    assert "no pending withdrawals" in result.stdout


async def test_show_pending_withdrawals_basic(
    cli_with_runner: tuple[CliveTyper, CliRunner],
    # tmp_path,
) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "deposit",
            "--amount=1 HIVE",
            "--from=alice",
            "--to=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            "--amount=0.111 HIVE",
            "--from=alice",
            "--to=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            "--amount=0.112 HIVE",
            "--from=alice",
            "--to=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0

    # ASSERT
    result = runner.invoke(cli, ["show", "pending", "withdrawals", "--profile-name=alice", "--account-name=alice"])
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0
    assert "0.111 HIVE" in result.stdout
    assert "0.112 HIVE" in result.stdout
