from typing import Any

import typer

from clive.__private.core.profile_data import ProfileData


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
