from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from .chaining.update_authority import (
    UpdateActiveAuthority,
    UpdateAuthority,
    UpdateOwnerAuthority,
    UpdatePostingAuthority,
)
from .command_options import build_cli_options, extract_params, stringify_parameter_value
from .exceptions import CLITestCommandError

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from decimal import Decimal
    from pathlib import Path

    from click.testing import Result
    from typer.testing import CliRunner

    from clive.__private.cli.clive_typer import CliveTyper
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.schemas import PublicKey
    from clive_local_tools.cli.command_options import CliOptionT, StringConvertibleOptionTypes


class CLITester:
    def __init__(self, typer: CliveTyper, runner: CliRunner, world: World) -> None:
        self.__typer = typer
        self.__runner = runner
        self.__world = world

    @property
    def world(self) -> World:
        return self.__world

    def invoke_raw_command(self, command: list[str], password_stdin: str | None = None) -> Result:
        tt.logger.info(f"Executing command {command}.")
        result = self.__runner.invoke(self.__typer, command, password_stdin)
        if result.exit_code != 0:
            raise CLITestCommandError(command, result.exit_code, result.stdout, result)
        return result

    def show_authority(self, authority: AuthorityLevelRegular, *, account_name: str | None = None) -> Result:
        match authority:
            case "owner":
                return self.show_owner_authority(account_name=account_name)
            case "active":
                return self.show_active_authority(account_name=account_name)
            case "posting":
                return self.show_posting_authority(account_name=account_name)
            case _:
                raise ValueError(f"Unknown authority type: '{authority}'")

    def process_update_authority(  # noqa: PLR0913
        self,
        authority: AuthorityLevelRegular,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
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

    def show_owner_authority(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "owner-authority"], cli_named_options=extract_params(locals())
        )

    def show_active_authority(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "active-authority"], cli_named_options=extract_params(locals())
        )

    def show_posting_authority(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "posting-authority"], cli_named_options=extract_params(locals())
        )

    def show_memo_key(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(["show", "memo-key"], cli_named_options=extract_params(locals()))

    def show_pending_withdrawals(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "pending", "withdrawals"], cli_named_options=extract_params(locals())
        )

    def show_balances(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(["show", "balances"], cli_named_options=extract_params(locals()))

    def show_account(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(["show", "account"], cli_named_options=extract_params(locals()))

    def show_accounts(self) -> Result:
        return self.__invoke_command_with_options(["show", "accounts"])

    def process_update_owner_authority(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateOwnerAuthority:
        return UpdateOwnerAuthority(
            self.__typer,
            self.__runner,
            cli_named_options=extract_params(locals()),
        )

    def process_update_active_authority(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdateActiveAuthority:
        return UpdateActiveAuthority(
            self.__typer,
            self.__runner,
            cli_named_options=extract_params(locals()),
        )

    def process_update_posting_authority(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        threshold: int | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> UpdatePostingAuthority:
        return UpdatePostingAuthority(
            self.__typer,
            self.__runner,
            cli_named_options=extract_params(locals()),
        )

    def process_update_memo_key(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        key: PublicKey,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "update-memo-key"],
            cli_named_options=extract_params(locals()),
        )

    def process_savings_deposit(  # noqa: PLR0913
        self,
        *,
        to: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        amount: tt.Asset.AnyT,
        memo: str | None = None,
        from_: str | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "savings", "deposit"],
            cli_named_options=extract_params(locals()),
        )

    def process_savings_withdrawal(  # noqa: PLR0913
        self,
        *,
        request_id: int | None = None,
        to: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        amount: tt.Asset.AnyT,
        memo: str | None = None,
        from_: str | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "savings", "withdrawal"],
            cli_named_options=extract_params(locals()),
        )

    def process_savings_withdrawal_cancel(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        request_id: int,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "savings", "withdrawal-cancel"],
            cli_named_options=extract_params(locals()),
        )

    def process_custom_json(  # noqa: PLR0913
        self,
        *,
        authorize: str | list[str] | None = None,
        authorize_by_active: str | list[str] | None = None,
        id_: str,
        json_: str | Path,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "custom-json"],
            cli_named_options=extract_params(locals()),
        )

    def process_transaction(  # noqa: PLR0913
        self,
        *,
        from_file: Path,
        force_unsign: bool | None = None,
        already_signed_mode: AlreadySignedMode | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "transaction"],
            cli_named_options=extract_params(locals()),
        )

    def show_hive_power(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(["show", "hive-power"], cli_named_options=extract_params(locals()))

    def show_pending_power_down(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "pending", "power-down"], cli_named_options=extract_params(locals())
        )

    def show_pending_power_ups(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "pending", "power-ups"], cli_named_options=extract_params(locals())
        )

    def show_pending_removed_delegations(self, *, account_name: str | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["show", "pending", "removed-delegations"], cli_named_options=extract_params(locals())
        )

    def process_power_up(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str | None = None,
        amount: tt.Asset.HiveT,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(["process", "power-up"], cli_named_options=extract_params(locals()))

    def process_power_down_start(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        amount: tt.Asset.HiveT | tt.Asset.VestsT,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "power-down", "start"], cli_named_options=extract_params(locals())
        )

    def process_power_down_restart(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        amount: tt.Asset.HiveT | tt.Asset.VestsT,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "power-down", "restart"], cli_named_options=extract_params(locals())
        )

    def process_power_down_cancel(
        self,
        *,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "power-down", "cancel"], cli_named_options=extract_params(locals())
        )

    def process_delegations_set(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        delegatee: str | None = None,
        amount: tt.Asset.HiveT | tt.Asset.VestsT,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "delegations", "set"], cli_named_options=extract_params(locals())
        )

    def process_delegations_remove(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        delegatee: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "delegations", "remove"], cli_named_options=extract_params(locals())
        )

    def process_withdraw_routes_set(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str | None,
        percent: int,
        auto_vest: bool | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "withdraw-routes", "set"], cli_named_options=extract_params(locals())
        )

    def process_withdraw_routes_remove(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str | None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "withdraw-routes", "remove"], cli_named_options=extract_params(locals())
        )

    def show_chain(self) -> Result:
        return self.__invoke_command_with_options(["show", "chain"])

    def __invoke_command_with_options(
        self,
        command: list[str],
        *,
        cli_positional_args: Iterable[StringConvertibleOptionTypes] | None = None,
        cli_named_options: Mapping[str, CliOptionT] | None = None,
        password_stdin: str | None = None,
    ) -> Result:
        positional = (
            [stringify_parameter_value(arg) for arg in cli_positional_args] if cli_positional_args is not None else []
        )
        named = build_cli_options(cli_named_options) if cli_named_options is not None else []
        full_command = [*command, *positional, *named]
        return self.invoke_raw_command(full_command, password_stdin)

    def process_transfer(  # noqa: PLR0913
        self,
        *,
        from_: str | None = None,
        to: str,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        memo: str | None = None,
        autosign: bool | None = None,
        amount: tt.Asset.HiveT | tt.Asset.HbdT,
    ) -> Result:
        return self.__invoke_command_with_options(["process", "transfer"], cli_named_options=extract_params(locals()))

    def configure_key_add(
        self,
        *,
        key: str,
        alias: str | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "key", "add"], cli_named_options=extract_params(locals())
        )

    def configure_key_remove(
        self,
        *,
        alias: str,
        from_beekeeper: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "key", "remove"], cli_named_options=extract_params(locals())
        )

    def configure_node_set(
        self,
        *,
        node_address: str,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "node", "set"], cli_named_options=extract_params(locals())
        )

    def unlock(
        self,
        *,
        profile_name: str | None = None,
        password_stdin: str | None = None,
    ) -> Result:
        named_params = locals()
        named_params.pop("password_stdin")
        return self.__invoke_command_with_options(
            ["unlock"], password_stdin=password_stdin, cli_named_options=extract_params(named_params)
        )

    def lock(self) -> Result:
        return self.__invoke_command_with_options(["lock"], cli_named_options=extract_params(locals()))

    def configure_working_account_switch(self, *, account_name: str) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "working-account", "switch"], cli_named_options=extract_params(locals())
        )

    def configure_tracked_account_add(self, *, account_name: str) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "tracked-account", "add"], cli_named_options=extract_params(locals())
        )

    def configure_tracked_account_remove(self, *, account_name: str) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "tracked-account", "remove"], cli_named_options=extract_params(locals())
        )

    def show_profile(self) -> Result:
        return self.__invoke_command_with_options(["show", "profile"], cli_named_options=extract_params(locals()))

    def show_profiles(self) -> Result:
        return self.__invoke_command_with_options(["show", "profiles"], cli_named_options=extract_params(locals()))

    def configure_known_account_add(self, *, account_name: str) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "known-account", "add"], cli_named_options=extract_params(locals())
        )

    def configure_known_account_remove(self, *, account_name: str) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "known-account", "remove"], cli_named_options=extract_params(locals())
        )

    def configure_known_account_enable(self) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "known-account", "enable"], cli_named_options=extract_params(locals())
        )

    def configure_known_account_disable(self) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "known-account", "disable"], cli_named_options=extract_params(locals())
        )

    def configure_profile_create(
        self,
        *,
        profile_name: str | None = None,
        password_stdin: str | None = None,
    ) -> Result:
        named_params = locals()
        named_params.pop("password_stdin")
        return self.__invoke_command_with_options(
            ["configure", "profile", "create"],
            password_stdin=password_stdin,
            cli_named_options=extract_params(named_params),
        )

    def configure_profile_delete(self, *, profile_name: str, force: bool | None = None) -> Result:
        return self.__invoke_command_with_options(
            ["configure", "profile", "delete"], cli_named_options=extract_params(locals())
        )

    def process_proxy_set(  # noqa: PLR0913
        self,
        *,
        proxy: str,
        account_name: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "proxy", "set"], cli_named_options=extract_params(locals())
        )

    def process_proxy_clear(
        self,
        *,
        account_name: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "proxy", "clear"], cli_named_options=extract_params(locals())
        )

    def process_transfer_schedule_create(  # noqa: PLR0913
        self,
        *,
        to: str,
        repeat: int,
        frequency: str,
        amount: tt.Asset.HiveT | tt.Asset.HbdT,
        pair_id: int = 0,
        from_: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        memo: str | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "transfer-schedule", "create"], cli_named_options=extract_params(locals())
        )

    def process_transfer_schedule_modify(  # noqa: PLR0913
        self,
        *,
        to: str,
        repeat: int | None = None,
        amount: tt.Asset.HiveT | tt.Asset.HbdT | None = None,
        frequency: str | None = None,
        pair_id: int | None = None,
        from_: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        memo: str | None = None,
        force: bool | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "transfer-schedule", "modify"], cli_named_options=extract_params(locals())
        )

    def process_transfer_schedule_remove(  # noqa: PLR0913
        self,
        *,
        to: str,
        from_: str | None = None,
        pair_id: int = 0,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "transfer-schedule", "remove"], cli_named_options=extract_params(locals())
        )

    def generate_key_from_seed(
        self,
        *,
        account_name: str,
        role: str,
        only_private_key: bool | None = None,
        only_public_key: bool | None = None,
        password_stdin: str | None = None,
    ) -> Result:
        named_params = locals()
        named_params.pop("password_stdin")
        return self.__invoke_command_with_options(
            ["generate", "key-from-seed"], password_stdin=password_stdin, cli_named_options=extract_params(named_params)
        )

    def generate_public_key(self, *, password_stdin: str | None = None) -> Result:
        return self.__invoke_command_with_options(["generate", "public-key"], password_stdin=password_stdin)

    def generate_random_key(self, *, key_pairs: int | None = None) -> Result:
        named_params = locals()
        return self.__invoke_command_with_options(
            ["generate", "random-key"], cli_named_options=extract_params(named_params)
        )

    def generate_secret_phrase(self) -> Result:
        return self.__invoke_command_with_options(["generate", "secret-phrase"])

    def process_claim_new_account_token(  # noqa: PLR0913
        self,
        *,
        account_name: str | None = None,
        fee: tt.Asset.HiveT | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "claim", "new-account-token"], cli_named_options=extract_params(locals())
        )

    def process_account_creation(  # noqa: PLR0913
        self,
        *args: StringConvertibleOptionTypes,
        creator: str | None = None,
        new_account_name: str | None = None,
        fee: bool | None = None,
        json_metadata: str | None = None,
        owner: PublicKey | None = None,
        active: PublicKey | None = None,
        posting: PublicKey | None = None,
        memo: PublicKey | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        return self.__invoke_command_with_options(
            ["process", "account-creation"],
            cli_positional_args=args,
            cli_named_options=extract_params(locals(), "args"),
        )

    def process_update_witness(  # noqa: PLR0913
        self,
        *,
        owner: str | None = None,
        use_witness_key: bool | None = None,
        account_creation_fee: tt.Asset.HiveT | None = None,
        maximum_block_size: int | None = None,
        hbd_interest_rate: Decimal | None = None,
        account_subsidy_budget: int | None = None,
        account_subsidy_decay: int | None = None,
        new_signing_key: PublicKey | None = None,
        hbd_exchange_rate: tt.Asset.HbdT | None = None,
        url: str | None = None,
        sign_with: str | None = None,
        broadcast: bool | None = None,
        save_file: Path | None = None,
        autosign: bool | None = None,
    ) -> Result:
        named_params = locals()
        # the actual option names are `--use-witness-key/--use-active-authority`
        if use_witness_key is False:
            named_params.pop("use_witness_key")
            named_params["use_active_authority"] = True
        return self.__invoke_command_with_options(
            ["process", "update-witness"], cli_named_options=extract_params(named_params)
        )
