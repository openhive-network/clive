from typing import Optional

import typer

from clive import World
from clive.__private.cli import common
from clive.__private.util import ExitCallHandler

list_ = typer.Typer(help="List various things.")


@list_.command()
def keys(
    profile: Optional[str] = common.profile_option,
) -> None:
    """
    List all Public keys stored in the wallet.
    """

    with ExitCallHandler(World(profile_name=profile), finally_callback=lambda w: w.close()) as world:
        assert world.profile_data.name == profile, "Wrong profile loaded."

        public_keys = world.profile_data.working_account.keys

        typer.echo(f"{profile}, your keys are:\n{public_keys}")
