from __future__ import annotations

from pathlib import Path
from typing import Final, Literal
import copy
import json
import requests

import pytest
import test_tools as tt

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools.models import Keys, WalletInfo
from hive_local_tools import ALTERNATE_CHAIN_JSON_FILENAME
from hive_local_tools.functional.python.operation import get_vesting_price

from generate_operations import generate_blocks

# Node parameters
SHARED_MEMORY_FILE_DIRECTORY: Final[str] = "/home/dev/Documents/full_block_generator/"
SHARED_MEMORY_FILE_SIZE: Final[int] = 24

# Processes parameters
SIGNING_MAX_WORKERS: Final[int] = 60
BROADCASTING_MAX_WORKERS: Final[int] = 8

# Block parameters
BLOCK_TO_GENERATE: Final[int] = 5
OPERATIONS_IN_TRANSACTION: Final[int] = 1
TRANSACTIONS_IN_ONE_BLOCK: Final[int] = 3720

NUMBER_OF_ACCOUNTS: Final[int] = 100_000
ACCOUNTS_PER_CHUNK: Final[int] = 1024
WITNESSES = [f"witness-{w}" for w in range(20)]
account_names = [f"account-{account}" for account in range(NUMBER_OF_ACCOUNTS)]


@pytest.mark.parametrize("signature_type", ["single_sign"])
# @pytest.mark.parematrize("signature_type", ["open_sign", "multi_sign", "single_sign"])
async def test_prepare_second_stage_of_block_log(
        signature_type: Literal["open_sign", "multi_sign", "single_sign"]) -> None:
    block_log_directory = Path(__file__).parent / f"block_log_{signature_type}"
    block_log_path = block_log_directory / "block_log"
    timestamp_path = block_log_directory / "timestamp"
    alternate_chain_spec_path = block_log_directory / ALTERNATE_CHAIN_JSON_FILENAME

    with open(timestamp_path, encoding="utf-8") as file:
        timestamp = tt.Time.parse(file.read())

    node = tt.InitNode()
    node.config.plugin.append("account_history_api")
    node.config.shared_file_size = f"{SHARED_MEMORY_FILE_SIZE}G"
    node.config.webserver_thread_pool_size = "16"
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
        replay_from=block_log_path,
        time_offset=tt.Time.serialize(timestamp, format_=tt.TimeFormats.TIME_OFFSET_FORMAT),
        wait_for_live=True,
        arguments=[
            f"--alternate-chain-spec={str(alternate_chain_spec_path)}",
            f"--shared-file-dir={SHARED_MEMORY_FILE_DIRECTORY}",
        ],
    )

    cli_wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization=hf26"])
    assert len(cli_wallet.api.list_witnesses("", 1000)) == 21, "Incorrect number of witnesses"
    assert get_vesting_price(node) > 1_799_990, "Too low price Hive to Vest"
    cli_wallet.close()

    gdpo = node.api.database.get_dynamic_global_properties()
    node_config = node.api.database.get_config()

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
            iterations=BLOCK_TO_GENERATE,
            ops_in_one_element=OPERATIONS_IN_TRANSACTION,
            elements_number_for_iteration=TRANSACTIONS_IN_ONE_BLOCK,
            tokens=tokens,
            beekeeper_url=beekeeper.http_endpoint.as_string(),
            gdpo=gdpo,
            node_config=node_config,
            signature_type=signature_type,
            node=node
        )

    # assert node.get_last_block_number() >= 57600, "Generated block log its shorted than 2 days."
    # waiting for the block with the last transaction to become irreversible
    # node.wait_for_irreversible_block()
    #
    # head_block_num = node.get_last_block_number()
    # timestamp = tt.Time.serialize(node.api.block.get_block(block_num=head_block_num).block.timestamp)
    # tt.logger.info(f"head block timestamp: {timestamp}")
    #
    # block_log_directory = Path(__file__).parent / f"block_log_second_stage_{signature_type}"
    #
    # with open(block_log_directory / "timestamp", "w", encoding="utf-8") as file:
    #     file.write(f"{timestamp}")
    #
    # node.close()
    # node.block_log.copy_to(Path(__file__).parent / f"block_log_second_stage_{signature_type}")


async def import_keys_to_beekeeper(bk: Beekeeper, wallet_name: str, signature_type: str):
    match signature_type:
        case "open_sign":
            tt.logger.info("open_sign")
        case "single_sign":
            await bk.api.import_key(
                wallet_name=wallet_name, wif_key=tt.Account("account", secret="owner").private_key
            )
            await bk.api.import_key(
                wallet_name=wallet_name, wif_key=tt.Account("account", secret="active").private_key
            )
            await bk.api.import_key(
                wallet_name=wallet_name, wif_key=tt.Account("account", secret="posting").private_key
            )
        case "multi_sign":
            [
                bk.api.import_key(
                    wallet_name=wallet_name, wif_key=tt.Account("account", secret=f"owner-{num}").private_key
                )
                for num in range(3)
            ]
            [
                bk.api.import_key(
                    wallet_name=wallet_name, wif_key=tt.Account("account", secret=f"active-{num}").private_key
                )
                for num in range(6)
            ]
            [
                bk.api.import_key(
                    wallet_name=wallet_name, wif_key=tt.Account("account", secret=f"posting-{num}").private_key
                )
                for num in range(10)
            ]


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


# if __name__ == "__main__":
# prepare_second_stage_of_block_log("open_sign")
# prepare_second_stage_of_block_log("single_sign")
# prepare_second_stage_of_block_log("multi_sign")
