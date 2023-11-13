import typer

from clive.__private.cli.configure.key import key
from clive.__private.cli.configure.profile import profile
from clive.__private.cli.configure.watched_account import watched_account
from clive.__private.cli.configure.working_account import working_account

configure = typer.Typer(name="configure", help="All the commands to manage your Clive configuration.")

configure.add_typer(key)
configure.add_typer(profile)
configure.add_typer(watched_account)
configure.add_typer(working_account)
