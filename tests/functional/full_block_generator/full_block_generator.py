from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Final, Literal
import copy
import json
import requests
from shutil import rmtree

import test_tools as tt

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools.models import Keys, WalletInfo
from tests.functional.full_block_generator.generate_block_log_with_varied_signature_types import WITNESSES
from hive_local_tools import ALTERNATE_CHAIN_JSON_FILENAME
from generate_operations import generate_blocks

SIGNATURE_TYPE: Literal["open_sign", "single_sign", "multi_sign"] = "single_sign"

# Node parameters
SHARED_MEMORY_FILE_DIRECTORY: Final[str] = "/home/dev/Documents/full_block_generator/"
SHARED_MEMORY_FILE_SIZE: Final[int] = 24
WEBSERVER_THREAD_POOL_SIZE: Final[int] = 16

# Processes parameters
SIGNING_MAX_WORKERS: Final[int] = 63
BROADCASTING_MAX_WORKERS: Final[int] = 16

# Block parameters
STOP_AT_BLOCK: int | None = None
OPERATIONS_IN_TRANSACTION: Final[int] = 1
# 70 (4200 trx for open_sign), 60 ( 3780 trx for single_sign ), 40 (2400 trx for multi_sign)
TRANSACTIONS_IN_ONE_BLOCK: Final[int] = SIGNING_MAX_WORKERS * 60


async def full_block_generator(signature_type: Literal["open_sign", "multi_sign", "single_sign"]) -> None:
    # fixme: delete after repair ( https://gitlab.syncad.com/hive/test-tools/-/issues/44 ). From this
    clive_path = Path("/home/dev/.clive")
    if not os.path.exists(clive_path):
        os.makedirs(clive_path)
    if os.path.exists(clive_path / "beekeeper"):
        rmtree(clive_path / "beekeeper", ignore_errors=False, onerror=None)
    generated_directory = Path(__file__).parent / "generated"
    if not os.path.exists(generated_directory):
        os.makedirs(generated_directory)
    # fixme: To this

    block_log_directory = Path(__file__).parent / f"block_log_{signature_type}"
    block_log = tt.BlockLog(block_log_directory / "block_log")
    alternate_chain_spec_path = block_log_directory / ALTERNATE_CHAIN_JSON_FILENAME

    node = tt.InitNode()

    node.config.plugin.remove("account_by_key")
    node.config.plugin.remove("state_snapshot")
    node.config.plugin.remove("account_by_key_api")
    node.config.shared_file_size = f"{SHARED_MEMORY_FILE_SIZE}G"
    node.config.webserver_thread_pool_size = f"{str(WEBSERVER_THREAD_POOL_SIZE)}"
    node.config.log_logger = (
        '{"name":"default","level":"info","appender":"stderr"} '
        '{"name":"user","level":"debug","appender":"stderr"} '
        '{"name":"chainlock","level":"error","appender":"p2p"} '
        '{"name":"sync","level":"debug","appender":"p2p"} '
        '{"name":"p2p","level":"debug","appender":"p2p"}'
    )

    for witness in WITNESSES:
        key = tt.Account(witness).private_key
        node.config.witness.append(witness)
        node.config.private_key.append(key)

    node.run(
        replay_from=block_log,
        time_offset=tt.Time.serialize(block_log.get_head_block_time(), format_=tt.TimeFormats.TIME_OFFSET_FORMAT),
        timeout=120,
        wait_for_live=True,
        arguments=[
            f"--alternate-chain-spec={str(alternate_chain_spec_path)}",
            f"--shared-file-dir={SHARED_MEMORY_FILE_DIRECTORY}",
        ],
    )

    wallet = WalletInfo(name="my_only_wallet", password="my_password", keys=Keys(count=0))
    async with await Beekeeper().launch() as beekeeper:
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
        await import_keys_to_beekeeper(beekeeper, wallet.name, signature_type)
        await beekeeper.api.lock(wallet_name=wallet.name)
        await beekeeper.api.close(wallet_name=wallet.name)

        # Create and unlock sessions
        tokens = []
        for iteration, chunk in enumerate(range(SIGNING_MAX_WORKERS)):
            tokens.append(start_session(beekeeper.http_endpoint.as_string(), iteration))

        # Create signing transactions
        generate_blocks(
            stop_at_block=STOP_AT_BLOCK,
            ops_in_one_element=OPERATIONS_IN_TRANSACTION,
            elements_number_for_iteration=TRANSACTIONS_IN_ONE_BLOCK,
            tokens=tokens,
            beekeeper_url=beekeeper.http_endpoint.as_string(),
            node=node,
            max_broadcast_workers=BROADCASTING_MAX_WORKERS,
            public_keys=get_public_keys(signature_type)["active"]
        )


async def import_keys_to_beekeeper(bk: Beekeeper, wallet_name: str, signature_type: str):
    match signature_type:
        case "single_sign":
            for authority_type in ["owner", "active", "posting"]:
                await bk.api.import_key(
                    wallet_name=wallet_name,
                    wif_key=tt.Account("account", secret=authority_type).private_key
                )
        case "multi_sign":
            for authority_type, num_keys in [("owner", 3), ("active", 6), ("posting", 10)]:
                for num in range(num_keys):
                    await bk.api.import_key(
                        wallet_name=wallet_name,
                        wif_key=tt.Account("account", secret=f"{authority_type}-{num}").private_key
                    )


def start_session(url, chunk_num):
    headers = {'Content-Type': 'application/json'}
    template = {
        "jsonrpc": "2.0",
        "method": "",
        "params": {},
        "id": 1
    }

    create_session = copy.deepcopy(template)
    create_session["method"] = "beekeeper_api.create_session"
    create_session["params"] = {
        "salt": chunk_num,
        "notifications_endpoint": url
    }
    response_token = requests.post(url, json=create_session, headers=headers)
    token = json.loads(response_token.text)["result"]["token"]

    unlock = copy.deepcopy(template)
    unlock["method"] = "beekeeper_api.unlock"
    unlock["params"] = {
        "token": token,
        "wallet_name": "my_only_wallet",
        "password": "my_password",
    }
    requests.post(url, json=unlock, headers=headers)

    return token


def get_public_keys(authority_type: Literal["open_sign", "multi_sign", "single_sign"]) -> dict[str:list]:
    match authority_type:
        case "open_sign":
            return {
                "owner": [],
                "active": [],
                "posting": [],
            }
        case "single_sign":
            return {
                "owner": [tt.Account("account", secret="owner").public_key[3:]],
                "active": [tt.Account("account", secret="active").public_key[3:]],
                "posting": [tt.Account("account", secret="posting").public_key[3:]],
            }
        case "multi_sign":
            return {
                "owner": [tt.Account("account", secret=f"owner-{num}").public_key[3:] for num in range(3)],
                "active": [tt.Account("account", secret=f"active-{num}").public_key[3:] for num in range(6)],
                "posting": [tt.Account("account", secret=f"posting-{num}").public_key[3:] for num in range(10)],
            }


if __name__ == "__main__":
    asyncio.run(full_block_generator(SIGNATURE_TYPE))
