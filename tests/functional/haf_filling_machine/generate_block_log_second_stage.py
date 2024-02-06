from __future__ import annotations

import asyncio
from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path
from typing import Final, Literal

import pytest
import test_tools as tt
from generate_operations import prepare_operations_for_transactions
from generate_transaction_template import (
    SimpleTransaction,
    generate_transaction_template,
)
from hive_local_tools import ALTERNATE_CHAIN_JSON_FILENAME
from hive_local_tools.functional.python.operation import get_vesting_price

import wax
from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools.models import Keys, WalletInfo
from schemas.operations.representations import HF26Representation

NUMBER_OF_ACCOUNTS: Final[int] = 100_000
ACCOUNTS_PER_CHUNK: Final[int] = 1024
CHUNKS: Final[int] = 10
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
    prepare_wallet(cli_wallet, signature_type)

    assert len(cli_wallet.api.list_witnesses("", 1000)) == 21, "Incorrect number of witnesses"
    assert get_vesting_price(node) > 1_799_990, "Too low price Hive to Vest"

    tt.logger.info("Start Create Operations")
    operations = prepare_operations_for_transactions(
        iterations=1, ops_in_one_element=1, elements_number_for_iteration=12_000
    )
    tt.logger.info("Finish Create Operations")

    ####################################################
    init_node_http_endpoint = node.http_endpoint
    init_node_ws_endpoint = node.ws_endpoint

    # Tworzymy pomocnicza obiekt reprezentujacy wallet z 0 parami kluczy priv/pub
    wallet = WalletInfo(name="my_only_wallet", password="my_password", keys=Keys(count=0))
    bbbbb = Beekeeper()
    bbbbb.config.webserver_thread_pool_size = CHUNKS + 1
    async with await bbbbb.launch() as beekeeper:
        # Tworzymy fizyczny wallet i importujemy do niego klucz
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
        # for pair in wallet.keys.pairs:
        #     await beekeeper.api.import_key(wallet_name=wallet.name, wif_key=pair.private_key.value)
        await beekeeper.api.import_key(wallet_name=wallet.name,
                                       wif_key=tt.Account("account", secret="owner").private_key)

        await beekeeper.api.lock(wallet_name=wallet.name)

        num_chunks = CHUNKS  # fixme: Dla 2 sesji działa w 50%, przy większej ilości powodzenie spada
        chunk_size = len(operations) // num_chunks
        chunks = [operations[i: i + chunk_size] for i in range(0, len(operations), chunk_size)]

        created_wallets = await beekeeper.api.list_created_wallets(token=beekeeper.token)
        tt.logger.warning(f"@@@ Beekeeper created_wallets (first token): {created_wallets}")

    # Sign transactions
    tt.logger.info("Start Signing Transactions")
    with ProcessPoolExecutor(max_workers=CHUNKS) as executor:
        num_chunks = CHUNKS
        chunk_size = len(operations) // num_chunks
        chunks = [operations[i: i + chunk_size] for i in range(0, len(operations), chunk_size)]

        futures: list[Future[list]] = []
        for iteration, chunk in enumerate(chunks):
            futures.append(executor.submit(asyncio_run, iteration, chunk, signature_type, node.http_endpoint.as_string(), node.ws_endpoint.as_string()))

        signed_transactions: list[list] = []
        for x in futures:
            signed_transactions.append(x.result())
    tt.logger.info("Finish Signing Transactions")


