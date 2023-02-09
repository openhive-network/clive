from __future__ import annotations

import sys
from os import environ

from clive.cli import cli
from clive.run_cli import run_cli
from clive.run_tui import run_tui


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
    main()
