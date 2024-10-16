from __future__ import annotations

import sys

from clive.__private.cli.completion import is_tab_completion_active
from clive.__private.cli.main import cli
from clive.__private.core._thread import thread_pool
from clive.__private.run_cli import run_cli
from clive.__private.run_tui import run_tui


def _is_cli_requested() -> bool:
    return len(sys.argv) > 1


def main() -> None:
    with thread_pool:
        if is_tab_completion_active():
            cli()
            return

        if not _is_cli_requested():
            run_tui()
            return

        run_cli()


if __name__ == "__main__":
    main()
