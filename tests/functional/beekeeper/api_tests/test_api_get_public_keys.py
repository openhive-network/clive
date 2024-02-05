from __future__ import annotations

import functools
import json
import time

import requests
import copy
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

import pytest

import test_tools as tt

from clive.exceptions import CommunicationError
from clive_local_tools.models import WalletInfo

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper
    from clive_local_tools.models import WalletInfo
    from clive_local_tools.types import WalletsGeneratorT


async def open_and_unlock_wallet(beekeeper: Beekeeper, wallet: WalletInfo) -> None:
    await beekeeper.api.open(wallet_name=wallet.name)
    await beekeeper.api.unlock(wallet_name=wallet.name, password=wallet.password)


async def test_api_get_public_keys(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT) -> None:
    """Test test_api_get_public_keys will test beekeeper_api.get_public_keys api call."""
    # ARRANGE
    wallets = await setup_wallets(1, import_keys=False, keys_per_wallet=5)
    wallet = wallets[0]
    for pair in wallet.keys.pairs:
        await beekeeper.api.import_key(wallet_name=wallet.name, wif_key=pair.private_key.value)

    # ACT
    response = (await beekeeper.api.get_public_keys()).keys
    bk_public_keys = [pub.public_key for pub in response]

    # ASSERT
    assert bk_public_keys == wallet.keys.get_public_keys(), "All keys should be available."


async def test_api_get_public_keys_with_many_wallets(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT) -> None:
    """Test test_api_get_public_keys_with_many_wallets will test beekeeper_api.get_public_keys when wallets are being locked."""
    # ARRANGE
    # Prepare wallets
    wallets = await setup_wallets(2, import_keys=True, keys_per_wallet=5)
    wallet_1 = wallets[0]
    wallet_2 = wallets[1]
    all_keys = wallet_1.keys.get_public_keys() + wallet_2.keys.get_public_keys()
    all_keys.sort()
    # open and and unlock wallets
    await open_and_unlock_wallet(wallet=wallet_1, beekeeper=beekeeper)
    await open_and_unlock_wallet(wallet=wallet_2, beekeeper=beekeeper)

    # Get ALL public key from bk it should contain both, wallet_1_keys and  wallet_2_keys
    bk_pub_keys_all = [pub.public_key for pub in (await beekeeper.api.get_public_keys()).keys]
    bk_pub_keys_all.sort()
    assert bk_pub_keys_all == all_keys, "All keys should be available."

    # ACT & ASSERT 1
    # Lock wallet 2
    await beekeeper.api.lock(wallet_name=wallet_2.name)
    # Now only keys from wallet 1 should be available
    bk_pub_keys_1 = [pub.public_key for pub in (await beekeeper.api.get_public_keys()).keys]
    assert bk_pub_keys_1 == wallet_1.keys.get_public_keys(), "Only keys from wallet 1 should be available."

    # ACT & ASSERT 2
    # Lock wallet 1
    await beekeeper.api.lock(wallet_name=wallet_1.name)
    # Now all wallet are closed, so that no key should be available
    with pytest.raises(CommunicationError, match="You don't have any unlocked wallet"):
        await beekeeper.api.get_public_keys()


async def test_api_get_public_keys_with_many_wallets_closed(
        beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT
) -> None:
    """Test test_api_get_public_keys_with_many_wallets_closed will test beekeeper_api.get_public_keys when wallets are being closed."""
    # ARRANGE
    # Prepare wallets
    wallets = await setup_wallets(2, import_keys=True, keys_per_wallet=5)
    wallet_1 = wallets[0]
    wallet_2 = wallets[1]
    all_keys = wallet_1.keys.get_public_keys() + wallet_2.keys.get_public_keys()
    all_keys.sort()

    # Open and unlock wallets
    await open_and_unlock_wallet(wallet=wallet_1, beekeeper=beekeeper)
    await open_and_unlock_wallet(wallet=wallet_2, beekeeper=beekeeper)

    # Get all available public keys ()
    bk_pub_keys_all = [pub.public_key for pub in (await beekeeper.api.get_public_keys()).keys]
    bk_pub_keys_all.sort()
    assert bk_pub_keys_all == all_keys, "Keys from wallet 1 and wallet 2 should be available."

    # ACT & ASSERT 1
    # Close wallet 2
    await beekeeper.api.close(wallet_name=wallet_2.name)
    bk_pub_keys_1 = [pub.public_key for pub in (await beekeeper.api.get_public_keys()).keys]
    assert bk_pub_keys_1 == wallet_1.keys.get_public_keys(), "Only keys from wallet 1 should be available."

    # ACT & ASSERT 2
    # Close wallet 1,
    await beekeeper.api.close(wallet_name=wallet_1.name)
    # There is no wallet
    with pytest.raises(CommunicationError, match="You don't have any wallet"):
        await beekeeper.api.get_public_keys()


