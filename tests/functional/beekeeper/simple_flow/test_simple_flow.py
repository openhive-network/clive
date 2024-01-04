from __future__ import annotations

import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Final

import pytest

from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.keys import PrivateKeyAliased, PublicKeyAliased
from clive_local_tools import checkers, waiters
from clive_local_tools.models import Keys, WalletInfo

DIGEST_TO_SIGN: Final[str] = "9B29BA0710AF3918E81D7B935556D7AB205D8A8F5CA2E2427535980C2E8BDAFF"
MAX_SESSION_NUMBER: Final[int] = 64


async def prepare_wallet_dirs(
    tmp_path: Path,
    number_of_dirs: int,
    source_directory: Path | None = None,
) -> tuple[list[WalletInfo], list[Path]]:
    """Copy wallets (.wallet) files from source_directory into number_of_dirs temp dirs."""

    async def _export_wallet_to_wallet_info(wallets: list[WalletInfo], source_directory_keys: Path) -> None:
        """Load keys from exported walled and save them into WalletInfo."""
        for wallet in wallets:
            with Path.open(source_directory_keys / f"{wallet.name}.keys") as key_file:
                keys = json.load(key_file)
                wallet.keys.pairs.clear()
                for key in keys:
                    wallet.keys.pairs.append(
                        Keys.KeysPair(
                            PublicKeyAliased(value=key["public_key"], alias=""),
                            PrivateKeyAliased(value=key["private_key"], alias=""),
                        )
                    )

    temp_directories = [tmp_path / f"wallets-{n}" for n in range(number_of_dirs)]

    for tmp_dir in temp_directories:
        tmp_dir.mkdir()

    wallets = [WalletInfo(name=str(i), password=str(i), keys=Keys(count=i % 5)) for i in range(MAX_SESSION_NUMBER)]

    if source_directory:
        source_directory_wallets = source_directory / "wallets"
        source_directory_keys = source_directory / "keys"
        wallet_files = [f for f in os.listdir(source_directory_wallets) if f.endswith(".wallet")]
        for wallet_file in wallet_files:
            for temp_dir in temp_directories:
                source_path = source_directory_wallets / wallet_file
                destination_path = temp_dir / wallet_file
                shutil.copy2(source_path, destination_path)
        await _export_wallet_to_wallet_info(wallets=wallets, source_directory_keys=source_directory_keys)
    return wallets, temp_directories


async def simple_flow(*, bk: Beekeeper, wallets: list[WalletInfo], use_existing_wallets: bool) -> None:
    sessions = []
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
            if use_existing_wallets:
                await bk.api.open(wallet_name=wallet.name)
                await bk.api.unlock(wallet_name=wallet.name, password=wallet.password)

                bk_keys = [keys.public_key for keys in (await bk.api.get_public_keys()).keys]
                bk_keys.sort()

                wallet_keys = wallet.keys.get_public_keys()
                assert len(bk_keys) == len(
                    wallet_keys
                ), "Number of public keys from wallet should be the same as in bk."
                assert bk_keys == wallet_keys, "There should be same number of keys."
                for keys in wallet.keys.pairs:
                    # Sign digest with imported token
                    await bk.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=keys.public_key.value)
            else:
                # Create wallet
                await bk.api.create(wallet_name=wallet.name, password=wallet.password)
                for keys in wallet.keys.pairs:
                    # Import keys to wallet
                    await bk.api.import_key(wallet_name=wallet.name, wif_key=keys.private_key.value)
                    # Sign digest with imported token
                    await bk.api.sign_digest(sig_digest=DIGEST_TO_SIGN, public_key=keys.public_key.value)
            # Lock wallet in this session
            await bk.api.lock(wallet_name=wallet.name)

    # ACT & ASSERT 2
    # In this block we will unlock previous locked wallet, get public keys, list walleta, remove key from unlocked wallet and set timeout on it.
    for nr, session in enumerate(sessions):
        wallet = wallets[nr]
        async with bk.with_session(token=session):
            # Check is valid token will be used
            assert bk.token == session
            # Unlock wallet locked in previous block
            await bk.api.unlock(wallet_name=wallet.name, password=wallet.password)
            # Get keys from unlocked wallet
            bk_keys = [keys.public_key for keys in (await bk.api.get_public_keys()).keys]
            # Get unlocked wallet
            bk_wallets = (await bk.api.list_wallets()).wallets
            # Check if only one wallet has been unlocked
            assert len(bk_wallets) == 1, "There should be only one wallet per session."
            assert wallet.name == bk_wallets[0].name, "Name of wallet should be the same as unlocked one."
            # Check if valid keys had been listed
            assert len(bk_keys) == len(wallet.keys.pairs), " There should be only one key inside wallet."
            for pub_key in wallet.keys.get_public_keys():
                assert pub_key in bk_keys, "Imported public keys should be the same as the one returned by beekeeper."
            # Remove wallet from unlocked wallet
            for keys in wallet.keys.pairs:
                await bk.api.remove_key(
                    wallet_name=wallet.name, password=wallet.password, public_key=keys.public_key.value
                )
            bk_keys_empty = (await bk.api.get_public_keys()).keys
            assert len(bk_keys_empty) == 0, "There should be no keys after removement."
            # Set timeout for this session
            await bk.api.set_timeout(seconds=1)

    # ACT & ASSERT 3
    # In this block we will unlock wallet which should be locked by timeout, close it, and lastly close all sessions.
    await asyncio.sleep(1)
    for nr, session in enumerate(sessions):
        wallet = wallets[nr]
        async with bk.with_session(token=session):
            await bk.api.unlock(wallet_name=wallet.name, password=wallet.password)
            await bk.api.close(wallet_name=wallet.name)
        await bk.api.close_session(token=session)

    await waiters.wait_for_beekeeper_to_close(beekeeper=bk)

    assert checkers.check_for_pattern_in_file(
        bk.get_wallet_dir() / "stderr.log", "exited cleanly"
    ), "Beekeeper should be closed after last session termination."


@pytest.mark.parametrize(
    ("use_existing_wallets", "number_of_beekeeper_instances"), [(True, 1), (True, 2), (False, 1), (False, 2)]
)
async def test_simple_flow(tmp_path: Path, use_existing_wallets: bool, number_of_beekeeper_instances: int) -> None:
    """
    Test simple flow of multiply instance of beekeepers launched parallel with each available session by newly created or imported wallets.

    * Creating/deleting session(s),
    * Creating/deleting wallet(s),
    * Locking/unlockinq wallet(s),
    * Check timeout,
    * Creating/removing/listing keys,
    * List wallet(s),
    * Signing.
    """
    # ARRANGE
    source_directories = Path(__file__).parent / "prepared_wallets" if use_existing_wallets else None
    wallets, wallets_dirs = await prepare_wallet_dirs(
        tmp_path=tmp_path, number_of_dirs=number_of_beekeeper_instances, source_directory=source_directories
    )

    await asyncio.gather(
        *[
            simple_flow(
                bk=await Beekeeper().launch(wallet_dir=wallet_dir),
                wallets=wallets,
                use_existing_wallets=use_existing_wallets,
            )
            for wallet_dir in wallets_dirs
        ]
    )