async def sign_chunk_of_transactions_by_beekeeper(
        chunk: list[dict],
        init_node_http_endpoint: str,
        init_node_ws_endpoint: str,
        signature_type: str,
        iteration: int,
) -> list:
    beekeeper = Beekeeper()
    await beekeeper.launch()

    wallet_name = f"process_wallet_{iteration}"
    await beekeeper.api.create(wallet_name=wallet_name, password="password")
    imported_key = await import_keys_to_beekeeper(beekeeper, f"process_wallet_{iteration}", signature_type)

    remote_node = tt.RemoteNode(http_endpoint=init_node_http_endpoint, ws_endpoint=init_node_ws_endpoint)

    gdpo = remote_node.api.database.get_dynamic_global_properties()
    node_config = remote_node.api.database.get_config()

    async def foo(file, pack_operations):
        trx: SimpleTransaction = generate_transaction_template(gdpo)
        for op in pack_operations:
            trx.add_operation(op)
        sig_digest_wax_response = wax.calculate_sig_digest(trx.json(by_alias=True).encode("ascii"), node_config.HIVE_CHAIN_ID.encode("ascii"))
        if sig_digest_wax_response.status != wax.python_error_code.ok:
            file.write(f"failed to calculate sign digest from wax: {sig_digest_wax_response.exception_message.decode('ascii')}" + "\n")
            file.write(f"tried to calculate for: {trx.json(by_alias=True)}\n")
            raise Exception(sig_digest_wax_response.exception_message)
        trx.signatures.append((await beekeeper.api.sign_digest(sig_digest=sig_digest_wax_response.result.decode("ascii"), public_key=imported_key[0])).signature)
        file.write(f"properly signed: {trx}\n\n")
        return trx

    transactions_in_chunk = []
    with (Path(".") / f"{wallet_name}.log").open("w") as sign_log:
        transactions_in_chunk = await asyncio.gather(*[foo(sign_log, pack_operations) for pack_operations in chunk])

    return transactions_in_chunk


async def import_keys_to_beekeeper(bk: Beekeeper, wallet_name: str, signature_type: str) -> list[tt.PublicKey]:
    match signature_type:
        case "open_sign":
            tt.logger.info("open_sign")
            return []
        case "single_sign":
            imported_owner = [(await bk.api.import_key(
                wallet_name=wallet_name, wif_key=tt.Account("account", secret="owner").private_key
            )).public_key]
            await bk.api.import_key(
                wallet_name=wallet_name, wif_key=tt.Account("account", secret="active").private_key
            )
            await bk.api.import_key(
                wallet_name=wallet_name, wif_key=tt.Account("account", secret="posting").private_key
            )
            return imported_owner
        case "multi_sign":
            imported_owner = [
                (await bk.api.import_key(
                    wallet_name=wallet_name, wif_key=tt.Account("account", secret=f"owner-{num}").private_key
                )).public_key
                for num in range(3)
            ]
            [
                await bk.api.import_key(
                    wallet_name=wallet_name, wif_key=tt.Account("account", secret=f"active-{num}").private_key
                )
                for num in range(6)
            ]
            [
                await bk.api.import_key(
                    wallet_name=wallet_name, wif_key=tt.Account("account", secret=f"posting-{num}").private_key
                )
                for num in range(10)
            ]
            return imported_owner
    return []


def prepare_wallet(wallet: tt.Wallet, signature_type: str) -> tt.Wallet:
    wallet.api.set_transaction_expiration(3600 - 1)

    match signature_type:
        case "open_sign":
            tt.logger.info("open_sign")
        case "single_sign":
            wallet.api.import_key(tt.PrivateKey("account", secret="owner"))
            wallet.api.import_key(tt.PrivateKey("account", secret="active"))
            wallet.api.import_key(tt.PrivateKey("account", secret="posting"))
        case "multi_sign":
            wallet.api.import_keys([tt.PrivateKey("account", secret=f"owner-{num}") for num in range(3)])
            wallet.api.import_keys([tt.PrivateKey("account", secret=f"active-{num}") for num in range(6)])
            wallet.api.import_keys([tt.PrivateKey("account", secret=f"posting-{num}") for num in range(10)])
    return wallet

def asyncio_run(i: int, chk: list[dict], sig_type: str, http: str, ws: str) -> list:
    return asyncio.run(sign_chunk_of_transactions_by_beekeeper(
            chk,
            http,
            ws,
            sig_type,
            i
        )
    )

class BroadcastTransactionsChunk:
    def broadcast_chunk_of_transactions(self, chunk: list[dict], init_node_address: str) -> None:
        remote_node = tt.RemoteNode(http_endpoint=init_node_address)
        for trx in chunk:
            remote_node.api.network_broadcast.broadcast_transaction(trx=trx)

