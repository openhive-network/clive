from __future__ import annotations

import asyncio
from typing import Final

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive.exceptions import CommunicationError
from clive_local_tools import checkers

WRONG_TOKEN: Final[str] = "104fc637d5c32c271bdfdc366af5bfc8f977e2462b01877454cfd1643196bcf1"


async def test_api_close_session() -> None:
    """Test test_api_close_session will test beekeeper_api.close_session api call."""
    # ARRANGE
    beekeeper = Beekeeper()
    await beekeeper.launch()
    first_token = beekeeper.token
    notification_endpoint = beekeeper.notification_server_http_endpoint.as_string(with_protocol=False)
    await beekeeper.api.create_session(notifications_endpoint=notification_endpoint, salt="test_api_close_session")

    # ACT
    await beekeeper.api.close_session(token=first_token)

    # ASSERT
    close_log_entry = (
        f'"id":0,"jsonrpc":"2.0","method":"beekeeper_api.close_session","params":{{"token":"{first_token}"}}'
    )

    with pytest.raises(CommunicationError, match=f"A session attached to {first_token} doesn't exist"):
        await beekeeper.api.list_wallets()
    assert checkers.check_for_pattern_in_file(
        Beekeeper().get_wallet_dir() / "stderr.log", close_log_entry
    ), "Log should have information about closing session with specific token created during create_session call."


async def test_if_beekeeper_closes_after_last_session_termination() -> None:
    """Test test_api_close_session will test if beekeeper closes after closing last session."""

    # ARRANGE
    async def wait_for_beekeeper_to_close() -> None:
        while beekeeper.is_already_running_locally():
            await asyncio.sleep(0.1)

    beekeeper = Beekeeper()
    await beekeeper.launch()

    # ACT
    await beekeeper.api.close_session()

    try:
        await asyncio.wait_for(wait_for_beekeeper_to_close(), timeout=1)
    except asyncio.TimeoutError:
        pytest.fail("Beekeeper was not closed after last session termination in the expected time.")

    # ASSERT
    with pytest.raises(CommunicationError, match="no response available"):
        await beekeeper.api.list_wallets()

    assert checkers.check_for_pattern_in_file(
        Beekeeper().get_wallet_dir() / "stderr.log", "exited cleanly"
    ), "Beekeeper should be closed after last session termination."


async def test_api_close_session_double(beekeeper: Beekeeper) -> None:
    """Test test_api_close_session will test possibility of double closing session."""
    # ARRANGE
    token = (
        await beekeeper.api.create_session(
            notifications_endpoint=beekeeper.notification_server_http_endpoint.as_string(with_protocol=False),
            salt="salt",
        )
    ).token

    # ACT
    await beekeeper.api.close_session(token=token)

    # ASSERT
    with pytest.raises(CommunicationError, match=f"A session attached to {token} doesn't exist"):
        await beekeeper.api.close_session(token=token)


@pytest.mark.parametrize("create_session", [False, True], ids=["no_session_before", "in_other_session"])
async def test_api_close_session_not_existing(create_session: bool, beekeeper: Beekeeper) -> None:
    """Test test_api_close_session_not_existing will test possibility of closing not existing session."""
    # ARRANGE
    if create_session:
        await beekeeper.api.create_session(
            notifications_endpoint=beekeeper.notification_server_http_endpoint.as_string(with_protocol=False),
            salt="salt",
        )

    # ACT & ASSERT
    with pytest.raises(CommunicationError, match=f"A session attached to {WRONG_TOKEN} doesn't exist"):
        await beekeeper.api.close_session(token=WRONG_TOKEN)
