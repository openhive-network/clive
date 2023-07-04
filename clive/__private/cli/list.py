from typing import Any, Optional

import typer

from clive import World
from clive.__private.core.profile_data import ProfileData
from clive.__private.util import ExitCallHandler

list_ = typer.Typer(help="List various things.")


def _get_default_profile_name() -> str | None:
    return ProfileData.get_lastly_used_profile_name()


def get_default_or_make_required(value: Any) -> Any:
    return ... if value is None else value


@list_.command()
def keys(
    profile: Optional[str] = typer.Option(
        get_default_or_make_required(_get_default_profile_name()),
        help="The profile to use.",
        show_default=bool(_get_default_profile_name()),
    )
) -> None:
    """
    List all Public keys stored in the wallet.
    """

    with ExitCallHandler(World(profile_name=profile), finally_callback=lambda w: w.close()) as world:
        assert world.profile_data.name == profile, "Wrong profile loaded."

        public_keys = world.profile_data.working_account.keys

        typer.echo(f"{profile}, your keys are:\n{public_keys}")
