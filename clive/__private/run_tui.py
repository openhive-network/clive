from __future__ import annotations

import warnings


def _hide_never_awaited_warnings_in_non_dev_mode() -> None:
    from clive.dev import is_in_dev_mode

    if not is_in_dev_mode():
        warnings.filterwarnings("ignore", message=".* was never awaited")


def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive
    from clive.__private.ui.bindings import initialize_bindings_files

    _hide_never_awaited_warnings_in_non_dev_mode()
    prepare_before_launch()
    initialize_bindings_files()
    Clive().run()
