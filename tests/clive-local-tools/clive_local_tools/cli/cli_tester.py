from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from .chaining.update_authority import (
    UpdateActiveAuthority,
    UpdateAuthority,
    UpdateOwnerAuthority,
    UpdatePostingAuthority,
)
from .command_options import extract_params, kwargs_to_cli_options
from .exceptions import CLITestCommandError

if TYPE_CHECKING:
    from pathlib import Path

    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.cli.types import AuthorityType
    from clive.__private.core.commands.sign import AlreadySignedMode
    from clive_local_tools.cli.command_options import CliOptionT
    from schemas.fields.basic import PublicKey


class CLITester:
    def __init__(self, typer: CliveTyper, runner: CliRunner) -> None:
        self.__typer = typer
        self.__runner = runner

    def __invoke(self, command: list[str], **cli_options: CliOptionT) -> Result:
        full_command = [*command, *kwargs_to_cli_options(**cli_options)]
        tt.logger.info(f"Executing command {full_command}.")
        result = self.__runner.invoke(self.__typer, full_command)
        if result.exit_code != 0:
            raise CLITestCommandError(full_command, result.exit_code, result.stdout, result)
        return result

    def show_authority(
        self, authority: AuthorityType, *, account_name: str | None = None, profile_name: str | None = None
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
                    **extract_params(locals(), "authority")  # type: ignore[arg-type]
                )
            case "active":
                return self.process_update_active_authority(
                    **extract_params(locals(), "authority")  # type: ignore[arg-type]
                )
            case "posting":
                return self.process_update_posting_authority(
                    **extract_params(locals(), "authority")  # type: ignore[arg-type]
                )
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def show_owner_authority(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "owner-authority"], account_name=account_name, profile_name=profile_name)

    def show_active_authority(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "active-authority"], account_name=account_name, profile_name=profile_name)

    def show_posting_authority(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "posting-authority"], account_name=account_name, profile_name=profile_name)

    def show_memo_key(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "memo-key"], account_name=account_name, profile_name=profile_name)

    def show_pending_withdrawals(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "pending", "withdrawals"], account_name=account_name, profile_name=profile_name)

    def show_balances(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "balances"], account_name=account_name, profile_name=profile_name)

    def process_update_owner_authority(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
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
            **extract_params(locals()),
        )

    def process_update_active_authority(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
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
            **extract_params(locals()),
        )

    def process_update_posting_authority(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
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
            **extract_params(locals()),
        )

    def process_update_memo_key(  # noqa: PLR0913
        self,
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
            **extract_params(locals()),
        )

    def process_savings_deposit(  # noqa: PLR0913
        self,
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
            **extract_params(locals()),
        )

    def process_savings_withdrawal(  # noqa: PLR0913
        self,
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
            **extract_params(locals()),
        )

    def process_savings_withdrawal_cancel(  # noqa: PLR0913
        self,
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
            **extract_params(locals()),
        )

    def process_custom_json(  # noqa: PLR0913
        self,
        *,
        authorize: str | list[str] | None = None,
        authorize_by_active: str | list[str] | None = None,
        id_: str,
        json_: str | Path,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
    ) -> Result:
        return self.__invoke(
            ["process", "custom-json"],
            **extract_params(locals()),
        )

    def process_transaction(  # noqa: PLR0913
        self,
        *,
        from_file: Path,
        force_unsign: bool | None = None,
        already_signed_mode: AlreadySignedMode | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
    ) -> Result:
        return self.__invoke(
            ["process", "transaction"],
            **extract_params(locals()),
        )

    def show_hive_power(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "hive-power"], **extract_params(locals()))

    def show_pending_power_down(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "pending", "power-down"], **extract_params(locals()))

    def show_pending_power_ups(self, *, account_name: str | None = None, profile_name: str | None = None) -> Result:
        return self.__invoke(["show", "pending", "power-ups"], **extract_params(locals()))

    def show_pending_removed_delegations(
        self, *, account_name: str | None = None, profile_name: str | None = None
    ) -> Result:
        return self.__invoke(["show", "pending", "removed-delegations"], **extract_params(locals()))

    def process_power_up(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str | None = None,
        amount: tt.Asset.HiveT,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "power-up"], **extract_params(locals()))

    def process_power_down_start(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        amount: tt.Asset.HiveT | tt.Asset.VestsT,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "power-down", "start"], **extract_params(locals()))

    def process_power_down_restart(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        amount: tt.Asset.HiveT | tt.Asset.VestsT,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "power-down", "restart"], **extract_params(locals()))

    def process_power_down_cancel(  # noqa: PLR0913
        self,
        *,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "power-down", "cancel"], **extract_params(locals()))

    def process_delegations_set(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        delegatee: str | None = None,
        amount: tt.Asset.HiveT | tt.Asset.VestsT,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "delegations", "set"], **extract_params(locals()))

    def process_delegations_remove(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        delegatee: str | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "delegations", "remove"], **extract_params(locals()))

    def process_withdraw_routes_set(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str | None,
        percent: int,
        auto_vest: bool | None = None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "withdraw-routes", "set"], **extract_params(locals()))

    def process_withdraw_routes_remove(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str | None,
        profile_name: str | None = None,
        password: str | None = None,
        sign: str | None = None,
        beekeeper_remote: str | None = None,
        broadcast: bool | None = None,
        save_file: str | None = None,
    ) -> Result:
        return self.__invoke(["process", "withdraw-routes", "remove"], **extract_params(locals()))
