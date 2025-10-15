from __future__ import annotations

from decimal import Decimal  # noqa: TC003
from functools import partial
from typing import TYPE_CHECKING, cast

import typer

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters import argument_related_options, arguments, modified_param
from clive.__private.cli.common.parameters.ensure_single_value import (
    EnsureSingleValue,
)
from clive.__private.cli.common.parameters.styling import stylized_help
from clive.__private.cli.common.parsers import decimal_percent, hbd_asset, hive_asset, public_key
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
from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.core.types import AlreadySignedMode  # noqa: TC001

if TYPE_CHECKING:
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.models.asset import Asset

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


@process.command(name="transaction")
async def process_transaction(  # noqa: PLR0913
    from_file: str = typer.Option(..., help="The file to load the transaction from."),
    force_unsign: bool = typer.Option(default=False, help="Whether to force unsigning the transaction."),  # noqa: FBT001
    already_signed_mode: AlreadySignedMode = typer.Option(
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
        already_signed_mode=already_signed_mode,
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
    help=stylized_help("The name of the new account.", required_as_arg_or_option=True),
)


@process.command(name="account-creation")
async def process_account_creation(  # noqa: PLR0913
    creator: str = modified_param(options.working_account_template, param_decls=("--creator",)),
    new_account_name: str | None = _new_account_name_argument,
    new_account_name_option: str | None = argument_related_options.new_account_name,
    owner: str | None = arguments.owner_key,
    active: str | None = arguments.active_key,
    posting: str | None = arguments.posting_key,
    memo: str | None = arguments.memo_key,
    owner_option: str | None = argument_related_options.owner_key,
    active_option: str | None = argument_related_options.active_key,
    posting_option: str | None = argument_related_options.posting_key,
    memo_option: str | None = argument_related_options.memo_key,
    fee: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="If set to true then account creation fee will be paid, you can check it with command `clive show chain`."
        " If set to false then new account token will be used.",
    ),
    json_metadata: str = typer.Option(
        "",
        "--json-metadata",
        help=stylized_help("The json metadata of the new account passed as string.", default="empty string"),
        show_default=True,
    ),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """
    A simple account creation command that allows to create a new account with authority specified via 4 public keys.

    Thresholds and weights have default values of 1 and 1.

    Example:
    1) positional
    clive process account-creation --fee <new-account-name> <owner-key> <active-key> <posting-key> <memo-key>
    2) named options
    clive process account-creation --fee --new-account-name <new-account-name> --owner <owner-key> \
--active <active-key> --posting <posting-key> --memo <memo-key>
    """
    # indentation matters in docstring as this is displayed to user as help for cli commands
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation  # noqa: PLC0415
    from clive.__private.core.keys.keys import PublicKey  # noqa: PLC0415

    owner_ = cast("PublicKey | None", owner)
    active_ = cast("PublicKey | None", active)
    posting_ = cast("PublicKey | None", posting)
    memo_ = cast("PublicKey | None", memo)

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
        EnsureSingleValue[PublicKey]("owner").of(owner_, owner_option_),
        EnsureSingleValue[PublicKey]("active").of(active_, active_option_),
        EnsureSingleValue[PublicKey]("posting").of(posting_, posting_option_),
    )
    account_creation_command.set_memo_key(EnsureSingleValue[PublicKey]("memo").of(memo_, memo_option_))
    await account_creation_command.run()


@process.command(name="update-witness")
async def process_witness_update(  # noqa: PLR0913
    witness_name: str = modified_param(
        options.working_account_template,
        help=stylized_help("Witness account name, aka owner in the operation.", is_working_account_default=True),
    ),
    use_witness_key: bool = typer.Option(  # noqa: FBT001
        True,  # noqa: FBT003
        "--use-witness-key/--use-active-authority",
        help=(
            "There are 3 operations for updating the witness properties. By default,"
            " `witness_set_properties` is used and a witness key is required to sign such a transaction."
            " Alternatively, active authority can be used with operations `witness_update` and `feed_publish`."
        ),
    ),
    account_creation_fee: str | None = typer.Option(
        None,
        parser=hive_asset,
        help="Fee paid by creator of new account, applies also to price of new account tokens.",
    ),
    maximum_block_size: int | None = typer.Option(
        None,
        help="Block size (in bytes) that cannot be exceeded.",
    ),
    hbd_interest_rate: Decimal | None = typer.Option(
        None,
        help="Interest paid when hbd is in savings, in percent (0.00-100.00).",
        parser=decimal_percent,
    ),
    account_subsidy_budget: int | None = typer.Option(None, help="Requires to be signed with witness key."),
    account_subsidy_decay: int | None = typer.Option(None, help="Requires to be signed with witness key."),
    new_signing_key: str | None = typer.Option(
        None,
        help="New witness public key.",
        parser=public_key,
    ),
    hbd_exchange_rate: str | None = typer.Option(
        None,
        parser=hbd_asset,
        help="Updated price value of 1 HIVE in HBD.",
    ),
    url: str | None = typer.Option(None, help="New witness url."),
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool = options.broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Update witness properties with witness update, feed publish or witness set properties operation."""
    from clive.__private.cli.commands.process.process_update_witness import ProcessUpdateWitness  # noqa: PLC0415

    account_creation_fee_ = cast("Asset.Hive | None", account_creation_fee)
    new_signing_key_ = cast("PublicKey | None", new_signing_key)
    hbd_exchange_rate_ = cast("Asset.Hbd | None", hbd_exchange_rate)
    operation = ProcessUpdateWitness(
        owner=witness_name,
        use_witness_key=use_witness_key,
        account_creation_fee=account_creation_fee_,
        maximum_block_size=maximum_block_size,
        hbd_interest_rate=hbd_interest_rate,
        account_subsidy_budget=account_subsidy_budget,
        account_subsidy_decay=account_subsidy_decay,
        new_signing_key=new_signing_key_,
        hbd_exchange_rate=hbd_exchange_rate_,
        url=url,
        sign_with=sign_with,
        broadcast=broadcast,
        save_file=save_file,
        autosign=autosign,
    )
    await operation.run()
