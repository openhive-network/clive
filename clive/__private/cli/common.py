from abc import ABC
from collections.abc import Callable
from functools import wraps
from typing import Any, Concatenate, Optional, ParamSpec

import typer
from merge_args import merge_args  # type: ignore
from pydantic import BaseModel

from clive.__private.core.profile_data import ProfileData
from clive.__private.core.world import World
from clive.__private.util import ExitCallHandler
from clive.core.url import Url

P = ParamSpec("P")


def _get_default_profile_name() -> str | None:
    return ProfileData.get_lastly_used_profile_name()


def get_default_or_make_required(value: Any) -> Any:
    return ... if value is None else value


profile_option = typer.Option(
    get_default_or_make_required(_get_default_profile_name()),
    help="The profile to use.",
    show_default=bool(_get_default_profile_name()),
)

beekeeper_remote_option = typer.Option(None, help="Beekeeper remote endpoint.", show_default=False)


class PreconfiguredBaseModel(BaseModel, ABC):
    class Config:
        arbitrary_types_allowed: bool = True

    @staticmethod
    def decorator(func: Callable[..., None]) -> Any:
        """Should be overridden in subclasses."""


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


PreWrapFuncT = Callable[Concatenate[typer.Context, P], None]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class WithWorld(PreconfiguredBaseModel):
    profile: Optional[str] = profile_option
    world: World

    @staticmethod
    def decorator(*, use_beekeeper: bool = True) -> Callable[[PreWrapFuncT[P]], PostWrapFuncT[P]]:  # type: ignore[override]
        """
        Decorator to be used on commands that need a world. The world could be created with a beekeeper or without.
        Beekeeper is launched locally by default, but it is possible to use a remote beekeeper by specifying the
        `beekeeper_remote` argument in the decorated function.

        Params:
            use_beekeeper: Set this to False when there is no need to use a beekeeper.
        """

        def outer(func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
            common = WithWorld.construct(world=None)  # type: ignore[arg-type]

            @merge_args(func)
            @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
            def inner(
                ctx: typer.Context,
                profile: Optional[str] = common.profile,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                def _get_beekeeper_remote() -> Url | None:
                    beekeeper_remote: str | None = kwargs.get("beekeeper_remote", None)  # type: ignore[assignment]
                    return Url.parse(beekeeper_remote) if beekeeper_remote else None

                beekeeper_remote_endpoint = _get_beekeeper_remote()

                typer.echo(
                    "Launching beekeeper..."
                    if not beekeeper_remote_endpoint
                    else f"Using beekeeper at {beekeeper_remote_endpoint}"
                )

                with ExitCallHandler(
                    World(
                        profile_name=profile,
                        use_beekeeper=use_beekeeper,
                        beekeeper_remote_endpoint=beekeeper_remote_endpoint,
                    ),
                    finally_callback=lambda w: w.close(),
                ) as world:
                    ctx.params.update(world=world)
                    return func(ctx, *args, **kwargs)

            return inner  # type: ignore[no-any-return]

        return outer
