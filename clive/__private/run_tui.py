from __future__ import annotations

import asyncio
import sys


def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    prepare_before_launch()
    sys.exit(asyncio.run(Clive.app_instance().run_async()))
