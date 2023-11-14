from functools import wraps
from typing import TYPE_CHECKING, Any, Optional

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.core.world import World


class OperationCommon(CommonBaseModel):
    """
    Common options for some commands.

    Inspired by https://github.com/tiangolo/typer/issues/296#issuecomment-1381269597.
    """

    profile_name: str = options.profile_name_option
    password: Optional[str] = options.password_optional_option
    sign: Optional[str] = typer.Option(None, help="Key alias to sign the transaction with.", show_default=False)
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option
    broadcast: bool = typer.Option(True, help="Whether broadcast the transaction. (i.e. dry-run)")
    save_file: Optional[str] = typer.Option(
        None,
        help="The file to save the transaction to (format is determined by file extension - .bin or .json).",
        show_default=False,
    )
    world: "World" = None  # type: ignore[assignment]

    @classmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        common = cls.construct()

        @merge_args(func)
        @wraps(func)
        def wrapper(
            ctx: typer.Context,
            profile_name: str = common.profile_name,
            password: Optional[str] = common.password,
            sign: Optional[str] = common.sign,  # noqa: ARG001
            beekeeper_remote: Optional[str] = common.beekeeper_remote,
            broadcast: bool = common.broadcast,
            save_file: Optional[str] = common.save_file,  # noqa: ARG001
            **kwargs: Any,
        ) -> None:
            from clive.__private.core.world import TyperWorld
            from clive.core.url import Url

            cls.validate_options(ctx.params)

            if not broadcast:
                typer.echo("[Performing dry run, because --no-broadcast was specified.]\n")

            beekeeper_remote_endpoint = Url.parse(beekeeper_remote) if beekeeper_remote else None

            cls._print_launching_beekeeper(beekeeper_remote_endpoint)

            async def impl() -> None:
                async with TyperWorld(
                    profile_name=profile_name,
                    beekeeper_remote_endpoint=beekeeper_remote_endpoint,
                ) as world:
                    cls._assert_correct_profile_is_loaded(world.profile_data.name, profile_name)
                    ctx.params.update(world=world)

                    if password is not None:
                        await world.commands.activate(password=password)

                    await func(ctx, **kwargs)

            asyncio_run(impl())

        return wrapper  # type: ignore[no-any-return]

    def _validate_options(self) -> None:
        if self.broadcast and self.sign is None:
            raise CLIPrettyError(
                "You must provide a key alias to sign the transaction with if you want to broadcast them."
            )

        if self.sign is not None and self.password is None:
            raise CLIPrettyError("You must provide a password so wallet can be unlocked while signing a transaction.")

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.world import World  # noqa: F401

        OperationCommon.update_forward_refs(**locals())
