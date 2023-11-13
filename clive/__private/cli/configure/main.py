import typer

from clive.__private.cli.configure.profile import profile

configure = typer.Typer(name="configure", help="All the commands to manage your Clive configuration.")

configure.add_typer(profile)
