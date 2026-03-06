from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

import pytest
import test_tools as tt

from clive.__private.core.keys.keys import PrivateKey
from clive_local_tools.checkers.blockchain_checkers import assert_transaction_in_blockchain
from clive_local_tools.data.constants import WORKING_ACCOUNT_KEY_ALIAS
from clive_local_tools.helpers import get_signatures_count_from_output
from clive_local_tools.testnet_block_log.constants import (
    WATCHED_ACCOUNTS_DATA,
    WORKING_ACCOUNT_DATA,
    WORKING_ACCOUNT_NAME,
)

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

RECEIVER: Final[str] = WATCHED_ACCOUNTS_DATA[0].account.name
AMOUNT: Final[tt.Asset.HiveT] = tt.Asset.Hive(1)


@dataclass(frozen=True)
class KeyAuth:
    """Key authority entry: a reference to a key and its weight."""

    key_ref: str
    weight: int


@dataclass(frozen=True)
class AccountAuth:
    """Account authority entry: an account name and its weight."""

    account: str
    weight: int


@dataclass(frozen=True)
class Authority:
    """Desired active authority configuration."""

    threshold: int
    key_auths: tuple[KeyAuth, ...] = ()
    account_auths: tuple[AccountAuth, ...] = ()


ACCOUNT_PUB_KEYS: Final[dict[str, str]] = {
    "alice": WORKING_ACCOUNT_DATA.account.public_key,
    "bob": WATCHED_ACCOUNTS_DATA[0].account.public_key,
    "timmy": WATCHED_ACCOUNTS_DATA[1].account.public_key,
    "john": WATCHED_ACCOUNTS_DATA[2].account.public_key,
}
ACCOUNT_PRIV_KEYS: Final[dict[str, str]] = {
    "alice": WORKING_ACCOUNT_DATA.account.private_key,
    "bob": WATCHED_ACCOUNTS_DATA[0].account.private_key,
    "timmy": WATCHED_ACCOUNTS_DATA[1].account.private_key,
    "john": WATCHED_ACCOUNTS_DATA[2].account.private_key,
}

ALICE_DEFAULT_AUTH: Final[Authority] = Authority(threshold=1, key_auths=(KeyAuth("alice", 1),))


def _alias(ref: str) -> str:
    """Get wallet alias for a key reference."""
    if ref == "alice":
        return WORKING_ACCOUNT_KEY_ALIAS
    return f"{ref}_key" if ref in ACCOUNT_PUB_KEYS else ref


def _apply_authority_change(  # noqa: PLR0913
    cli_tester: CLITester,
    account_name: str | None,
    sign_with: str,
    original_key_ref: str,
    target: Authority,
    pub_keys: dict[str, str],
) -> None:
    """Apply authority changes to reach the target state from default (threshold=1, own key weight 1)."""
    chain = cli_tester.process_update_authority(
        "active",
        account_name=account_name,
        sign_with=sign_with,
        threshold=target.threshold,
    )

    # Handle the original key (default: weight 1 in authority)
    original_in_target = next((ka for ka in target.key_auths if ka.key_ref == original_key_ref), None)
    if original_in_target is None:
        chain = chain.remove_key(key=pub_keys[original_key_ref])
    elif original_in_target.weight != 1:
        chain = chain.modify_key(key=pub_keys[original_key_ref], weight=original_in_target.weight)

    # Add new keys (skip the original, already handled above)
    for ka in target.key_auths:
        if ka.key_ref != original_key_ref:
            chain = chain.add_key(key=pub_keys[ka.key_ref], weight=ka.weight)

    # Add account authorities
    for aa in target.account_auths:
        chain = chain.add_account(account=aa.account, weight=aa.weight)

    chain.fire()


