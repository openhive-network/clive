from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel

from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.util import ExitCallHandler


def _get_default_profile_name() -> str | None:
    return ProfileData.get_lastly_used_profile_name()


def get_default_or_make_required(value: Any) -> Any:
    return ... if value is None else value


profile_option = typer.Option(
    get_default_or_make_required(_get_default_profile_name()),
    help="The profile to use.",
    show_default=bool(_get_default_profile_name()),
)


class PreconfiguredBaseModel(BaseModel):
    class Config:
        arbitrary_types_allowed: bool = True


class Common(PreconfiguredBaseModel):
    """
    Common options for some commands.
    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597
    """

    broadcast: bool = typer.Option(..., help="Broadcast the transaction.", show_default=False)
    profile: Optional[str] = profile_option
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.", show_default=False)
    save_file: Optional[str] = typer.Option(None, help="The file to save the transaction to.", show_default=False)
    world: World | None = None


def common_options(func: Callable[..., None]) -> Any:
    common = Common()

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


class WithWorld(PreconfiguredBaseModel):
    profile: Optional[str] = profile_option
    world: World

    @staticmethod
    def decorator(func: Callable[..., None]) -> Any:
        common = WithWorld.construct(world=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
        def wrapper(
            ctx: typer.Context,
            profile: Optional[str] = common.profile,
            **kwargs: Any,
        ) -> None:
            with ExitCallHandler(World(profile_name=profile), finally_callback=lambda w: w.close()) as world:
                ctx.params.update(world=world)
                return func(ctx=ctx, **kwargs)

        return wrapper
