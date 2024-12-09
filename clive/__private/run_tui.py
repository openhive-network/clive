from __future__ import annotations

import warnings

import typer


def _hide_never_awaited_warnings_in_non_dev_mode() -> None:
    from clive.dev import is_in_dev_mode

    if not is_in_dev_mode():
        warnings.filterwarnings("ignore", message=".* was never awaited")


def _check_for_beekeeper_session_token_set() -> None:
    import sys

    from clive.__private.settings import safe_settings

    if safe_settings.beekeeper.is_session_token_set:
        # We assume that user will not set CLIVE_BEEKEEPEER__SESSION_TOKEN by himself.
        # But it will be set by using start_clive_cli.sh
        #
        message = (
            "You cannot run Clive TUI directly from the start_clive_cli.sh script.\n"
            "Please close it, and then use start_clive.sh script instead."
        )
        typer.echo(message)
        sys.exit(1)


def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    _check_for_beekeeper_session_token_set()

    _hide_never_awaited_warnings_in_non_dev_mode()
    prepare_before_launch()
    Clive().run()
