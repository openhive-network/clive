from collections.abc import Callable
from functools import wraps
from typing import Concatenate, Optional, ParamSpec

import typer
from merge_args import merge_args  # type: ignore[import]

from clive import World
from clive.__private.cli.common.base import PreconfiguredBaseModel
from clive.__private.cli.common.options import profile_option
from clive.__private.util import ExitCallHandler
from clive.core.url import Url

P = ParamSpec("P")

PreWrapFuncT = Callable[Concatenate[typer.Context, P], None]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class WithWorld(PreconfiguredBaseModel):
    profile: Optional[str] = profile_option
    world: World

    @classmethod
    def decorator(cls, *, use_beekeeper: bool = True) -> Callable[[PreWrapFuncT[P]], PostWrapFuncT[P]]:  # type: ignore[override]
        """
        Decorator to be used on commands that need a world. The world could be created with a beekeeper or without.
        Beekeeper is launched locally by default, but it is possible to use a remote beekeeper by specifying the
        `beekeeper_remote` argument in the decorated function.

        Params:
            use_beekeeper: Set this to False when there is no need to use a beekeeper.
        """

        def outer(func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
            common = cls.construct(world=None)  # type: ignore[arg-type]

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
