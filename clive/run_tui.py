from __future__ import annotations

import sys


def run_tui() -> None:
    from clive.ui.app import clive_app
    from clive.util import prepare_before_launch

    prepare_before_launch()
    reply = clive_app.run()
    sys.exit(reply)
