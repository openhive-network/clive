from __future__ import annotations

import sys
import warnings


def _hide_never_awaited_warnings_in_non_dev_mode() -> None:
    from clive.__private.config import settings

    if not settings.get("dev", False):
        warnings.filterwarnings("ignore", message=".* was never awaited")


async def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    _hide_never_awaited_warnings_in_non_dev_mode()
    prepare_before_launch()
    sys.exit(await Clive.app_instance().run_async())
