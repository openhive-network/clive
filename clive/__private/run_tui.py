from __future__ import annotations

import sys


def run_tui() -> None:
    from clive.__private.ui.app import Clive
    from clive.__private.util import prepare_before_launch, spawn_thread_pool

    with spawn_thread_pool() as executor:
        prepare_before_launch(executor=executor)
        sys.exit(Clive.app_instance().run())
