from __future__ import annotations

import copy
import time
from functools import partial

import wax
import json
from concurrent.futures import ProcessPoolExecutor, as_completed, Future
from pathlib import Path
import requests
from typing import Final, Literal

import pytest
from schemas.operations.representations import HF26Representation
from generate_operations import prepare_operations_for_transactions, prepare_blocks

import test_tools as tt
from hive_local_tools import ALTERNATE_CHAIN_JSON_FILENAME
from hive_local_tools.functional.python.operation import get_vesting_price

from clive.__private.core.beekeeper import Beekeeper

from generate_transaction_template import (
    generate_transaction_template,
    SimpleTransaction,
)

from clive_local_tools.models import Keys, WalletInfo

# Node parameters
SHARED_MEMORY_FILE_DIRECTORY: Final[str] = "/home/dev/Documents/full_block_generator/"
SHARED_MEMORY_FILE_SIZE: Final[int] = 24

#
SIGNING_MAX_WORKERS: Final[int] = 60
BROADCASTING_MAX_WORKERS: Final[int] = 8

# Block parameters
BLOCK_TO_GENERATE: Final[int] = 5
OPERATIONS_IN_TRANSACTION: Final[int] = 1
TRANSACTIONS_IN_ONE_BLOCK: Final[int] = 6000

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

    gdpo = node.api.database.get_dynamic_global_properties()
    node_config = node.api.database.get_config()

    # node.close()

    wallet = WalletInfo(name="my_only_wallet", password="my_password", keys=Keys(count=0))
    async with await Beekeeper().launch() as beekeeper:
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
        await import_keys_to_beekeeper(beekeeper, wallet.name, signature_type)
        await beekeeper.api.lock(wallet_name=wallet.name)
        await beekeeper.api.close(wallet_name=wallet.name)

        # Create and unlock sessions
        tokens = []
        for iteration, chunk in enumerate(range(SIGNING_MAX_WORKERS)):
            # time.sleep(0.51)  # the minimum time between unlocking subsequent beekeeper sessions is 0.50s
            tokens.append(start_session(beekeeper.http_endpoint.as_string(), iteration))

        # Create signing transactions
        start_time = time.time()  # fixme: delete comment
        prepare_blocks(
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
        end_time = time.time()  # fixme: delete comment
        execution_time = end_time - start_time  # fixme: delete comment
        tt.logger.info(
            f"prepare_blocks::time: {execution_time}, on {SIGNING_MAX_WORKERS} processes.")  # fixme: delete comment

        # # Signing
        # start_time = time.time()  # fixme: delete comment
        # with ProcessPoolExecutor(max_workers=SIGNING_MAX_WORKERS) as executor:
        #     blocks = []
        #     for time_offset, c in enumerate(operations_by_block):
        #         chunk_size = len(c) // SIGNING_MAX_WORKERS
        #         chunks = [c[i: i + chunk_size] for i in range(0, len(c), chunk_size)]
        #         sign_futures: list[Future] = []
        #         assert len(tokens) == len(chunks)
        #         for num, cc in enumerate(chunks):
        #             sign_futures.append(executor.submit(sign,
        #                                                 beekeeper.http_endpoint.as_string(),
        #                                                 cc,
        #                                                 num,
        #                                                 tokens[num],
        #                                                 time_offset * 3,
        #                                                 gdpo,
        #                                                 node_config,
        #                                                 signature_type
        #                                                 ))
        #         results = [None] * len(chunks)
        #         for future in as_completed(sign_futures):
        #             index = sign_futures.index(future)
        #             results[index] = future.result()
        #         sign_futures.clear()
        #         blocks.append([item for sublist in results for item in sublist])
        #
        # executor.shutdown(cancel_futures=True, wait=False)
        # end_time = time.time()  # fixme: delete comment
        # execution_time = end_time - start_time  # fixme: delete comment
        # tt.logger.info(f">>>TIME: {execution_time}, on {SIGNING_MAX_WORKERS} processes.")  # fixme: delete comment

    # create_send_pack(blocks)

    # node.run(
    #     replay_from=block_log_path,
    #     time_offset=tt.Time.serialize(timestamp, format_=tt.TimeFormats.TIME_OFFSET_FORMAT),
    #     wait_for_live=True,
    #     arguments=[
    #         f"--alternate-chain-spec={str(alternate_chain_spec_path)}",
    #         f"--shared-file-dir={SHARED_MEMORY_FILE_DIRECTORY}",
    #     ],
    # )
    #
    # # Broadcasting
    # for block in range(BLOCK_TO_GENERATE):
    #     transactions = []
    #     with open(Path(__file__).parent / f"block_log_{signature_type}/full_blocks/block_{block}.txt", 'r') as file:
    #         for transaction in file:
    #             transactions.append(json.loads(transaction))
    #
    #     tt.logger.info("Start Broadcasting")
    #     with ProcessPoolExecutor(max_workers=BROADCASTING_MAX_WORKERS) as executor:
    #         processor = BroadcastTransactionsChunk()
    #
    #         num_chunks = BROADCASTING_MAX_WORKERS
    #         chunk_size = len(transactions) // num_chunks
    #         chunks = [transactions[i: i + chunk_size] for i in range(0, len(transactions), chunk_size)]
    #
    #         single_transaction_broadcast_with_address = partial(
    #             processor.broadcast_chunk_of_transactions, init_node_address=node.http_endpoint
    #         )
    #
    #         results = []
    #         results.extend(list(executor.map(single_transaction_broadcast_with_address, chunks)))
    #         executor.shutdown(cancel_futures=True, wait=False)
    #         transactions.clear()
    # tt.logger.info("Finish Broadcasting")

    # todo: część zapisu block_loga
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


def create_send_pack(blocks) -> list:
    template = {
        "jsonrpc": "2.0",
        "method": "network_broadcast_api.broadcast_transaction",
        "params": {},
        "id": 0,
    }
    for block_num, block in enumerate(blocks):
        transactions = []
        for trx_num, trx in enumerate(block):
            message = copy.deepcopy(template)
            message["params"] = {"trx": json.loads(wax.deserialize_transaction(trx).result.decode('ascii'))}
            transactions.append(message)
        blocks[block_num] = transactions


def create_and_sign_transaction(ops, gdpo, node_config, num, url, token, public_key, time_offset, authority_type):
    trx: SimpleTransaction = generate_transaction_template(gdpo, time_offset)
    trx.operations.extend(
        [HF26Representation(type=op.get_name_with_suffix(), value=op) for op in ops])

    if authority_type != "open_sign":
        headers = {'Content-Type': 'application/json'}

        sig_digest_pack = {
            "jsonrpc": "2.0",
            "method": "beekeeper_api.sign_digest",
            "params": {
                "token": token,
                "sig_digest": "",
                "public_key": public_key,
            },
            "id": 1
        }

        sig_digest = wax.calculate_sig_digest(
            trx.json(by_alias=True).encode("ascii"), node_config.HIVE_CHAIN_ID.encode("ascii")
        ).result.decode("ascii")
        sig_digest_pack["params"]["sig_digest"] = sig_digest
        response_sig_digest = requests.post(url, json=sig_digest_pack, headers=headers)
        signature = json.loads(response_sig_digest.text)["result"]["signature"]
        trx.signatures.append(signature)
    binary_transaction = wax.serialize_transaction(trx.json(by_alias=True).encode("ascii")).result
    return binary_transaction


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
