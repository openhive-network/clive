from __future__ import annotations

from typing import TYPE_CHECKING, get_args

import pytest

from clive.__private.cli.types import AuthorityType
from clive_local_tools.cli.checkers import (
    assert_authority_weight,
    assert_is_authority,
    assert_is_not_authority,
    assert_no_exit_code_error,
)
from clive_local_tools.data.constants import WATCHED_ACCOUNTS, WORKING_ACCOUNT, WORKING_ACCOUNT_KEY_ALIAS

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper


other_account = WATCHED_ACCOUNTS[0]
weight = 123
modified_weight = 124


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_add_key(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "add-key",
            f"--key={other_account.public_key}",
            f"--weight={weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_is_authority(runner, cli, other_account.public_key, authority)
    assert_authority_weight(runner, cli, other_account.public_key, authority, weight)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_remove_key(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "add-key",
            f"--key={other_account.public_key}",
            f"--weight={weight}",
        ],
    )
    assert_no_exit_code_error(result)
    assert_is_authority(runner, cli, other_account.public_key, authority)

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "remove-key",
            f"--key={other_account.public_key}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_is_not_authority(runner, cli, other_account.public_key, authority)


@pytest.mark.parametrize("authority", get_args(AuthorityType))
async def test_modify_key(cli_with_runner: tuple[CliveTyper, CliRunner], authority: AuthorityType) -> None:
    # ARRANGE
    cli, runner = cli_with_runner

    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "add-key",
            f"--key={other_account.public_key}",
            f"--weight={weight}",
        ],
    )
    assert_no_exit_code_error(result)
    assert_is_authority(runner, cli, other_account.public_key, authority)

    # ACT
    result = runner.invoke(
        cli,
        [
            "process",
            f"update-{authority}-authority",
            f"--password={WORKING_ACCOUNT.name}",
            f"--sign={WORKING_ACCOUNT_KEY_ALIAS}",
            "modify-key",
            f"--key={other_account.public_key}",
            f"--weight={modified_weight}",
        ],
    )
    assert_no_exit_code_error(result)

    # ASSERT
    assert_is_authority(runner, cli, other_account.public_key, authority)
    assert_authority_weight(runner, cli, other_account.public_key, authority, modified_weight)
