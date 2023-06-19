from __future__ import annotations

import time
from random import randint
from typing import TYPE_CHECKING

import test_tools as tt

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from test_tools.__private.asset import AssetBase

node = tt.InitNode()
node.config.webserver_http_endpoint = "0.0.0.0:8090"
node.config.plugin.append("account_history_rocksdb")
node.config.plugin.append("account_history_api")
node.config.plugin.append("reputation_api")
node.config.plugin.append("rc_api")
node.run()

wallet = tt.Wallet(attach_to=node, additional_arguments=["--transaction-serialization", "hf26"])
wallet.api.import_key(node.config.private_key[0])

# setup working account
creator = "initminer"
alice = tt.Account("alice")
wallet.create_account(
    alice.name, hives=tt.Asset.Test(100).as_nai(), vests=tt.Asset.Test(100).as_nai(), hbds=tt.Asset.Tbd(100).as_nai()
)

# setup watching accounts
watched_accounts = [tt.Account(name) for name in ("gtg", "god")]
random_assets: Callable[[type[AssetBase]], dict[str, Any]] = lambda asset: asset(randint(1_000, 5_000)).as_nai()  # type: ignore[no-any-return] # noqa: E731
for account in watched_accounts:
    wallet.create_account(
        account.name,
        hives=random_assets(tt.Asset.Test),
        vests=random_assets(tt.Asset.Test),
        hbds=random_assets(tt.Asset.Tbd),
    )

# test
wallet.api.transfer(alice.name, creator, tt.Asset.Test(1).as_nai(), memo="memo")

node.wait_number_of_blocks(2)
tt.logger.info(f"{alice.name} public key: {alice.public_key}")
tt.logger.info(f"{alice.name} private key: {alice.private_key}")
tt.logger.info("done!")

tt.logger.info("serving forever... press Ctrl+C to exit")

while True:
    time.sleep(1)
