from __future__ import annotations

import sys


def run_tui() -> None:
    from clive.__private.ui.app import Clive
    from clive.__private.util import prepare_before_launch

    prepare_before_launch()
    reply = Clive.app_instance().run()
    sys.exit(reply)
