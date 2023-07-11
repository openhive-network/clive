from __future__ import annotations

import sys


def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    prepare_before_launch()
    sys.exit(Clive.app_instance().run())
