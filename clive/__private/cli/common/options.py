from typing import Any

import typer


def _get_default_profile_name() -> str | None:
    raise NotImplementedError


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
