import sys
from os import environ

from clive.cli import cli
from clive.run_cli import run_cli
from clive.run_tui import run_tui


def is_tab_completion_active() -> bool:
    return "_CLIVE_COMPLETE" in environ


def main() -> None:
    if is_tab_completion_active():
        cli()
        return

    if not sys.argv[1:]:
        run_tui()
        return
    run_cli()


if __name__ == "__main__":
    main()
