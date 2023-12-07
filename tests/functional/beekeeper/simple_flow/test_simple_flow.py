from __future__ import annotations

import asyncio
from typing import Final

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools import checkers, waiters
from clive_local_tools.models import Keys, WalletInfo

DIGEST_TO_SIGN: Final[str] = "9B29BA0710AF3918E81D7B935556D7AB205D8A8F5CA2E2427535980C2E8BDAFF"
MAX_SESSION_NUMBER: Final[int] = 64


async def test_simple_flow() -> None:
    """
    Test simple flow of beekeeper in each available session.

    * Creating/deleting session(s),
    * Creating/deleting wallet(s),
    * Locking/unlockinq wallet(s),
    * Check timeout,
    * Creating/removing/listing keys,
    * List wallet(s),
    * Signing.
    """
    # ARRANGE
    sessions = []
    # Create wallets == MAX_SESSION_NUMBER so that we can create wallet per session
    wallets = [WalletInfo(name=str(i), password=str(i), keys=Keys(count=1)) for i in range(MAX_SESSION_NUMBER)]
    bk = await Beekeeper().launch()
    notification_endpoint = bk.notification_server_http_endpoint.as_string(with_protocol=False)

    # ACT & ASSERT 1
    # In this block we will create new session, and wallet import key to is and sign a digest
    for nr in range(MAX_SESSION_NUMBER):
        wallet = wallets[nr]
        # Create new session
        new_session = (
            bk.token
            if nr == 0
            else (await bk.api.create_session(notifications_endpoint=notification_endpoint, salt=f"salt-{nr}")).token
        )
        # Remember session token so that we can use it later
        sessions.append(new_session)
        # Use specific session
        async with bk.with_session(token=new_session):
            # Check is valid token will be used
            assert bk.token == new_session, "All api calls should be made with provided token."
            # Create wallet
            await bk.api.create(wallet_name=wallet.name, password=wallet.password)
            # Import key to wallet
            await bk.api.import_key(wallet_name=wallet.name, wif_key=wallet.keys.pairs[0].private_key.value)
            # Sign digest with imported token
            await bk.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=wallet.keys.pairs[0].public_key.value)
            # Lock wallet in this session
            await bk.api.lock(wallet_name=wallet.name)
    # ACT & ASSERT 2
    # In this vlock we will unlock previous locked wallet, get public keys, list walleta, remove key from unlocked wallet and set timeout on it
    for nr, session in enumerate(sessions):
        wallet = wallets[nr]
        async with bk.with_session(token=session):
            # Check is valid token will be used
            assert bk.token == session
            # Unlock wallet locked in previous block
            await bk.api.unlock(wallet_name=wallet.name, password=wallet.password)
            # Get keys from unlocked wallet
            bk_keys = (await bk.api.get_public_keys()).keys
            # Get unlocked wallet
            bk_wallets = (await bk.api.list_wallets()).wallets
            # Check if only one wallet has been unlocked
            assert len(bk_wallets) == 1, "There should be only one wallet per session."
            assert wallet.name == bk_wallets[0].name, "Name of wallet should be the same as unlocked one."
            # Check if valid keys had been listed
            assert len(bk_keys) == 1, " There should be only one key inside wallet."
            assert (
                wallet.keys.pairs[0].public_key.value == bk_keys[0].public_key
            ), "Listed key should be the same as imported one"
            # Remove wallet from unlocked wallet
            await bk.api.remove_key(
                wallet_name=wallet.name, password=wallet.password, public_key=wallet.keys.pairs[0].public_key.value
            )
            # Set timeout for this session
            await bk.api.set_timeout(seconds=1)

    # ACT & ASSERT 3
    # In this block we will unlock wallet which should be locked by timeout, close it, and lastly close all sessions
    await asyncio.sleep(1)
    for nr, session in enumerate(sessions):
        wallet = wallets[nr]
        async with bk.with_session(token=session):
            await bk.api.unlock(wallet_name=wallet.name, password=wallet.password)
            await bk.api.close(wallet_name=wallet.name)
        await bk.api.close_session(token=session)

    await waiters.wait_for_beekeeper_to_close_after_last_session_termination(beekeeper=bk)

    assert checkers.check_for_pattern_in_file(
        Beekeeper().get_wallet_dir() / "stderr.log", "exited cleanly"
    ), "Beekeeper should be closed after last session termination."
