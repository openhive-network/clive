from __future__ import annotations

from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters import modified_param
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.cli.common.parsers import public_key

if TYPE_CHECKING:
    from clive.__private.core.keys.keys import PublicKey

recovery_account = CliveTyper(
    name="recovery-account",
    help=(
        "Manage account recovery on the Hive blockchain.\n\n"
        "The recovery process consists of 3 steps:\n\n"
        "1. PREPARATION (change): Performed by the ACCOUNT OWNER."
        " Designates a trusted recovery account using owner authority."
        " Takes effect after a 30-day delay.\n\n"
        "2. REQUEST (request): Performed by the RECOVERY ACCOUNT."
        " Initiates recovery for a compromised account, proposing a new owner authority."
        " Requires active authority of the recovery account."
        " Creates a 24-hour window to complete recovery.\n\n"
        "3. RECOVERY (recover): Performed by the OWNER OF THE COMPROMISED ACCOUNT."
        " Confirms recovery by providing the new owner authority (matching the request)"
        " and a recent owner authority (valid within the last 30 days)."
        " Must be signed with keys satisfying both authorities."
        " Must be completed within 24 hours of the request."
    ),
)


@recovery_account.command(name="change")
async def process_change_recovery_account(  # noqa: PLR0913
    account_name: str = modified_param(
        options.working_account_template,
        help=stylized_help("The account for which recovery account changes.", is_working_account_default=True),
    ),
    new_recovery_account: str = typer.Option(
        ...,
        help="This is your trusted account. In case of compromise, only this account can create a recovery request.",
    ),
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Change recovery account. Should be signed with the owner authority.

    The operation changes your recovery account. It is important to keep it actual, because only a recovery account \
may create a request account recovery in case of compromised owner authority. The operation must be signed with \
owner authority. The change takes effect after a 30-day delay. If you want to cancel a pending change recovery \
account operation, you must create a new change_recovery_account_operation with --new-recovery-account set to the \
old one. If you want to remove recovery account you can set it to account 'null'. \
You can check pending operation with command `clive show pending change-recovery-account`.
    """
    from clive.__private.cli.commands.process.process_change_recovery_account import (  # noqa: PLC0415
        ProcessChangeRecoveryAccount,
    )

    await ProcessChangeRecoveryAccount(
        account_to_recover=account_name,
        new_recovery_account=new_recovery_account,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@recovery_account.command(name="request")
async def process_request_account_recovery(  # noqa: PLR0913
    recovery_account_name: str = modified_param(
        options.working_account_template,
        param_decls=("--recovery-account",),
        help=stylized_help(
            "The recovery account that initiates the recovery request.", is_working_account_default=True
        ),
    ),
    account_to_recover: str = typer.Option(
        ...,
        help="The account to be recovered.",
    ),
    new_owner_key: str = typer.Option(
        ...,
        "--new-owner-key",
        parser=public_key,
        help="The new owner public key to set for the recovered account.",
    ),
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Request account recovery. Should be signed with the active authority of the recovery account.

    The recovery account creates a recovery request for a compromised account, proposing a new owner authority. \
The request expires after 24 hours. \
You can check pending requests with command `clive show pending account-recovery`.
    """
    from clive.__private.cli.commands.process.process_request_account_recovery import (  # noqa: PLC0415
        ProcessRequestAccountRecovery,
    )

    new_owner_key_ = cast("PublicKey", new_owner_key)
    await ProcessRequestAccountRecovery(
        recovery_account=recovery_account_name,
        account_to_recover=account_to_recover,
        new_owner_key=new_owner_key_,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


@recovery_account.command(name="recover")
async def process_recover_account(  # noqa: PLR0913
    account_to_recover: str = modified_param(
        options.working_account_template,
        param_decls=("--account-to-recover",),
        help=stylized_help("The account to be recovered.", is_working_account_default=True),
    ),
    new_owner_key: str = typer.Option(
        ...,
        "--new-owner-key",
        parser=public_key,
        help="The new owner public key (must match the one from the active recovery request).",
    ),
    recent_owner_key: str = typer.Option(
        ...,
        "--recent-owner-key",
        parser=public_key,
        help="A recent owner public key (must have been valid within the last 30 days).",
    ),
    sign_with: list[str] = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Recover a compromised account. Must be signed with keys satisfying both new and recent owner authorities.

    Completes the recovery process by providing the new owner authority (matching the pending recovery request) \
and a recent owner authority (valid within the last 30 days). The new and recent owner authorities must differ. \
Must be completed within 24 hours of the recovery request.
    """
    from clive.__private.cli.commands.process.process_recover_account import ProcessRecoverAccount  # noqa: PLC0415

    new_owner_key_ = cast("PublicKey", new_owner_key)
    recent_owner_key_ = cast("PublicKey", recent_owner_key)
    await ProcessRecoverAccount(
        account_to_recover=account_to_recover,
        new_owner_key=new_owner_key_,
        recent_owner_key=recent_owner_key_,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()
