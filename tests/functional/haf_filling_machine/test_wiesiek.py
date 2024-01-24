from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.beekeeper.exceptions import BeekeeperTokenNotAvailableError
from clive_local_tools import checkers, waiters
from clive_local_tools.constants import DIGEST_TO_SIGN, MAX_BEEKEEPER_SESSION_AMOUNT
from clive_local_tools.generates import generate_wallet_name, generate_wallet_password
from clive_local_tools.models import Keys, WalletInfo
import test_tools as tt


async def test_krzysiek() -> None:
    wallet = WalletInfo(name="name", password="pass", keys=Keys(count=2))
    async with await Beekeeper().launch() as bk:
        sessions = []
        notification_endpoint = bk.notification_server_http_endpoint.as_string(with_protocol=False)
        for nr in range(10):
            new_session = (
                await bk.api.create_session(notifications_endpoint=notification_endpoint, salt=f"salt-{nr}")
            ).token
            sessions.append(new_session)
        for nr, session in enumerate(sessions):
            async with bk.with_session(session):
                if nr == 0:
                    tt.logger.info(f"Creating wallet {wallet.name} in session {session}")
                    await bk.api.create(wallet_name=wallet.name, password=wallet.password)
                    for keys in wallet.keys.pairs:
                        await bk.api.import_key(wallet_name=wallet.name, wif_key=keys.private_key.value)

                tt.logger.info(f"wallet {wallet.name} opened in session {session}")
                await bk.api.open(wallet_name=wallet.name)
                await bk.api.unlock(wallet_name=wallet.name, password=wallet.password)

        for session in sessions:
            async with bk.with_session(session) as taa:
                assert 1 == len((await bk.api.list_wallets()).wallets)
                assert "name" == (await bk.api.list_wallets()).wallets[0].name
