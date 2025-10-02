from __future__ import annotations

from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters import argument_related_options, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import (
    EnsureSingleValue,
)
from clive.__private.cli.common.parsers import public_key
from clive.__private.cli.process.claim import claim
from clive.__private.cli.process.custom_operations.custom_json import custom_json
from clive.__private.cli.process.hive_power.delegations import delegations
from clive.__private.cli.process.hive_power.power_down import power_down
from clive.__private.cli.process.hive_power.power_up import power_up
from clive.__private.cli.process.hive_power.withdraw_routes import withdraw_routes
from clive.__private.cli.process.proxy import proxy
from clive.__private.cli.process.savings import savings
from clive.__private.cli.process.transfer_schedule import transfer_schedule
from clive.__private.cli.process.update_authority import get_update_authority_typer
from clive.__private.cli.process.vote_proposal import vote_proposal
from clive.__private.cli.process.vote_witness import vote_witness
from clive.__private.core.constants.cli import (
    DEFAULT_AUTHORITY_THRESHOLD,
    DEFAULT_AUTHORITY_WEIGHT,
    FOUR_PUBLIC_KEYS_METAVAR,
    REQUIRED_AS_ARG_OR_OPTION,
)
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT, ALREADY_SIGNED_MODES

if TYPE_CHECKING:
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.models import Asset

process = CliveTyper(name="process", help="Process something (e.g. perform a transfer).")

process.add_typer(claim)
process.add_typer(proxy)
process.add_typer(savings)
process.add_typer(get_update_authority_typer("owner"))
process.add_typer(get_update_authority_typer("active"))
process.add_typer(get_update_authority_typer("posting"))
process.add_typer(vote_proposal)
process.add_typer(vote_witness)
process.add_typer(delegations)
process.add_typer(power_down)
process.add_typer(power_up)
process.add_typer(withdraw_routes)
process.add_typer(transfer_schedule)
process.add_typer(custom_json)


