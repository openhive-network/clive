from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, Optional, ParamSpec

import typer
from merge_args import merge_args  # type: ignore[import]

from clive import World
from clive.__private.cli.common.base import PreconfiguredBaseModel
from clive.__private.cli.common.options import beekeeper_remote_option, profile_option
from clive.__private.util import ExitCallHandler
from clive.core.url import Url

P = ParamSpec("P")

PreWrapFuncT = Callable[Concatenate[typer.Context, P], None]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class OperationCommon(PreconfiguredBaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    profile: Optional[str] = profile_option
    sign: str = typer.Option(..., help="Key alias to sign the transaction with.", show_default=False)
    beekeeper_remote: Optional[str] = beekeeper_remote_option
    broadcast: bool = typer.Option(..., help="Broadcast the transaction.", show_default=False)
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.", show_default=False)
    world: World

    @staticmethod
    def decorator(func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
        common = OperationCommon.construct(world=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
        def wrapper(
            ctx: typer.Context,
            profile: Optional[str] = common.profile,
            sign: str = common.sign,  # noqa: ARG001
            beekeeper_remote: Optional[str] = common.beekeeper_remote,
            broadcast: bool = common.broadcast,  # noqa: ARG001
            save_file: Optional[str] = common.save_file,  # noqa: ARG001
            *args: P.args,
            **kwargs: Any,
        ) -> None:
            with ExitCallHandler(
                World(
                    profile_name=profile,
                    beekeeper_remote_endpoint=Url.parse(beekeeper_remote) if beekeeper_remote else None,
                ),
                finally_callback=lambda w: w.close(),
            ) as world:
                ctx.params.update(world=world)
                return func(ctx, *args, **kwargs)

        return wrapper  # type: ignore[no-any-return]
