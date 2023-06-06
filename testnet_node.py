from __future__ import annotations

import os
import time
from collections.abc import Callable  # noqa: TCH003

import test_tools as tt

node = tt.InitNode()
node.config.webserver_http_endpoint = "0.0.0.0:8090"
node.config.plugin.append("account_history_rocksdb")
node.config.plugin.append("account_history_api")
node.run()

wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
wallet.api.import_key(node.config.private_key[0])

# setup account
creator = "initminer"
alice = tt.Account("alice")
wallet.create_account(
    alice.name, hives=tt.Asset.Test(100).as_nai(), vests=tt.Asset.Test(100).as_nai(), hbds=tt.Asset.Tbd(100).as_nai()
)

# test
wallet.api.transfer(alice.name, creator, tt.Asset.Test(1).as_nai(), memo="memo")

node.wait_number_of_blocks(2)
tt.logger.info(f"{alice.name} public key: {alice.public_key}")
tt.logger.info(f"{alice.name} private key: {alice.private_key}")
tt.logger.info("done!")


# wait
should_continue: Callable[[], bool] = lambda: input("type 'exit' to exit: ") != "exit"  # noqa: E731
if os.environ.get("SERVE_FOREVER", False):
    tt.logger.info("serving forever... press Ctrl+C to exit")
    should_continue = lambda: True  # noqa: E731

while should_continue():
    time.sleep(1)
