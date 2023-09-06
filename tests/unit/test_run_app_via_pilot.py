from __future__ import annotations

from clive.__private.ui.app import Clive


async def test_run_app_via_pilot() -> None:
    async with Clive().run_test():
        pass
