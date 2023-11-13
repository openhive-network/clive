import typer

from clive.__private.cli.configure.profile import profile
from clive.__private.cli.configure.watched_account import watched_account

configure = typer.Typer(name="configure", help="All the commands to manage your Clive configuration.")

configure.add_typer(profile)
configure.add_typer(watched_account)
