from __future__ import annotations

import asyncio
import signal
import sys
import warnings

from clive.__private.core.clive_import import get_clive


def _hide_never_awaited_warnings_in_non_dev_mode() -> None:
    from clive.dev import is_in_dev_mode

    if not is_in_dev_mode():
        warnings.filterwarnings("ignore", message=".* was never awaited")


async def _shutdown_tui_gracefully() -> None:
    app = get_clive().app_instance()
    await app.action_quit()


def _handle_close_signals_in_tui() -> None:
    loop = asyncio.get_event_loop()
    for signal_number in [signal.SIGHUP, signal.SIGINT, signal.SIGQUIT, signal.SIGTERM]:
        loop.add_signal_handler(signal_number, lambda: asyncio.create_task(_shutdown_tui_gracefully()))


async def run_tui() -> None:
    from clive.__private.before_launch import prepare_before_launch
    from clive.__private.ui.app import Clive

    _hide_never_awaited_warnings_in_non_dev_mode()
    _handle_close_signals_in_tui()
    prepare_before_launch()
    sys.exit(await Clive.app_instance().run_async())
