from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, Concatenate, Optional, ParamSpec

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel
from clive.__private.cli_error import CLIError
from clive.__private.core._async import asyncio_run
from clive.__private.core.commands.activate import ActivateInvalidPasswordError

if TYPE_CHECKING:
    from clive.__private.core.world import World


P = ParamSpec("P")

PreWrapFuncT = Callable[Concatenate[typer.Context, P], Awaitable[None]]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class OperationCommon(CommonBaseModel):
    """
    Common options for some commands.

    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597.
    """

    profile: str = options.profile_option
    password: str = typer.Option(..., help="Password to unlock the wallet.", show_default=False)
    sign: str = typer.Option(..., help="Key alias to sign the transaction with.", show_default=False)
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option
    broadcast: bool = typer.Option(True, help="Whether broadcast the transaction. (i.e. dry-run)")
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.", show_default=False)
    world: "World"

    @classmethod
    def decorator(cls, func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
        common = cls.construct(world=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
        def wrapper(
            ctx: typer.Context,
            profile: str = common.profile,
            password: str = common.password,
            sign: str = common.sign,  # noqa: ARG001
            beekeeper_remote: Optional[str] = common.beekeeper_remote,
            broadcast: bool = common.broadcast,
            save_file: Optional[str] = common.save_file,  # noqa: ARG001
            *args: P.args,
            **kwargs: Any,
        ) -> None:
            from clive.__private.core.world import TyperWorld
            from clive.core.url import Url

            if not broadcast:
                typer.echo("[Performing dry run, because --no-broadcast was specified.]\n")

            beekeeper_remote_endpoint = Url.parse(beekeeper_remote) if beekeeper_remote else None

            cls._print_launching_beekeeper(beekeeper_remote_endpoint)

            async def impl() -> None:
                async with TyperWorld(
                    profile_name=profile,
                    beekeeper_remote_endpoint=beekeeper_remote_endpoint,
                ) as world:
                    cls._assert_correct_profile_is_loaded(world.profile_data.name, profile)
                    ctx.params.update(world=world)
                    try:
                        await world.commands.activate(password=password)
                    except ActivateInvalidPasswordError:
                        raise CLIError("Invalid password.") from None
                    await func(ctx, *args, **kwargs)

            asyncio_run(impl())

        return wrapper  # type: ignore[no-any-return]

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401

        OperationCommon.update_forward_refs(**locals())
