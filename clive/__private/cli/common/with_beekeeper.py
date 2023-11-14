from functools import wraps
from typing import TYPE_CHECKING, Any, Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


class WithBeekeeper(CommonBaseModel):
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option
    beekeeper: "Beekeeper"

    @classmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        common = cls.construct(beekeeper=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func)
        def wrapper(
            ctx: typer.Context,
            beekeeper_remote: Optional[str] = common.beekeeper_remote,
            **kwargs: Any,
        ) -> None:
            from clive.__private.core.beekeeper import Beekeeper
            from clive.core.url import Url

            beekeeper_remote_endpoint = Url.parse(beekeeper_remote) if beekeeper_remote else None

            cls._print_launching_beekeeper(beekeeper_remote_endpoint)

            async def impl() -> None:
                async with Beekeeper(remote_endpoint=beekeeper_remote_endpoint) as beekeeper:
                    ctx.params.update(beekeeper=beekeeper)
                    await func(ctx, **kwargs)

            asyncio_run(impl())

        return wrapper  # type: ignore[no-any-return]

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.beekeeper import Beekeeper  # noqa: F401

        WithBeekeeper.update_forward_refs(**locals())
