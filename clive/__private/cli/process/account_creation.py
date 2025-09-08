from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, cast

import typer
from click import Context, pass_context

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.common import options
from clive.__private.cli.common.parameters import options  # noqa: F811
from clive.__private.cli.common.parameters.modified_param import modified_param
from clive.__private.core._async import asyncio_run
from clive.__private.core.constants.cli import (
    NEW_ACCOUNT_AUTHORITY_THRESOHLD,
    NEW_ACCOUNT_AUTHORITY_WEIGHT,
    WEIGHT_MARK,
)

if TYPE_CHECKING:
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation
    from clive.__private.cli.types import AuthorityType


type AccountWithWeight = tuple[str, int]
type KeyWithWeight = tuple[str, int]

account_creation = CliveTyper(name="account-creation", help="Account creation with token or fee.", chain=True)
EPILOG: Final[str] = "Look also at the help for `clive process account-creation` for more options."
KEYS_WITH_WEIGHT_METAVAR: Final[str] = (
    f"KEY[{WEIGHT_MARK}WEIGHT]\nExamples:\n"
    " --key STM1111111111111111111111111111111114T1Anm\n"
    f" --key STM1111111111111111111111111111111114T1Anm{WEIGHT_MARK}2"
)
ACCOUNTS_WITH_WEIGHT_METAVAR: Final[str] = (
    f"ACCOUNT[{WEIGHT_MARK}WEIGHT]\nExamples:\n --account alice\n --account alice{WEIGHT_MARK}2"
)


def _ensure_context_parent(ctx: Context) -> Context:
    assert ctx.parent, f"{ctx.command_path} context parent does not exist"
    return ctx.parent


def _get_command_from_context(ctx: Context) -> ProcessAccountCreation:
    from clive.__private.cli.commands.process.process_account_creation import ProcessAccountCreation  # noqa: PLC0415

    account_creation_command = ctx.obj
    assert isinstance(account_creation_command, ProcessAccountCreation), (
        f"{ctx.command_path} context object is not instance of ProcessAccountCreation"
    )
    return account_creation_command


def _account_with_weight(raw: str) -> AccountWithWeight:
    if WEIGHT_MARK in raw:
        key, weight_str = raw.split(WEIGHT_MARK, 1)
        try:
            weight = int(weight_str)
        except ValueError as e:
            raise typer.BadParameter(f"Weight must be an integer, got: {weight_str}") from e
        return key, weight
    return raw, NEW_ACCOUNT_AUTHORITY_WEIGHT


def _key_with_weight(raw: str) -> KeyWithWeight:
    if WEIGHT_MARK in raw:
        key, weight_str = raw.split(WEIGHT_MARK, 1)
        try:
            weight = int(weight_str)
        except ValueError as e:
            raise typer.BadParameter(f"Weight must be an integer, got: {weight_str}") from e
        return key, weight
    return raw, NEW_ACCOUNT_AUTHORITY_WEIGHT


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
        account_creation_command = _get_command_from_context(ctx)
        await account_creation_command.run()

    asyncio_run(send_account_creation_async())


def set_authority(
    ctx: typer.Context,
    type_: AuthorityType,
    threshold: int,
    keys_with_weight: list[tuple[str, int]],
    accounts_with_weight: list[tuple[str, int]],
) -> None:
    command = _get_command_from_context(_ensure_context_parent(ctx))
    command.set_threshold(type_, threshold)
    for key, weight in keys_with_weight:
        command.add_key_authority(type_, key, weight)
    for account_name, weight in accounts_with_weight:
        command.add_account_authority(type_, account_name, weight)


def set_memo_key(
    ctx: typer.Context,
    key: str,
) -> None:
    _get_command_from_context(_ensure_context_parent(ctx)).set_memo_key(key)


def modify_command_common_options(
    ctx: typer.Context,
    sign_with: str | None,
    broadcast: bool | None,  # noqa: FBT001
    save_file: str | None,
) -> None:
    _get_command_from_context(_ensure_context_parent(ctx)).modify_common_options(
        sign_with=sign_with, broadcast=broadcast, save_file=save_file
    )


@account_creation.callback(result_callback=send_account_creation)
async def process_account_creation(  # noqa: PLR0913
    ctx: typer.Context,
    creator: str = modified_param(options.working_account_template, param_decls=("--creator",)),
    new_account_name: str = typer.Option(
        ...,
        help="The name of the new account.",
    ),
    fee: bool = typer.Option(  # noqa: FBT001
        default=False,
        help="If set to true then account creation fee will be paid, you can check it with command `clive show chain`."
        " If set to false then new account token will be used.",
    ),
    json_metadata: str = typer.Option(
        "",
        help="The json metadata of the new account.",
    ),
    sign_with: str | None = options.sign_with,
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
    )
    ctx.obj = account_creation_command


