from __future__ import annotations

import warnings

import typer


def _hide_never_awaited_warnings_in_non_dev_mode() -> None:
    from clive.dev import is_in_dev_mode

    if not is_in_dev_mode():
        warnings.filterwarnings("ignore", message=".* was never awaited")


def _check_for_beekeeper_session_token_set() -> bool:
    from clive.__private.core.constants.setting_identifiers import BEEKEEPER_SESSION_TOKEN
    from clive.__private.settings import clive_prefixed_envvar, safe_settings

    if safe_settings.beekeeper.is_session_token_set:
        env_var = clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)
        message = f"You cannot run Clive TUI with {env_var} set.\n" "Please unset it first."
        typer.echo(message)
        return True
    return False


def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    if _check_for_beekeeper_session_token_set():
        return

    _hide_never_awaited_warnings_in_non_dev_mode()
    prepare_before_launch()
    Clive().run()
