from __future__ import annotations

import copy
import time
from functools import partial

import wax
import aiohttp
import asyncio
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import requests
from typing import Final, Literal

import pytest
from schemas.operations.representations import HF26Representation
from generate_operations import prepare_operations_for_transactions

import test_tools as tt
from hive_local_tools import ALTERNATE_CHAIN_JSON_FILENAME
from hive_local_tools.functional.python.operation import get_vesting_price

from clive.__private.core.beekeeper import Beekeeper

from generate_transaction_template import (
    generate_transaction_template,
    SimpleTransaction,
)

from clive_local_tools.models import Keys, WalletInfo

NUMBER_OF_ACCOUNTS: Final[int] = 100_000
ACCOUNTS_PER_CHUNK: Final[int] = 1024
SIGNING_MAX_WORKERS: Final[int] = 8  # fixme after repair
BROADCASTING_MAX_WORKERS: Final[int] = 8
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
    node.config.shared_file_size = "24G"
    node.config.webserver_thread_pool_size = "64"
    for witness in WITNESSES:
        key = tt.Account(witness).private_key
        node.config.witness.append(witness)
        node.config.private_key.append(key)

    node.run(
        replay_from=block_log_path,
        time_offset=tt.Time.serialize(timestamp, format_=tt.TimeFormats.TIME_OFFSET_FORMAT),
        wait_for_live=True,
        arguments=["--alternate-chain-spec", str(alternate_chain_spec_path)],
    )

    cli_wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization=hf26"])

    assert len(cli_wallet.api.list_witnesses("", 1000)) == 21, "Incorrect number of witnesses"
    assert get_vesting_price(node) > 1_799_990, "Too low price Hive to Vest"

    gdpo = node.api.database.get_dynamic_global_properties()
    node_config = node.api.database.get_config()

    node.close()

    tt.logger.info("Start Create Operations")
    start_time = time.time()  # fixme: delete comment
    transactions_in_one_block = 12000
    block_to_generate = 6
    operations_in_transaction = 1
    operations = prepare_operations_for_transactions(
        iterations=block_to_generate, ops_in_one_element=operations_in_transaction,
        elements_number_for_iteration=transactions_in_one_block
    )
    end_time = time.time()  # fixme: delete comment
    execution_time = end_time - start_time  # fixme: delete comment
    tt.logger.info(f">>>> Create operations time: {execution_time}")  # fixme: delete comment
    tt.logger.info("Finish Create Operations")

    operations_by_block = [operations[op:op + transactions_in_one_block] for op in
                           range(0, len(operations), transactions_in_one_block)]

    wallet = WalletInfo(name="my_only_wallet", password="my_password", keys=Keys(count=0))
    async with await Beekeeper().launch() as beekeeper:
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
        await import_keys_to_beekeeper(beekeeper, wallet.name, signature_type)
        await beekeeper.api.lock(wallet_name=wallet.name)
        await beekeeper.api.close(wallet_name=wallet.name)

        num_chunks = SIGNING_MAX_WORKERS
        chunk_size = len(operations) // num_chunks
        chunks = [operations[i: i + chunk_size] for i in range(0, len(operations), chunk_size)]

        ################################################################################################################
        start_time = time.time()  # fixme: delete comment
        # Signing

        with ProcessPoolExecutor(max_workers=SIGNING_MAX_WORKERS) as executor:
            chunk = len(operations_by_block[0]) // SIGNING_MAX_WORKERS  # tyle dostanie każdy worker

            start_sessions = []
            for iteration, chunk in enumerate(range(SIGNING_MAX_WORKERS)):  # fixme tutaj  SIGNING_MAX_WORKERS
                time.sleep(0.51)  # nie można spamować beekeeper:unlock -> zabezpieczenie przed botami
                start_sessions.append(executor.submit(start_session, beekeeper.http_endpoint.as_string(), iteration))

            tokens = []
            for future in as_completed(start_sessions):
                tokens.append(future.result())

            futures = []
            for time_offset, c in enumerate(operations_by_block):
                chunk_size = len(c) // SIGNING_MAX_WORKERS
                chunks = [operations[i: i + chunk_size] for i in range(0, len(c), chunk_size)]
                for num, cc in enumerate(chunks):
                    futures.append(executor.submit(sign,
                                                   beekeeper.http_endpoint.as_string(),
                                                   cc,
                                                   num,
                                                   tokens[num],
                                                   time_offset * 3,
                                                   gdpo,
                                                   node_config,
                                                   ))

        signed_transactions = [result for future in as_completed(futures) for result in future.result()]
        one_block_transactions = [signed_transactions[i:i + transactions_in_one_block] for i in
                                  range(0, len(signed_transactions), transactions_in_one_block)]

        executor.shutdown(cancel_futures=True, wait=False)
        end_time = time.time()  # fixme: delete comment
        execution_time = end_time - start_time  # fixme: delete comment
        tt.logger.info(f">>>TIME: {execution_time}, on {SIGNING_MAX_WORKERS} processes.")  # fixme: delete comment
        tt.logger.info(f"signed_transactions: {len(signed_transactions)}")  # fixme: delete comment

    # todo: sprawdzić czy się włączy
    node.run(
        replay_from=block_log_path,
        time_offset=tt.Time.serialize(timestamp, format_=tt.TimeFormats.TIME_OFFSET_FORMAT),
        wait_for_live=True,
        arguments=["--alternate-chain-spec", str(alternate_chain_spec_path)],
    )
    http_endpoint = node.http_endpoint
    # todo: czy tutaj jest taki sam endpoint

    # Broadcasting
    for block in one_block_transactions:
        tt.logger.info("Start Broadcasting")
        with ProcessPoolExecutor(max_workers=BROADCASTING_MAX_WORKERS) as executor:
            processor = BroadcastTransactionsChunk()

            num_chunks = BROADCASTING_MAX_WORKERS
            chunk_size = len(block) // num_chunks
            chunks = [block[i: i + chunk_size] for i in range(0, len(block), chunk_size)]

            single_transaction_broadcast_with_address = partial(
                processor.broadcast_chunk_of_transactions, init_node_address=http_endpoint
            )

            results = []
            results.extend(list(executor.map(single_transaction_broadcast_with_address, chunks)))
            executor.shutdown(cancel_futures=True, wait=False)
    tt.logger.info("Finish Broadcasting")
    ####################################################################################################################

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


