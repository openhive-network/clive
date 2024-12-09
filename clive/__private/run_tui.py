from __future__ import annotations

import warnings


def _hide_never_awaited_warnings_in_non_dev_mode() -> None:
    from clive.dev import is_in_dev_mode

    if not is_in_dev_mode():
        warnings.filterwarnings("ignore", message=".* was never awaited")


def _check_for_beekeeper_session_token_set() -> None:
    """
    Check if CLIVE_BEEKEEPEER__SESSION_TOKEN is set when starting Clive TUI.

    We need to prevent running Clvie TUI when this env var is set, because we will not get notification from Beekeeper.
    Notification server endpoint is associated with created session, and Clive does not have access to it.

    We assume that user will not set CLIVE_BEEKEEPEER__SESSION_TOKEN by himself, but it will be set by
    using start_clive_cli.sh

    Related issue: https://gitlab.syncad.com/hive/clive/-/issues/323
    """
    from clive.__private.settings import safe_settings

    if safe_settings.beekeeper.is_session_token_set:
        from clive.__private.cli.exceptions import CLIPrettyError

        raise CLIPrettyError(
            "You cannot run Clive TUI directly from the start_clive_cli.sh script.\n"
            "Please close it, and then use start_clive.sh script instead."
        )


def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    _check_for_beekeeper_session_token_set()

    _hide_never_awaited_warnings_in_non_dev_mode()
    prepare_before_launch()
    Clive().run()
