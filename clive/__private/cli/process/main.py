from __future__ import annotations

from enum import Enum
from functools import partial
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
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
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT, ALREADY_SIGNED_MODES

if TYPE_CHECKING:
    from clive.__private.models import Asset


from typing import TYPE_CHECKING

from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.cli.common.parsers import account_with_weight, key_with_weight, public_key
from clive.__private.core.constants.cli import (
    ACCOUNTS_WITH_WEIGHT_METAVAR,
    DEFAULT_AUTHORITY_THRESOHLD,
    KEYS_WITH_WEIGHT_METAVAR,
    WEIGHT_MARK,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountWithWeight, KeyWithWeight
    from clive.__private.core.keys.keys import PublicKey


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


_new_account_name_option = typer.Option(
    None,
    "--new-account-name",
    help="The name of the new account. Required at least on one of command/subcommands.",
)
_fee = typer.Option(
    None,
    help="If set to true then account creation fee will be paid, you can check it with command `clive show chain`."
    " If set to false then new account token will be used. Default is false.",
)
_json_metadata = typer.Option(
    None,
    "--json-metadata",
    help="The json metadata of the new account passed as string. Default is empty string.",
)


@process.command(name="account-creation")
async def process_account_creation(  # noqa: PLR0913
    creator: str = modified_param(options.working_account_template, param_decls=("--creator",)),
    owner_threshold: int = typer.Option(
        DEFAULT_AUTHORITY_THRESOHLD,
        help="Set threshold for owner authority.",
        show_default=True,
    ),
    owner_keys_with_weight: list[str] = typer.Option(
        [],
        "--owner-key",
        parser=key_with_weight,
        help=(
            "The public key to add as owner authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    owner_accounts_with_weight: list[str] = typer.Option(
        [],
        "--owner-account",
        parser=account_with_weight,
        help=(
            "The account to add as owner authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    active_threshold: int = typer.Option(
        DEFAULT_AUTHORITY_THRESOHLD,
        help="Set threshold for active authority.",
        show_default=True,
    ),
    active_keys_with_weight: list[str] = typer.Option(
        [],
        "--active-key",
        parser=key_with_weight,
        help=(
            "The public key to add as active authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    active_accounts_with_weight: list[str] = typer.Option(
        [],
        "--active-account",
        parser=account_with_weight,
        help=(
            "The account to add as active authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    posting_threshold: int = typer.Option(
        DEFAULT_AUTHORITY_THRESOHLD,
        help="Set threshold for posting authority.",
        show_default=True,
    ),
    posting_keys_with_weight: list[str] = typer.Option(
        [],
        "--posting-key",
        parser=key_with_weight,
        help=(
            "The public key to add as posting authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    posting_accounts_with_weight: list[str] = typer.Option(
        [],
        "--posting-account",
        parser=account_with_weight,
        help=(
            "The account to add as posting authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    memo: str = typer.Option(
        ...,
        parser=public_key,
        help=("The public key to add as memo key"),
        show_default=False,
    ),
    new_account_name: str = _new_account_name_option,
    fee: bool = _fee,  # noqa: FBT001
    json_metadata: str | None = _json_metadata,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Create new account."""
    from clive.__private.cli.commands.process.process_account_creation import (  # noqa: PLC0415
        ProcessAccountCreation,
    )

    owner_keys_with_weight_ = cast("list[KeyWithWeight]", owner_keys_with_weight)
    owner_accounts_with_weight_ = cast("list[AccountWithWeight]", owner_accounts_with_weight)
    active_keys_with_weight_ = cast("list[KeyWithWeight]", active_keys_with_weight)
    active_accounts_with_weight_ = cast("list[AccountWithWeight]", active_accounts_with_weight)
    posting_keys_with_weight_ = cast("list[KeyWithWeight]", posting_keys_with_weight)
    posting_accounts_with_weight_ = cast("list[AccountWithWeight]", posting_accounts_with_weight)
    memo_ = cast("PublicKey", memo)

    account_creation_command = ProcessAccountCreation(
        creator=creator,
        new_account_name=new_account_name,
        fee=fee,
        json_metadata=json_metadata,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    )
    account_creation_command.add_authority(
        "owner", owner_threshold, owner_keys_with_weight_, owner_accounts_with_weight_
    )
    account_creation_command.add_authority(
        "active", active_threshold, active_keys_with_weight_, active_accounts_with_weight_
    )
    account_creation_command.add_authority(
        "posting", posting_threshold, posting_keys_with_weight_, posting_accounts_with_weight_
    )
    account_creation_command.set_memo_key(memo_)

    await account_creation_command.run()