@process.command(name="transfer")
async def transfer(  # noqa: PLR0913
    from_account: str = options.from_account_name,
    to: str = typer.Option(..., help="The account to transfer to."),
    amount: str = options.liquid_amount,
    memo: str = options.memo_value,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Transfer some funds to another account."""
    from clive.__private.cli.commands.process.transfer import Transfer  # noqa: PLC0415

    amount_ = cast("Asset.LiquidT", amount)
    await Transfer(
        from_account=from_account,
        to=to,
        amount=amount_,
        memo=memo,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    ).run()


# unfortunately typer doesn't support Literal types yet, so we have to convert it to an enum
AlreadySignedModeEnum = Enum(  # type: ignore[misc]
    "AlreadySignedModeEnum", {option: option for option in ALREADY_SIGNED_MODES}
)


@process.command(name="transaction")
async def process_transaction(  # noqa: PLR0913
    from_file: str = typer.Option(..., help="The file to load the transaction from."),
    force_unsign: bool = typer.Option(default=False, help="Whether to force unsigning the transaction."),  # noqa: FBT001
    already_signed_mode: AlreadySignedModeEnum = typer.Option(
        ALREADY_SIGNED_MODE_DEFAULT,
        help=(
            "How to handle situations when a transaction is already signed.\n\n "
            "In 'strict' mode for: \n\n"
            "- '--sign-with': an error is raised, \n\n"
            "- '--autosign': a warning is shown, but will continue."
            ""
        ),
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
    force: bool = options.force_value,  # noqa: FBT001
) -> None:
    """Process a transaction from file."""
    from clive.__private.cli.commands.process.process_transaction import ProcessTransaction  # noqa: PLC0415

    await ProcessTransaction(
        from_file=from_file,
        force_unsign=force_unsign,
        already_signed_mode=already_signed_mode.value,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        force=force,
        autosign=autosign,
    ).run()


@process.command(name="update-memo-key")
async def process_update_memo_key(  # noqa: PLR0913
    account_name: str = options.account_name,
    memo_key: str = typer.Option(
        ...,
        "--key",
        help="New memo public key that will be set for account.",
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Set memo key."""
    from clive.__private.cli.commands.process.process_account_update import (  # noqa: PLC0415
        ProcessAccountUpdate,
        set_memo_key,
    )

    update_memo_key_callback = partial(set_memo_key, key=memo_key)

    operation = ProcessAccountUpdate(
        account_name=account_name, sign_with=sign_with, broadcast=broadcast, save_file=save_file, autosign=autosign
    )
    operation.add_callback(update_memo_key_callback)
    await operation.run()


_new_account_name_argument = typer.Argument(
    None,
    help=f"The name of the new profile. ({REQUIRED_AS_ARG_OR_OPTION})",
)


@process.command(name="account-creation")
async def process_account_creation(  # noqa: PLR0913
    creator: str = modified_param(options.working_account_template, param_decls=("--creator",)),
    new_account_name: str | None = _new_account_name_argument,
    new_account_name_option: str | None = argument_related_options.new_account_name,
    keys: tuple[str, str, str, str] | None = typer.Argument(
        None,
        parser=public_key,
        help="Specify owner, active, posting and memo public keys, separated by space. Thresholds and weights"
        f" have default values of {DEFAULT_AUTHORITY_THRESHOLD} and {DEFAULT_AUTHORITY_WEIGHT}.",
        metavar=FOUR_PUBLIC_KEYS_METAVAR,
    ),
    owner_option: str | None = typer.Option(
        None,
        "--owner",
        parser=public_key,
        help="Owner public key that will be set for account.",
    ),
    active_option: str | None = typer.Option(
        None,
        "--active",
        parser=public_key,
        help="Active public key that will be set for account.",
    ),
    posting_option: str | None = typer.Option(
        None,
        "--posting",
        parser=public_key,
        help="Posting public key that will be set for account.",
    ),
    memo_option: str | None = typer.Option(
        None,
        "--memo",
        parser=public_key,
        help="Memo public key that will be set for account.",
    ),
    fee: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="If set to true then account creation fee will be paid, you can check it with command `clive show chain`."
        " If set to false then new account token will be used. Default is false.",
    ),
    json_metadata: str = typer.Option(
        "",
        "--json-metadata",
        help="The json metadata of the new account passed as string. Default is empty string.",
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    Simplified version of command for account creation where only 4 keys are required.

    Example: clive process account-creation  "alice-$(date +%s)" --fee
    STM4xDsaG7wZu8gENJLC1GyVmorPGZrJePwazZsgcThWWnfkQKVbx
    STM4xDsaG7wZu8gENJLC1GyVmorPGZrJePwazZsgcThWWnfkQKVbx
    STM4xDsaG7wZu8gENJLC1GyVmorPGZrJePwazZsgcThWWnfkQKVbx
    STM4xDsaG7wZu8gENJLC1GyVmorPGZrJePwazZsgcThWWnfkQKVbx
    """
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation  # noqa: PLC0415
    from clive.__private.core.keys.keys import PublicKey  # noqa: PLC0415

    if keys is not None:
        owner, active, posting, memo = (cast("PublicKey", key) for key in keys)
    else:
        # because in typer complex tuple types are not supported
        owner, active, posting, memo = None, None, None, None
    owner_option_ = cast("PublicKey | None", owner_option)
    active_option_ = cast("PublicKey | None", active_option)
    posting_option_ = cast("PublicKey | None", posting_option)
    memo_option_ = cast("PublicKey | None", memo_option)

    account_creation_command = ProcessAccountCreation(
        creator=creator,
        new_account_name=EnsureSingleValue("new-account-name").of(new_account_name, new_account_name_option),
        fee=fee,
        json_metadata=json_metadata,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    )
    account_creation_command.set_keys(
        EnsureSingleValue[PublicKey]("owner").of(owner, owner_option_),
        EnsureSingleValue[PublicKey]("active").of(active, active_option_),
        EnsureSingleValue[PublicKey]("posting").of(posting, posting_option_),
    )
    account_creation_command.set_memo_key(EnsureSingleValue[PublicKey]("memo").of(memo, memo_option_))
    await account_creation_command.run()
