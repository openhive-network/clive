from __future__ import annotations

import json
from typing import TYPE_CHECKING, Final

from clive.__private.core.keys import PrivateKey, PublicKey
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES

if TYPE_CHECKING:
    from clive_local_tools.cli.cli_tester import CLITester

SEED: Final[str] = "seed with multiple words"
ROLE: Final[str] = "other_role"


async def test_generate_key_pair(cli_tester_without_remote_address: CLITester) -> None:
    """Check clive generate key-from-seed command."""
    # ACT
    result = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ASSERT
    parsed = json.loads(result.stdout)
    assert len(parsed) == 2, "There should be two keys: private and public in output."  # noqa: PLR2004
    assert PublicKey(value=parsed[0]) == PrivateKey(value=parsed[1]).calculate_public_key(), (
        "Public key should match private key."
    )


async def test_generate_twice(cli_tester_without_remote_address: CLITester) -> None:
    """Check clive generate key-from-seed command gives same output multiple times."""
    # ARRANGE
    first = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ACT
    second = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ASSERT
    assert first.output == second.output, (
        "The key should be the same across different `clive generate key-from-seed` runs."
    )


async def test_generate_only_private_key(cli_tester_without_remote_address: CLITester) -> None:
    """Check clive generate key-from-seed command with `only-private-key` option."""
    # ACT
    result = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_private_key=True
    )

    # ASSERT
    value = result.stdout.strip()
    assert "\n" not in value, "There should be only one line in output."
    PrivateKey.validate(value)


async def test_generate_only_public_key(cli_tester_without_remote_address: CLITester) -> None:
    """Check clive generate key-from-seed command with `only-public-key` option."""
    # ACT
    result = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_public_key=True
    )

    # ASSERT
    value = result.stdout.strip()
    assert "\n" not in value, "There should be only one line in output."


async def test_generate_public_key_matches_private_key(cli_tester_without_remote_address: CLITester) -> None:
    """Check that clive generate key-from-seed generates private key matching public key."""
    # ARRANGE
    result_public_key = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_public_key=True
    )
    public_key = PublicKey(value=result_public_key.stdout.strip())

    # ACT
    result_private_key = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_private_key=True
    )
    private_key = PrivateKey(value=result_private_key.stdout.strip())

    # ASSERT
    assert private_key.calculate_public_key() == public_key, (
        "Generated private key should match previously generated public key."
    )


async def test_generate_key_from_seed_depends_on_account_name(cli_tester_without_remote_address: CLITester) -> None:
    """Check clive generate key-from-seed command is different for different `account-name` argument."""
    # ACT
    result0 = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_private_key=True
    )
    result1 = cli_tester_without_remote_address.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[1], role=ROLE, password_stdin=SEED, only_private_key=True
    )

    # ASSERT
    assert result0.stdout != result1.stdout, "There should be different result for different account names."
