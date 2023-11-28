from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


async def test_withdrawal_cancel_valid(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
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
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            "--request-id=13",
            "--amount=0.234 HIVE",
            "--from=alice",
            "--to=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal-cancel",
            "--request-id=13",
            "--from=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    assert result.exit_code == 0

    # ASSERT
    result = runner.invoke(cli, ["show", "pending", "withdrawals", "--profile-name=alice", "--account-name=alice"])
    assert result.exit_code == 0
    assert "0.234" not in result.stdout


async def test_withdrawal_cancel_invalid(cli_with_runner: tuple[CliveTyper, CliRunner]) -> None:
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
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal",
            "--request-id=13",
            "--amount=0.234 HIVE",
            "--from=alice",
            "--to=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    assert result.exit_code == 0

    result = runner.invoke(
        cli,
        [
            "process",
            "savings",
            "withdrawal-cancel",
            "--request-id=24",
            "--from=alice",
            "--profile-name=alice",
            "--password=alice",
            "--sign=alice_key",
        ],
    )
    assert result.exit_code == 1

    # ASSERT
    result = runner.invoke(cli, ["show", "pending", "withdrawals", "--profile-name=alice", "--account-name=alice"])
    assert result.exit_code == 0
    assert "0.234" in result.stdout
