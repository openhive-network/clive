from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.configure.key import key
from clive.__private.cli.configure.node import node
from clive.__private.cli.configure.profile import profile
from clive.__private.cli.configure.watched_account import watched_account
from clive.__private.cli.configure.working_account import working_account

configure = CliveTyper(name="configure", help="All the commands to manage your Clive configuration.")

configure.add_typer(key)
configure.add_typer(node)
configure.add_typer(profile)
configure.add_typer(watched_account)
configure.add_typer(working_account)
