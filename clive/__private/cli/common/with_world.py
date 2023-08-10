from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TYPE_CHECKING, Concatenate, ParamSpec

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive.core.url import Url


P = ParamSpec("P")

PreWrapFuncT = Callable[Concatenate[typer.Context, P], Awaitable[None]]
PostWrapFuncT = Callable[Concatenate[typer.Context, P], None]


class WithWorld(CommonBaseModel):
    profile: str = options.profile_option
    world: "World"

    @classmethod
    def decorator(cls, *, use_beekeeper: bool = True) -> Callable[[PreWrapFuncT[P]], PostWrapFuncT[P]]:  # type: ignore[override]
        """
        Decorator to be used on commands that need a world.

        The world could be created with a beekeeper or without.
        Beekeeper is launched locally by default, but it is possible to use a remote beekeeper by specifying the
        `beekeeper_remote` argument in the decorated function.

        Args:
        ----
        use_beekeeper: Set this to False when there is no need to use a beekeeper.
        """

        def outer(func: PreWrapFuncT[P]) -> PostWrapFuncT[P]:
            common = cls.construct(world=None)  # type: ignore[arg-type]

            @merge_args(func)
            @wraps(func, assigned=["__module__", "__name__", "__doc__", "__anotations__"])
            def inner(
                ctx: typer.Context,
                profile: str = common.profile,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> None:
                from clive.__private.core.exit_call_handler import ExitCallHandler
                from clive.__private.core.world import TyperWorld

                beekeeper_remote_endpoint = cls.__get_beekeeper_remote(kwargs)

                cls._print_launching_beekeeper(beekeeper_remote_endpoint, use_beekeeper)

                async def impl() -> None:
                    async def world_close(world: TyperWorld) -> None:
                        await world.close()

                    async with ExitCallHandler(
                        TyperWorld(
                            profile_name=profile,
                            use_beekeeper=use_beekeeper,
                            beekeeper_remote_endpoint=beekeeper_remote_endpoint,
                        ),
                        finally_callback=world_close,
                    ) as world:
                        cls._assert_correct_profile_is_loaded(world.profile_data.name, profile)

                        ctx.params.update(world=world)
                        return await func(ctx, *args, **kwargs)

                asyncio_run(impl())

            return inner  # type: ignore[no-any-return]

        return outer

    @staticmethod
    def __get_beekeeper_remote(kwargs: P.kwargs) -> "Url | None":
        from clive.core.url import Url

        beekeeper_remote: str | None = kwargs.get("beekeeper_remote", None)
        return Url.parse(beekeeper_remote) if beekeeper_remote else None

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401
        from clive.core.url import Url  # noqa: F401

        WithWorld.update_forward_refs(**locals())
