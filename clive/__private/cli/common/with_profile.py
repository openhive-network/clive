from functools import wraps
from typing import TYPE_CHECKING

import typer
from merge_args import merge_args  # type: ignore[import]

from clive.__private.cli.common import options
from clive.__private.cli.common.base import CommonBaseModel, DecoratorParams, PostWrapFunc, PreWrapFunc
from clive.__private.core._async import asyncio_run

if TYPE_CHECKING:
    from clive.__private.core.profile_data import ProfileData


class WithProfile(CommonBaseModel):
    profile_name: str = options.profile_name_option
    profile_data: "ProfileData"

    @classmethod
    def decorator(cls, func: PreWrapFunc[DecoratorParams]) -> PostWrapFunc[DecoratorParams]:
        common = cls.construct(profile_data=None)  # type: ignore[arg-type]

        @merge_args(func)
        @wraps(func)
        def wrapper(
            ctx: typer.Context,
            profile_name: str = common.profile_name,
            **kwargs: DecoratorParams.kwargs,
        ) -> None:
            from clive.__private.core.profile_data import ProfileData

            profile_data_manager = ProfileData.load_with_auto_save(profile_name, auto_create=False)

            with profile_data_manager as profile_data:
                cls._assert_correct_profile_is_loaded(profile_data.name, profile_name)
                ctx.params.update(profile_data=profile_data)
                asyncio_run(func(ctx, **kwargs))

        return wrapper  # type: ignore[no-any-return]

    @staticmethod
    def update_forwards() -> None:
        from clive.__private.core.profile_data import ProfileData  # noqa: F401

        WithProfile.update_forward_refs(**locals())
