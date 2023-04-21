from __future__ import annotations

import sys


def run_tui() -> None:
    from clive.__private.ui.app import Clive
    from clive.__private.util import prepare_before_launch

    prepare_before_launch()
    try:
        sys.exit(Clive.app_instance().run())
    finally:
        Clive.app_instance().world.close()
