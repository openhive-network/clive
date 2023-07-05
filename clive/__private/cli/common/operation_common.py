from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive import World
from clive.__private.cli.common.base import PreconfiguredBaseModel
from clive.__private.cli.common.options import profile_option
from clive.__private.util import ExitCallHandler


class OperationCommon(PreconfiguredBaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    broadcast: bool = typer.Option(..., help="Broadcast the transaction.", show_default=False)
    profile: Optional[str] = profile_option
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.", show_default=False)
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.", show_default=False)
    world: World | None = None

    @staticmethod
    def decorator(func: Callable[..., None]) -> Any:
        common = OperationCommon()

        @merge_args(func)
        @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
        def wrapper(
            ctx: typer.Context,
            broadcast: bool = common.broadcast,  # noqa: ARG001
            sign: Optional[str] = common.sign,  # noqa: ARG001
            profile: Optional[str] = common.profile,
            save_file: Optional[str] = common.save_file,  # noqa: ARG001
            **kwargs: Any,
        ) -> None:
            with ExitCallHandler(World(profile_name=profile), finally_callback=lambda w: w.close()) as world:
                ctx.params.update(world=world)
                return func(ctx=ctx, **kwargs)

        return wrapper
