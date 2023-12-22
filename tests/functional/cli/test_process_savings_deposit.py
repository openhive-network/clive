from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


async def test_deposit_valid(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "deposit",
            "--amount=0.234 HIVE",
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
    result = runner.invoke(cli, ["show", "balances", "--profile-name=alice", "--account-name=alice"])
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0
    assert "0.234" in result.stdout


async def test_deposit_to_other_account(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "deposit",
            "--amount=0.234 HIVE",
            "--from=alice",
            "--to=bob",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0

    # ASSERT
    result = runner.invoke(cli, ["show", "balances", "--profile-name=alice", "--account-name=bob"])
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0
    assert "0.234" in result.stdout


async def test_deposit_not_enough_hive(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "deposit",
            "--amount=234234.234 HIVE",
            "--from=alice",
            "--to=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code != 0

    # ASSERT
    result = runner.invoke(cli, ["show", "balances", "--profile-name=alice", "--account-name=alice"])
    tt.logger.info(f"{result.stdout=}")
    assert result.exit_code == 0
    assert "234.234" not in result.stdout