def create_and_sign_transaction(ops, gdpo, node_config, num, url, token, public_key, time_offset):
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

    headers = {'Content-Type': 'application/json'}
    trx: SimpleTransaction = generate_transaction_template(gdpo, time_offset)
    trx.operations.append(
        *[HF26Representation(type=op.get_name_with_suffix(), value=op) for op in ops])
    sig_digest = wax.calculate_sig_digest(
        trx.json(by_alias=True).encode("ascii"), node_config.HIVE_CHAIN_ID.encode("ascii")
    ).result.decode("ascii")
    sig_digest_pack["params"]["sig_digest"] = sig_digest
    response_sig_digest = requests.post(url, json=sig_digest_pack, headers=headers)
    tt.logger.info(f"%%%SESSION {num} result:{json.loads(response_sig_digest.text)}")
    signature = json.loads(response_sig_digest.text)["result"]["signature"]
    trx.signatures.append(signature)
    return trx


def send_by_curl(url, chunk, init_node_http_endpoint, init_node_ws_endpoint, chunk_num):
    tt.logger.info(f"###Session send_by_curl: {chunk_num}, url: {url}")
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
    time.sleep(3)
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
    tt.logger.info(f"@@@Session number: {chunk_num} with token: {token} is ready.")

    get_public_keys = copy.deepcopy(template)
    get_public_keys["method"] = "beekeeper_api.get_public_keys"
    get_public_keys["params"] = {"token": token}
    response_get_public_keys = requests.post(url, json=get_public_keys, headers=headers)
    tt.logger.info(f"^^^Session number: {chunk_num} keys: {response_get_public_keys.text}")

    remote_node = tt.RemoteNode(http_endpoint=init_node_http_endpoint, ws_endpoint=init_node_ws_endpoint)
    gdpo = remote_node.api.database.get_dynamic_global_properties()
    node_config = remote_node.api.database.get_config()

    public_key = tt.Account("account", secret="owner").public_key[3:]

    tt.logger.info(f"$$$Session start id: {chunk_num}, token: {token}")

    singed_chunks = []
    for operation in chunk:
        try:
            trx = create_and_sign_transaction(operation, gdpo, node_config, chunk_num, url, token, public_key)
            singed_chunks.append(trx)
        except:
            tt.logger.info("fail")
    return singed_chunks


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


class BroadcastTransactionsChunk:
    @staticmethod
    def broadcast_chunk_of_transactions(chunk: list[dict], init_node_address: str) -> None:
        remote_node = tt.RemoteNode(http_endpoint=init_node_address)
        for trx in chunk:
            remote_node.api.network_broadcast.broadcast_transaction(trx=trx)


def start_session(url, chunk_num):
    tt.logger.info(f"###Session send_by_curl: {chunk_num}, url: {url}")
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
    time.sleep(3)
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
    tt.logger.info(f"@@@Session number: {chunk_num} with token: {token} is ready.")

    get_public_keys = copy.deepcopy(template)
    get_public_keys["method"] = "beekeeper_api.get_public_keys"
    get_public_keys["params"] = {"token": token}
    response_get_public_keys = requests.post(url, json=get_public_keys, headers=headers)
    tt.logger.info(f"^^^Session number: {chunk_num} keys: {response_get_public_keys.text}")

    return token

    # remote_node = tt.RemoteNode(http_endpoint=init_node_http_endpoint, ws_endpoint=init_node_ws_endpoint)
    # gdpo = remote_node.api.database.get_dynamic_global_properties()
    # node_config = remote_node.api.database.get_config()
    #
    # public_key = tt.Account("account", secret="owner").public_key[3:]
    #
    # tt.logger.info(f"$$$Session start id: {chunk_num}, token: {token}")
    #
    # singed_chunks = []
    # for operation in chunk:
    #     try:
    #         trx = create_and_sign_transaction(operation, gdpo, node_config, chunk_num, url, token, public_key)
    #         singed_chunks.append(trx)
    #     except:
    #         tt.logger.info("fail")
    # return singed_chunks


def sign(url, chunk, chunk_num, token, time_offset, gdpo, node_config):
    tt.logger.info(f"###sign: {chunk_num}, url: {url}")
    public_key = tt.Account("account", secret="owner").public_key[3:]
    tt.logger.info(f"$$$Session start id: {chunk_num}, token: {token}")
    singed_chunks = []
    for operation in chunk:
        try:
            trx = create_and_sign_transaction(operation, gdpo, node_config, chunk_num, url, token, public_key,
                                              time_offset)
            singed_chunks.append(trx)
        except:
            tt.logger.info("fail")
    return singed_chunks

# if __name__ == "__main__":
# prepare_second_stage_of_block_log("open_sign")
# prepare_second_stage_of_block_log("single_sign")
# prepare_second_stage_of_block_log("multi_sign")
