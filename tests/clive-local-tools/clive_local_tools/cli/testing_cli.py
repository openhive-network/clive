from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from .command_chaining import (
    UpdateActiveAuthority,
    UpdateAuthority,
    UpdateOwnerAuthority,
    UpdatePostingAuthority,
    kwargs_to_cli_options,
)
from .exceptions import CliveCommandError

if TYPE_CHECKING:
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.cli.types import AuthorityType


class TestingCli:
    def __init__(self, typer: CliveTyper, runner: CliRunner) -> None:
        self.__typer = typer
        self.__runner = runner

    def __invoke(self, command: list[str], *args: str, **kwargs: str) -> Result:
        full_command = [*command, *args, *kwargs_to_cli_options(**kwargs)]
        tt.logger.info(f"Executing command {full_command}.")
        result = self.__runner.invoke(self.__typer, full_command)
        if result.exit_code != 0:
            raise CliveCommandError(full_command, result.exit_code, result.stdout, result)
        return result

    def show_authority(self, authority: AuthorityType, *args: str, **kwargs: str) -> Result:
        match authority:
            case "owner":
                return self.show_owner_authority(*args, **kwargs)
            case "active":
                return self.show_active_authority(*args, **kwargs)
            case "posting":
                return self.show_posting_authority(*args, **kwargs)
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def process_update_authority(self, authority: AuthorityType, *args: str, **kwargs: str) -> UpdateAuthority:
        match authority:
            case "owner":
                return self.process_update_owner_authority(*args, **kwargs)
            case "active":
                return self.process_update_active_authority(*args, **kwargs)
            case "posting":
                return self.process_update_posting_authority(*args, **kwargs)
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def show_owner_authority(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["show", "owner-authority"], *args, **kwargs)

    def show_active_authority(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["show", "active-authority"], *args, **kwargs)

    def show_posting_authority(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["show", "posting-authority"], *args, **kwargs)

    def show_memo_key(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["show", "memo-key"], *args, **kwargs)

    def show_pending_withdrawals(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["show", "pending", "withdrawals"], *args, **kwargs)

    def show_balances(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["show", "balances"], *args, **kwargs)

    def process_update_owner_authority(self, *args: str, **kwargs: str) -> UpdateOwnerAuthority:
        return UpdateOwnerAuthority(self.__typer, self.__runner, *args, **kwargs)

    def process_update_active_authority(self, *args: str, **kwargs: str) -> UpdateActiveAuthority:
        return UpdateActiveAuthority(self.__typer, self.__runner, *args, **kwargs)

    def process_update_posting_authority(self, *args: str, **kwargs: str) -> UpdatePostingAuthority:
        return UpdatePostingAuthority(self.__typer, self.__runner, *args, **kwargs)

    def process_update_memo_key(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["process", "update-memo-key"], *args, **kwargs)

    def process_savings_deposit(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["process", "savings", "deposit"], *args, **kwargs)

    def process_savings_withdrawal(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["process", "savings", "withdrawal"], *args, **kwargs)

    def process_savings_withdrawal_cancel(self, *args: str, **kwargs: str) -> Result:
        return self.__invoke(["process", "savings", "withdrawal-cancel"], *args, **kwargs)
