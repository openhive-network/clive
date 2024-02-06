from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

MAX_BEEKEEPER_SESSION_COUNT = 64

if TYPE_CHECKING:
    from clive.__private.core.beekeeper.handle import Beekeeper
    from clive.__private.core.beekeeper.session import BeekeeperSession


async def some_login(session: BeekeeperSession) -> None:
    assert session.token, "Session should have token."
    wallet_name = session.token[:5]
    await session.api.create(wallet_name=wallet_name, password="pass")
    await session.api.open(wallet_name=wallet_name)
    wallet = (await session.api.list_wallets()).wallets
    assert wallet[0].name == wallet_name
    assert wallet[0].unlocked is False


async def test_create_session(beekeeper: Beekeeper) -> None:
    """Testing new wrapper which creates beekeeper session."""
    sessions = []
    for _ in range(MAX_BEEKEEPER_SESSION_COUNT - 1):
        sessions.append(await beekeeper.create_session())

    await asyncio.gather(*[some_login(session) for session in sessions])