SCENARIOS = [
    pytest.param(
        ["alice", "gen_0"],
        Authority(threshold=2, key_auths=(KeyAuth("alice", 1), KeyAuth("gen_0", 1))),
        {},
        id="two_keys_both_needed",
    ),
    pytest.param(
        ["alice", "gen_0"],
        Authority(threshold=1, key_auths=(KeyAuth("alice", 1), KeyAuth("gen_0", 1))),
        {},
        id="two_keys_one_sufficient",
    ),
    pytest.param(
        ["alice", "gen_0", "gen_1"],
        Authority(threshold=2, key_auths=(KeyAuth("alice", 1), KeyAuth("gen_0", 1), KeyAuth("gen_1", 1))),
        {},
        id="three_keys_threshold_2",
    ),
    pytest.param(
        ["alice", "gen_0"],
        Authority(threshold=3, key_auths=(KeyAuth("alice", 2), KeyAuth("gen_0", 1))),
        {},
        id="weighted_keys_both_needed",
    ),
    pytest.param(
        ["alice", "bob"],
        Authority(threshold=2, key_auths=(KeyAuth("alice", 1),), account_auths=(AccountAuth("bob", 1),)),
        {},
        id="account_auth_with_key",
    ),
    pytest.param(
        ["alice", "bob"],
        Authority(threshold=1, account_auths=(AccountAuth("bob", 1),)),
        {},
        id="account_auth_replaces_key",
    ),
    pytest.param(
        ["alice", "bob", "timmy"],
        Authority(threshold=2, account_auths=(AccountAuth("bob", 1), AccountAuth("timmy", 1))),
        {},
        id="two_account_auths",
    ),
    pytest.param(
        ["alice", "gen_0", "bob"],
        Authority(
            threshold=3,
            key_auths=(KeyAuth("alice", 1), KeyAuth("gen_0", 1)),
            account_auths=(AccountAuth("bob", 1),),
        ),
        {},
        id="mixed_key_and_account_auth",
    ),
    pytest.param(
        ["alice", "bob", "timmy"],
        Authority(threshold=1, account_auths=(AccountAuth("bob", 1),)),
        {"bob": Authority(threshold=1, account_auths=(AccountAuth("timmy", 1),))},
        id="chained_account_auth_depth_2",
    ),
    pytest.param(
        ["alice", "bob"],
        Authority(threshold=3, key_auths=(KeyAuth("alice", 2),), account_auths=(AccountAuth("bob", 2),)),
        {},
        id="account_auth_with_weighted_threshold",
    ),
]


@pytest.mark.parametrize(("wallet_keys", "alice_authority", "watched_authorities"), SCENARIOS)
async def test_autosign_with_multiple_keys(
    node: tt.RawNode,
    cli_tester: CLITester,
    wallet_keys: list[str],
    alice_authority: Authority,
    watched_authorities: dict[str, Authority],
) -> None:
    """Test that autosign correctly signs transfers with various multi-key authority configurations."""
    # ARRANGE
    # Collect all key references to determine which generated keys are needed
    all_refs: set[str] = set(wallet_keys)
    for ka in alice_authority.key_auths:
        all_refs.add(ka.key_ref)
    for auth in watched_authorities.values():
        for ka in auth.key_auths:
            all_refs.add(ka.key_ref)

    # Build key maps (copies of module-level + generated keys)
    pub_keys = dict(ACCOUNT_PUB_KEYS)
    priv_keys = dict(ACCOUNT_PRIV_KEYS)
    for ref in sorted(r for r in all_refs if r.startswith("gen_")):
        key = PrivateKey.generate()
        priv_keys[ref] = key.value
        pub_keys[ref] = key.calculate_public_key().value

    # Import keys into wallet (alice is already imported by the fixture)
    keys_to_import = set(wallet_keys) | set(watched_authorities.keys())
    for ref in sorted(keys_to_import - {"alice"}):
        cli_tester.configure_key_add(key=priv_keys[ref], alias=_alias(ref))

    # Apply alice's authority changes if needed
    if alice_authority != ALICE_DEFAULT_AUTH:
        _apply_authority_change(cli_tester, None, WORKING_ACCOUNT_KEY_ALIAS, "alice", alice_authority, pub_keys)

    # Apply watched accounts' authority changes
    for acct, auth in watched_authorities.items():
        _apply_authority_change(cli_tester, acct, _alias(acct), acct, auth, pub_keys)

    # Wait for authority changes to be included in a block so the new authorities
    # are active when the transfer transaction is validated by the node.
    node.wait_number_of_blocks(1)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        to=RECEIVER,
    )

    # ASSERT
    signatures_count = get_signatures_count_from_output(result.stdout)
    tt.logger.info(f"Signatures placed: {signatures_count}")
    assert_transaction_in_blockchain(node, result)


@pytest.mark.parametrize("threshold", [1, 2])
async def test_autosign_with_two_active_keys_and_threshold(
    node: tt.RawNode,
    cli_tester: CLITester,
    threshold: int,
) -> None:
    """Test autosign with two active keys both imported into wallet, parametrized by threshold."""
    # ARRANGE
    generated_key = PrivateKey.generate()
    pub_keys = dict(ACCOUNT_PUB_KEYS)
    pub_keys["gen_0"] = generated_key.calculate_public_key().value

    cli_tester.configure_key_add(key=generated_key.value, alias="gen_0_key")

    authority = Authority(threshold=threshold, key_auths=(KeyAuth("alice", 1), KeyAuth("gen_0", 1)))
    _apply_authority_change(cli_tester, None, WORKING_ACCOUNT_KEY_ALIAS, "alice", authority, pub_keys)
    node.wait_number_of_blocks(1)

    # ACT
    result = cli_tester.process_transfer(
        from_=WORKING_ACCOUNT_NAME,
        amount=AMOUNT,
        to=RECEIVER,
    )

    # ASSERT
    assert_transaction_in_blockchain(node, result)
    assert get_signatures_count_from_output(result.stdout) == threshold