@pytest.mark.parametrize("additional_sessions, request_count", [(2, 1000), (3, 2000), (4, 3000)])
async def test_many_session(beekeeper: Beekeeper, setup_wallets: WalletsGeneratorT, additional_sessions: int,
                            request_count: int) -> None:
    wallet = WalletInfo(name="my_wallet", password="my_password")
    await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
    assert len((await beekeeper.api.list_wallets()).wallets) == 1

    await beekeeper.api.import_key(wallet_name=wallet.name, wif_key=tt.Account("account").private_key)
    assert len((await beekeeper.api.get_public_keys()).keys) == 1

    await beekeeper.api.lock(wallet_name=wallet.name)
    await beekeeper.api.close(wallet_name=wallet.name)

    partial_function = functools.partial(create_and_unlock_sessions, url=beekeeper.http_endpoint.as_string(),
                                         wallet_name=wallet.name, wallet_password=wallet.password,
                                         request_count=request_count, nr_sessions=additional_sessions)

    with ThreadPoolExecutor(max_workers=additional_sessions) as executor:
        results = list(executor.map(partial_function, range(additional_sessions)))
    executor.shutdown(cancel_futures=True, wait=False)

    assert len([item for sublist in results for item in sublist]) == additional_sessions * request_count


def create_and_unlock_sessions(session_number, url: str, wallet_name: str, wallet_password: str,
                               request_count: int, nr_sessions: int) -> None:
    headers = {'Content-Type': 'application/json'}

    template = {
        "jsonrpc": "2.0",
        "method": "",
        "params": {},
        "id": 1
    }
    # create session
    create_session = copy.deepcopy(template)
    create_session["method"] = "beekeeper_api.create_session"
    create_session["params"] = {
        "salt": session_number,
        "notifications_endpoint": url
    }
    response_token = requests.post(url, json=create_session, headers=headers)
    token = json.loads(response_token.text)["result"]["token"]

    # It's impossible to unlock many wallets in short time, because we have 500ms protection against unlocking by bots.
    # Only one wallet can be unlocked every 500ms.
    protection_interval = 0.51

    # unlock
    unlock = copy.deepcopy(template)
    unlock["method"] = "beekeeper_api.unlock"
    unlock["params"] = {
        "token": token,
        "wallet_name": wallet_name,
        "password": wallet_password,
    }
    for _cnt in range(nr_sessions):
        time.sleep(protection_interval)
        unlock_response = requests.post(url, json=unlock, headers=headers)
        if "error" in json.loads(unlock_response.text) and "message" in json.loads(unlock_response.text)["error"]:
            assert "unlock is not accessible" in json.loads(unlock_response.text)["error"]["message"]
        else:
            break

    # get public keys
    get_public_keys = copy.deepcopy(template)
    get_public_keys["method"] = "beekeeper_api.get_public_keys"
    get_public_keys["params"] = {"token": token}

    keys = []
    for _ in range(request_count):
        response_get_public_keys = requests.post(url, json=get_public_keys, headers=headers)
        try:
            keys.append(json.loads(response_get_public_keys.text)["result"]["keys"][0]["public_key"])
        except KeyError:
            tt.logger.info(f"Session number: {session_number} keys: {response_get_public_keys.text}")
            raise AssertionError(f"Session number: {session_number} keys: {response_get_public_keys.text}")
    return keys
