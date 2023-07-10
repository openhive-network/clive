from typing import Any

import typer

from clive.__private.util import is_tab_completion_active


def _get_default_profile_name() -> str | None:
    if not is_tab_completion_active():
        from clive.__private.core.profile_data import ProfileData

        return ProfileData.get_lastly_used_profile_name()
    return None


def get_default_or_make_required(value: Any) -> Any:
    return ... if value is None else value


profile_option = typer.Option(
    get_default_or_make_required(_get_default_profile_name()),
    help="The profile to use. (defaults to the last used profile)",
    show_default=bool(_get_default_profile_name()),
)
beekeeper_remote_option = typer.Option(
    None, help="Beekeeper remote endpoint. (starts locally if not provided)", show_default=False
)
