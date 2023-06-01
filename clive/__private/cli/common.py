from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel

from clive.__private import config
from clive.__private.core.world import World
from clive.__private.util import ExitCallHandler


class Common(BaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    broadcast: bool = typer.Option(False, help="Broadcast the transaction.", show_default=False)
    profile: str = typer.Option(..., help="The profile to use.")
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.")
    password: Optional[str] = typer.Option(None, help="The password to use.")
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.")
    chain_id: Optional[str] = typer.Option(None, help="Chain id used for signatures")
    world: World | None = None

    class Config:
        arbitrary_types_allowed: bool = True


def common_options(func: Callable[..., None]) -> Any:
    common = Common()

    @merge_args(func)
    @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
    def wrapper(
        ctx: typer.Context,
        broadcast: bool = common.broadcast,  # noqa: ARG001
        sign: Optional[str] = common.sign,  # noqa: ARG001
        profile: str = common.profile,
        password: Optional[str] = common.password,  # noqa: ARG001
        save_file: Optional[str] = common.save_file,  # noqa: ARG001
        chain_id: Optional[str] = common.chain_id,
        **kwargs: Any,
    ) -> None:
        with ExitCallHandler(World(profile_name=profile), finally_callback=lambda w: w.close()) as world:
            if chain_id is not None:
                config.settings["node.chain_id"] = chain_id
            ctx.params.update(world=world)
            return func(ctx=ctx, **kwargs)

    return wrapper