@account_creation.command(name="owner", epilog=EPILOG)
async def specify_owner(  # noqa: PLR0913
    ctx: typer.Context,
    threshold: int = typer.Option(
        NEW_ACCOUNT_AUTHORITY_THRESOHLD,
        help="Set threshold for owner authority.",
        show_default=True,
    ),
    keys_with_weight: list[str] = typer.Option(
        [],
        "--key",
        parser=_key_with_weight,
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
        parser=_account_with_weight,
        help=(
            "The account to add as owner authority"
            f", with an optional weight specified after `{WEIGHT_MARK}` (default: 1)."
        ),
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    sign_with: str | None = options.sign_with,
    broadcast: bool | None = options.optional_broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify owner authority: keys or accounts with optional weights and threshold."""
    keys_with_weight_ = cast("list[KeyWithWeight]", keys_with_weight)
    accounts_with_weight_ = cast("list[AccountWithWeight]", accounts_with_weight)
    set_authority(ctx, "owner", threshold, keys_with_weight_, accounts_with_weight_)
    modify_command_common_options(ctx, sign_with, broadcast, save_file)


@account_creation.command(name="active", epilog=EPILOG)
async def specify_active(  # noqa: PLR0913
    ctx: typer.Context,
    threshold: int = typer.Option(
        NEW_ACCOUNT_AUTHORITY_THRESOHLD,
        help="Set threshold for active authority.",
        show_default=True,
    ),
    keys_with_weight: list[str] = typer.Option(
        [],
        "--key",
        parser=_key_with_weight,
        help="The public key to add as active authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    accounts_with_weight: list[str] = typer.Option(
        [],
        "--account",
        parser=_account_with_weight,
        help="The account to add as active authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    sign_with: str | None = options.sign_with,
    broadcast: bool | None = options.optional_broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify active authority: keys or accounts with optional weights and threshold."""
    keys_with_weight_ = cast("list[KeyWithWeight]", keys_with_weight)
    accounts_with_weight_ = cast("list[AccountWithWeight]", accounts_with_weight)
    set_authority(ctx, "active", threshold, keys_with_weight_, accounts_with_weight_)
    modify_command_common_options(ctx, sign_with, broadcast, save_file)


@account_creation.command(name="posting", epilog=EPILOG)
async def specify_posting(  # noqa: PLR0913
    ctx: typer.Context,
    threshold: int = typer.Option(
        NEW_ACCOUNT_AUTHORITY_THRESOHLD,
        help="Set threshold for posting authority.",
        show_default=True,
    ),
    keys_with_weight: list[str] = typer.Option(
        [],
        "--key",
        parser=_key_with_weight,
        help="The public key to add as posting authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=KEYS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    accounts_with_weight: list[str] = typer.Option(
        [],
        "--account",
        parser=_account_with_weight,
        help="The account to add as posting authority, with an optional weight specified after `=` (default: 1).",
        show_default=False,
        metavar=ACCOUNTS_WITH_WEIGHT_METAVAR,
    ),  # typer does not allow type "list[tuple[str, int]]" here so we use custom parser
    sign_with: str | None = options.sign_with,
    broadcast: bool | None = options.optional_broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify posting authority: keys or accounts with optional weights and threshold."""
    keys_with_weight_ = cast("list[KeyWithWeight]", keys_with_weight)
    accounts_with_weight_ = cast("list[AccountWithWeight]", accounts_with_weight)
    set_authority(ctx, "posting", threshold, keys_with_weight_, accounts_with_weight_)
    modify_command_common_options(ctx, sign_with, broadcast, save_file)


@account_creation.command(name="memo", epilog=EPILOG)
async def specify_memo(
    ctx: typer.Context,
    key: str = typer.Option(
        ...,
        "--key",
        help="Memo public key that will be set for account.",
        show_default=False,
    ),
    sign_with: str | None = options.sign_with,
    broadcast: bool | None = options.optional_broadcast,  # noqa: FBT001
    save_file: str | None = options.save_file,
) -> None:
    """Specify memo key."""
    set_memo_key(ctx, key)
    modify_command_common_options(ctx, sign_with, broadcast, save_file)
