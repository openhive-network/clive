from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from .command_chaining import (
    UpdateActiveAuthority,
    UpdateAuthority,
    UpdateOwnerAuthority,
    UpdatePostingAuthority,
)
from .command_options import kwargs_to_cli_options
from .exceptions import CliveCommandError

if TYPE_CHECKING:
    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.cli.types import AuthorityType
    from clive_local_tools.cli.command_options import KwargsType
    from schemas.fields.basic import PublicKey


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

    def show_authority(
        self, /, authority: AuthorityType, *, account_name: str | None = None, profile_name: str | None = None
    ) -> Result:
        match authority:
            case "owner":
                return self.show_owner_authority(account_name=account_name, profile_name=profile_name)
            case "active":
                return self.show_active_authority(account_name=account_name, profile_name=profile_name)
            case "posting":
                return self.show_posting_authority(account_name=account_name, profile_name=profile_name)
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def process_update_authority(  # noqa: PLR0913
        self,
        authority: AuthorityType,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        force_offline: bool | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> UpdateAuthority:
        match authority:
            case "owner":
                return self.process_update_owner_authority(
                    account_name=account_name,
                    threshold=threshold,
                    force_offline=force_offline,
                    profile_name=profile_name,
                    password=password,
                    sign=sign,
                    beekeeper_remote=beekeeper_remote,
                    broadcast=broadcast,
                    save_file=save_file,
                )
            case "active":
                return self.process_update_active_authority(
                    account_name=account_name,
                    threshold=threshold,
                    force_offline=force_offline,
                    profile_name=profile_name,
                    password=password,
                    sign=sign,
                    beekeeper_remote=beekeeper_remote,
                    broadcast=broadcast,
                    save_file=save_file,
                )
            case "posting":
                return self.process_update_posting_authority(
                    account_name=account_name,
                    threshold=threshold,
                    force_offline=force_offline,
                    profile_name=profile_name,
                    password=password,
                    sign=sign,
                    beekeeper_remote=beekeeper_remote,
                    broadcast=broadcast,
                    save_file=save_file,
                )
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def show_owner_authority(self, /, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "owner-authority"], account_name=account_name, profile_name=profile_name)

    def show_active_authority(self, /, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "active-authority"], account_name=account_name, profile_name=profile_name)

    def show_posting_authority(self, /, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "posting-authority"], account_name=account_name, profile_name=profile_name)

    def show_memo_key(self, /, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "memo-key"], account_name=account_name, profile_name=profile_name)

    def show_pending_withdrawals(
        self, /, *, account_name: str | None = None, profile_name: str | None = None
    ) -> Result:
        return self.__invoke(["show", "pending", "withdrawals"], account_name=account_name, profile_name=profile_name)

    def show_balances(self, /, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "balances"], account_name=account_name, profile_name=profile_name)

    def process_update_owner_authority(  # noqa: PLR0913
        self,
        /,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        force_offline: bool | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> UpdateOwnerAuthority:
        return UpdateOwnerAuthority(
            self.__typer,
            self.__runner,
            account_name=account_name,
            threshold=threshold,
            force_offline=force_offline,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
        )

    def process_update_active_authority(  # noqa: PLR0913
        self,
        /,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        force_offline: bool | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> UpdateActiveAuthority:
        return UpdateActiveAuthority(
            self.__typer,
            self.__runner,
            account_name=account_name,
            threshold=threshold,
            force_offline=force_offline,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
        )

    def process_update_posting_authority(  # noqa: PLR0913
        self,
        /,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        force_offline: bool | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> UpdatePostingAuthority:
        return UpdatePostingAuthority(
            self.__typer,
            self.__runner,
            account_name=account_name,
            threshold=threshold,
            force_offline=force_offline,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
        )

    def process_update_memo_key(  # noqa: PLR0913
        self,
        /,
        *,
        account_name: str | None = None,
        key: PublicKey,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(
            ["process", "update-memo-key"],
            account_name=account_name,
            key=key,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
        )

    def process_savings_deposit(  # noqa: PLR0913
        self,
        /,
        *,
        to: str | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
        amount: tt.Asset.AnyT,
        memo: str | None = None,
        from_: str | None = None,
    ) -> Result:
        return self.__invoke(
            ["process", "savings", "deposit"],
            to=to,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
            amount=amount,
            memo=memo,
            from_=from_,
        )

    def process_savings_withdrawal(  # noqa: PLR0913
        self,
        /,
        *,
        request_id: int | None = None,
        to: str | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
        amount: tt.Asset.AnyT,
        memo: str | None = None,
        from_: str | None = None,
    ) -> Result:
        return self.__invoke(
            ["process", "savings", "withdrawal"],
            request_id=request_id,
            to=to,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
            amount=amount,
            memo=memo,
            from_=from_,
        )

    def process_savings_withdrawal_cancel(  # noqa: PLR0913
        self,
        /,
        *,
        from_: str | None = None,
        request_id: int,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(
            ["process", "savings", "withdrawal-cancel"],
            from_=from_,
            request_id=request_id,
            profile_name=profile_name,
            password=password,
            sign=sign,
            beekeeper_remote=beekeeper_remote,
            broadcast=broadcast,
            save_file=save_file,
        )
