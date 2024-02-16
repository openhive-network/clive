from __future__ import annotations

import asyncio
import os
import signal
from pathlib import Path

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools import checkers


async def test_notification_webserver_listening(beekeeper: Beekeeper) -> None:
    """Test test_notification_webserver_listening will check webserver listening notifications."""
    # ARRANGE
    webserver_listening_msg = (
        f"Got notification: {{'value': {{'address': '0.0.0.0', 'port': {beekeeper.http_endpoint.port}, 'type':"
        " 'HTTP'}, 'time': '.*?', 'name': 'webserver listening'}"
    )

    # ACT
    webserver_listening_notification_found = checkers.check_for_pattern_in_file(
        Path(Beekeeper().get_wallet_dir()).parent / "logs" / "debug" / "latest.log", webserver_listening_msg
    )

    # ASSERT
    assert webserver_listening_notification_found, "There should be `webserver listening` notification."


@pytest.mark.parametrize("current_status", ["beekeeper is ready", "interrupted", "beekeeper is starting"])
async def test_notification_hived_status(current_status: str) -> None:
    """Test test_notification_hived_status will check all hived_status statutes."""

    # ARRANGE
    async def wait_for_beekeeper_to_close(beekeeper: Beekeeper) -> None:
        async def __wait_for_beekeeper_to_close() -> None:
            while beekeeper.is_already_running_locally():
                await asyncio.sleep(0.1)

        try:
            await asyncio.wait_for(__wait_for_beekeeper_to_close(), timeout=1)
        except asyncio.TimeoutError:
            pytest.fail("Beekeeper was not closed in the expected time.")

    notification_msg = (
        f"Got notification: {{'value': {{'current_status': '{current_status}'}}, 'time': '.*?', 'name':"
        " 'hived_status'}"
    )

    # ACT
    beekeeper = await Beekeeper().launch()
    if current_status == "interrupted":
        os.kill(beekeeper.get_pid_from_file(), signal.SIGINT)
        await wait_for_beekeeper_to_close(beekeeper=beekeeper)
    else:
        await beekeeper.close()

    notification_msg_found = checkers.check_for_pattern_in_file(
        Path(Beekeeper().get_wallet_dir()).parent / "logs" / "debug" / "latest.log", notification_msg
    )

    # ASSERT
    assert notification_msg_found, f"There should be `{current_status}` notification."


async def test_notification_opening_beekeeper_failed() -> None:
    """Test test_notification_opening_beekeeper_failed will check opening_beekeeper_failed notification."""
    # ARRANGE
    notification_msg = (
        "Got notification: {'value': {'current_status': 'interrupted'}, 'time': '.*?', 'name': 'hived_status'}"
    )

    # ACT
    async with await Beekeeper().launch(), await Beekeeper().launch():
        await asyncio.sleep(1)

    # ASSERT
    notification_msg_found = checkers.check_for_pattern_in_file(
        Path(Beekeeper().get_wallet_dir()).parent / "logs" / "debug" / "latest.log", notification_msg
    )
    assert notification_msg_found, "There should be `interrupted` notification."


async def test_notification_attempt_of_closing_all_wallets() -> None:
    """Test test_notification_attempt_of_closing_all_wallets will check if there is notification about closing wallets."""
    # ARRANGE
    notification_msg = "Got notification about closing all wallets"

    # ACT
    async with await Beekeeper().launch(unlock_timeout=1):
        await asyncio.sleep(2)

    # ASSERT
    notification_msg_found = checkers.check_for_pattern_in_file(
        Path(Beekeeper().get_wallet_dir()).parent / "logs" / "debug" / "latest.log", notification_msg
    )
    assert notification_msg_found, "There should be `closing all wallets` notification."
