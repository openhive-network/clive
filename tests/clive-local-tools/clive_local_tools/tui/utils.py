from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt
from textual.css.query import NoMatches

from clive.__private.ui.widgets.titled_label import TitledLabel

if TYPE_CHECKING:
    from beekeepy import AsyncBeekeeper, AsyncUnlockedWallet

    from clive_local_tools.tui.types import CliveApp


async def unlock_wallet(beekeeper: AsyncBeekeeper, wallet_name: str, wallet_password: str) -> AsyncUnlockedWallet:
    session = await beekeeper.session
    for wallet in await session.wallets:
        if wallet.name == wallet_name:
            if (unlocked_wallet := await wallet.unlocked) is not None:
                return unlocked_wallet
            return await wallet.unlock(password=wallet_password)
    locked_wallet = await session.open_wallet(name=wallet_name)
    return await locked_wallet.unlock(password=wallet_password)


def log_current_view(app: CliveApp, *, nodes: bool = False, source: str | None = None) -> None:
    """For debug purposes."""
    source = f"{source}: " if source is not None else ""
    tt.logger.debug(f"{source}screen: {app.screen}, focused: {app.focused}")
    if nodes:
        tt.logger.debug(f'nodes: {app.screen.query("*").nodes}')


def get_profile_name(app: CliveApp) -> str:
    try:
        widget = app.screen.query_exactly_one("#profile-label", TitledLabel)
    except NoMatches as error:
        raise AssertionError("Profile couldn't be found. It is not available in the create_profile process.") from error
    return str(widget.value).strip()
