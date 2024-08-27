from __future__ import annotations

from typing import TYPE_CHECKING

from clive_local_tools.cli.chaining.chained_command import ChainedCommand

if TYPE_CHECKING:
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.models.schemas import PublicKey
    from clive_local_tools.cli.command_options import CliOptionT


class UpdateAuthority(ChainedCommand):
    def add_key(self, *, key: PublicKey, weight: int) -> UpdateAuthority:
        self._add_command_to_chain("add-key", key=key, weight=weight)
        return self

    def add_account(self, *, account: str, weight: int) -> UpdateAuthority:
        self._add_command_to_chain("add-account", account=account, weight=weight)
        return self

    def remove_key(self, *, key: PublicKey) -> UpdateAuthority:
        self._add_command_to_chain("remove-key", key=key)
        return self

    def remove_account(self, *, account: str) -> UpdateAuthority:
        self._add_command_to_chain("remove-account", account=account)
        return self

    def modify_key(self, *, key: PublicKey, weight: int) -> UpdateAuthority:
        self._add_command_to_chain("modify-key", key=key, weight=weight)
        return self

    def modify_account(self, *, account: str, weight: int) -> UpdateAuthority:
        self._add_command_to_chain("modify-account", account=account, weight=weight)
        return self


class UpdateOwnerAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **cli_options: CliOptionT) -> None:
        command = ["process", "update-owner-authority"]
        super().__init__(typer, runner, command, **cli_options)


class UpdateActiveAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **cli_options: CliOptionT) -> None:
        command = ["process", "update-active-authority"]
        super().__init__(typer, runner, command, **cli_options)


class UpdatePostingAuthority(UpdateAuthority):
    def __init__(self, typer: CliveTyper, runner: CliRunner, **cli_options: CliOptionT) -> None:
        command = ["process", "update-posting-authority"]
        super().__init__(typer, runner, command, **cli_options)
