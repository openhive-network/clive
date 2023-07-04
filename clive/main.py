from __future__ import annotations

import sys
from os import environ

from clive.__private.cli import cli
from clive.__private.run_cli import run_cli
from clive.__private.run_tui import run_tui
from clive.__private.util import thread_pool


def __is_tab_completion_active() -> bool:
    return "_CLIVE_COMPLETE" in environ


def __any_arguments_given() -> bool:
    return len(sys.argv) > 1


def main() -> None:
    if __is_tab_completion_active():
        cli()
        return

    if not __any_arguments_given():
        run_tui()
        return

    run_cli()


if __name__ == "__main__":
    with thread_pool:
        main()
