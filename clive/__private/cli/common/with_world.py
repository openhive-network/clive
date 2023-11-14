from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.cli.common.options import modified_option
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.core.world import World
    from clive.core.url import Url


class WithWorld(CommonBaseModel):
    profile_name: str = options.profile_name_option
    world: "World"

    @classmethod
    def decorator(cls, *, use_beekeeper: bool = True) -> Callable[[PreWrapFunc[DecoratorParams]], PostWrapFunc[DecoratorParams]]:  # type: ignore[override]
        """
        Decorator to be used on commands that need a world.

        The world could be created with a beekeeper or without.
        Beekeeper is launched locally by default, but it is possible to use a remote beekeeper by specifying the
        `beekeeper_remote` argument in the decorated function.

        Args:
        ----
        use_beekeeper: Set this to False when there is no need to use a beekeeper.
        """

        def outer(func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
            common = cls.construct(world=None)  # type: ignore[arg-type]

            @merge_args(func)
            @wraps(func)
            def inner(
                ctx: typer.Context,
                profile: str = common.profile_name,
                beekeeper_remote: Optional[str] = modified_option(
                    options.beekeeper_remote_option, hidden=not use_beekeeper
                ),
                **kwargs: DecoratorParams.kwargs,
            ) -> None:
                from clive.__private.core.world import TyperWorld

                beekeeper_remote_endpoint = cls.__get_beekeeper_remote(beekeeper_remote)

                cls._print_launching_beekeeper(beekeeper_remote_endpoint, use_beekeeper)

                async def impl() -> None:
                    async with TyperWorld(
                        profile_name=profile,
                        use_beekeeper=use_beekeeper,
                        beekeeper_remote_endpoint=beekeeper_remote_endpoint,
                    ) as world:
                        cls._assert_correct_profile_is_loaded(world.profile_data.name, profile)

                        ctx.params.update(world=world)
                        return await func(ctx, **kwargs)

                asyncio_run(impl())

            return inner  # type: ignore[no-any-return]

        return outer

    @staticmethod
    def __get_beekeeper_remote(beekeeper_remote: str | None) -> "Url | None":
        from clive.core.url import Url

        return Url.parse(beekeeper_remote) if beekeeper_remote else None

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401
        from clive.core.url import Url  # noqa: F401

        WithWorld.update_forward_refs(**locals())
