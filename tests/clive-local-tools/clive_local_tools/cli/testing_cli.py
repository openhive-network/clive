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
    from clive_local_tools.cli.command_options import KwargsType


class TestingCli:
    def __init__(self, typer: CliveTyper, runner: CliRunner) -> None:
        self.__typer = typer
        self.__runner = runner

    def __invoke(self, command: list[str], **kwargs: KwargsType) -> Result:
        full_command = [*command, *kwargs_to_cli_options(**kwargs)]
        tt.logger.info(f"Executing command {full_command}.")
        result = self.__runner.invoke(self.__typer, full_command)
        if result.exit_code != 0:
            raise CliveCommandError(full_command, result.exit_code, result.stdout, result)
        return result

    def show_authority(self, authority: AuthorityType, **kwargs: KwargsType) -> Result:
        match authority:
            case "owner":
                return self.show_owner_authority(**kwargs)
            case "active":
                return self.show_active_authority(**kwargs)
            case "posting":
                return self.show_posting_authority(**kwargs)
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def process_update_authority(self, authority: AuthorityType, **kwargs: KwargsType) -> UpdateAuthority:
        match authority:
            case "owner":
                return self.process_update_owner_authority(**kwargs)
            case "active":
                return self.process_update_active_authority(**kwargs)
            case "posting":
                return self.process_update_posting_authority(**kwargs)
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def show_owner_authority(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["show", "owner-authority"], **kwargs)

    def show_active_authority(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["show", "active-authority"], **kwargs)

    def show_posting_authority(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["show", "posting-authority"], **kwargs)

    def show_memo_key(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["show", "memo-key"], **kwargs)

    def show_pending_withdrawals(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["show", "pending", "withdrawals"], **kwargs)

    def show_balances(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["show", "balances"], **kwargs)

    def process_update_owner_authority(self, **kwargs: KwargsType) -> UpdateOwnerAuthority:
        return UpdateOwnerAuthority(self.__typer, self.__runner, **kwargs)

    def process_update_active_authority(self, **kwargs: KwargsType) -> UpdateActiveAuthority:
        return UpdateActiveAuthority(self.__typer, self.__runner, **kwargs)

    def process_update_posting_authority(self, **kwargs: KwargsType) -> UpdatePostingAuthority:
        return UpdatePostingAuthority(self.__typer, self.__runner, **kwargs)

    def process_update_memo_key(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["process", "update-memo-key"], **kwargs)

    def process_savings_deposit(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["process", "savings", "deposit"], **kwargs)

    def process_savings_withdrawal(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["process", "savings", "withdrawal"], **kwargs)

    def process_savings_withdrawal_cancel(self, **kwargs: KwargsType) -> Result:
        return self.__invoke(["process", "savings", "withdrawal-cancel"], **kwargs)
