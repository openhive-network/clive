from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, cast

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.get_command_from_context import get_process_account_creation_command
from clive.__private.cli.common.parameters import options  # noqa: F811
from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.cli.common.parsers import account_with_weight, key_with_weight, public_key
from clive.__private.core._async import asyncio_run
from clive.__private.core.constants.cli import (
    ACCOUNTS_WITH_WEIGHT_METAVAR,
    DEFAULT_AUTHORITY_THRESOHLD,
    KEYS_WITH_WEIGHT_METAVAR,
    WEIGHT_MARK,
)

if TYPE_CHECKING:
    from clive.__private.cli.types import AccountWithWeight, KeyWithWeight
    from clive.__private.core.keys.keys import PublicKey

account_creation = CliveTyper(
    name="account-creation", help="Create an account using a token or by paying a fee.", chain=True
)
EPILOG: Final[str] = "Look also at the help for `clive process account-creation` for more options."


@pass_context
def send_account_creation(ctx: Context, /, *args: Any, **kwargs: Any) -> None:  # noqa: ARG001
    """
    Create and send account create operation or create claimed account operation.

    Args:
        ctx: The context of the command.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments.
    """

    async def send_account_creation_async() -> None:
        account_creation_command = get_process_account_creation_command(ctx)
        await account_creation_command.run()

    asyncio_run(send_account_creation_async())


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


@account_creation.callback(invoke_without_command=True, result_callback=send_account_creation)
async def process_account_creation(  # noqa: PLR0913
    ctx: typer.Context,
    creator: str = modified_param(options.working_account_template, param_decls=("--creator",)),
    new_account_name: str | None = _new_account_name_option,
    fee: bool | None = _fee,  # noqa: FBT001
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
    ctx.obj = account_creation_command


@account_creation.command(name="owner", epilog=EPILOG)
async def specify_owner(  # noqa: PLR0913
    ctx: typer.Context,
    threshold: int = typer.Option(
        DEFAULT_AUTHORITY_THRESOHLD,
        help="Set threshold for owner authority.",
        show_default=True,
    ),
    keys_with_weight: list[str] = typer.Option(
        [],
        "--key",
        parser=key_with_weight,
        help=(
            "The public key to add as owner authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    accounts_with_weight: list[str] = typer.Option(
        [],
        "--account",
        parser=account_with_weight,
        help=(
            "The account to add as owner authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    new_account_name: str | None = _new_account_name_option,
    fee: bool | None = _fee,  # noqa: FBT001
    json_metadata: str | None = _json_metadata,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast_optional,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify owner authority: keys or accounts with optional weights and threshold."""
    keys_with_weight_ = cast("list[KeyWithWeight]", keys_with_weight)
    accounts_with_weight_ = cast("list[AccountWithWeight]", accounts_with_weight)
    command = get_process_account_creation_command(ctx)
    command.add_authority("owner", threshold, keys_with_weight_, accounts_with_weight_)
    command.modify_account_creation_common_options(
        new_account_name, fee, json_metadata, sign_with, autosign, broadcast, save_file
    )


@account_creation.command(name="active", epilog=EPILOG)
async def specify_active(  # noqa: PLR0913
    ctx: typer.Context,
    threshold: int = typer.Option(
        DEFAULT_AUTHORITY_THRESOHLD,
        help="Set threshold for active authority.",
        show_default=True,
    ),
    keys_with_weight: list[str] = typer.Option(
        [],
        "--key",
        parser=key_with_weight,
        help="The public key to add as active authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    accounts_with_weight: list[str] = typer.Option(
        [],
        "--account",
        parser=account_with_weight,
        help="The account to add as active authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    new_account_name: str | None = _new_account_name_option,
    fee: bool | None = _fee,  # noqa: FBT001
    json_metadata: str | None = _json_metadata,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast_optional,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify active authority: keys or accounts with optional weights and threshold."""
    keys_with_weight_ = cast("list[KeyWithWeight]", keys_with_weight)
    accounts_with_weight_ = cast("list[AccountWithWeight]", accounts_with_weight)
    command = get_process_account_creation_command(ctx)
    command.add_authority("active", threshold, keys_with_weight_, accounts_with_weight_)
    command.modify_account_creation_common_options(
        new_account_name, fee, json_metadata, sign_with, autosign, broadcast, save_file
    )


@account_creation.command(name="posting", epilog=EPILOG)
async def specify_posting(  # noqa: PLR0913
    ctx: typer.Context,
    threshold: int = typer.Option(
        DEFAULT_AUTHORITY_THRESOHLD,
        help="Set threshold for posting authority.",
        show_default=True,
    ),
    keys_with_weight: list[str] = typer.Option(
        [],
        "--key",
        parser=key_with_weight,
        help="The public key to add as posting authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    accounts_with_weight: list[str] = typer.Option(
        [],
        "--account",
        parser=account_with_weight,
        help="The account to add as posting authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    new_account_name: str | None = _new_account_name_option,
    fee: bool | None = _fee,  # noqa: FBT001
    json_metadata: str | None = _json_metadata,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast_optional,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify posting authority: keys or accounts with optional weights and threshold."""
    keys_with_weight_ = cast("list[KeyWithWeight]", keys_with_weight)
    accounts_with_weight_ = cast("list[AccountWithWeight]", accounts_with_weight)
    command = get_process_account_creation_command(ctx)
    command.add_authority("posting", threshold, keys_with_weight_, accounts_with_weight_)
    command.modify_account_creation_common_options(
        new_account_name, fee, json_metadata, sign_with, autosign, broadcast, save_file
    )


@account_creation.command(name="memo", epilog=EPILOG)
async def specify_memo(  # noqa: PLR0913
    ctx: typer.Context,
    key: str = typer.Option(
        ...,
        "--key",
        parser=public_key,
        help="Memo public key that will be set for account.",
        show_default=False,
    ),
    new_account_name: str | None = _new_account_name_option,
    fee: bool | None = _fee,  # noqa: FBT001
    json_metadata: str | None = _json_metadata,
    sign_with: str | None = options.sign_with,
    autosign: bool | None = options.autosign,  # noqa: FBT001
    broadcast: bool | None = options.broadcast_optional,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify memo key."""
    key_ = cast("PublicKey", key)
    command = get_process_account_creation_command(ctx)
    command.set_memo_key(key_)
    command.modify_account_creation_common_options(
        new_account_name, fee, json_metadata, sign_with, autosign, broadcast, save_file
    )
