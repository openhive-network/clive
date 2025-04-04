from __future__ import annotations

from clive.__private.cli.clive_typer import CliveTyper
from clive.__private.cli.configure.chain_id import chain_id
from clive.__private.cli.configure.key import key
from clive.__private.cli.configure.known_account import known_account
from clive.__private.cli.configure.node import node
from clive.__private.cli.configure.profile import profile
from clive.__private.cli.configure.tracked_account import tracked_account
from clive.__private.cli.configure.working_account import working_account

configure = CliveTyper(name="configure", help="All the commands to manage your Clive configuration.")

configure.add_typer(chain_id)
configure.add_typer(key)
configure.add_typer(node)
configure.add_typer(profile)
configure.add_typer(tracked_account)
configure.add_typer(working_account)
configure.add_typer(known_account)
