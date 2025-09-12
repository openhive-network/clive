from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.keys import PrivateKey, PublicKey
from clive_local_tools.cli.checkers import assert_no_exit_code_error
from clive_local_tools.testnet_block_log.constants import WATCHED_ACCOUNTS_NAMES

if TYPE_CHECKING:
    from clive.__private.core.types import AuthorityLevel
    from clive_local_tools.cli.cli_tester import CLITester

SEED: Final[str] = "seed with multiple words"
ROLE: Final[AuthorityLevel] = "owner"


@pytest.mark.parametrize(
    "cli_tester_variant",
    [
        "unlocked",
        "locked",
        "without remote address",
        "without session token",
    ],
    indirect=True,
)
async def test_command_is_working_in_environment(cli_tester_variant: CLITester) -> None:
    # ACT
    result = cli_tester_variant.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ASSERT
    assert_no_exit_code_error(result)


async def test_generate_key_pair(cli_tester_locked: CLITester) -> None:
    """Check clive generate key-from-seed command."""
    # ACT
    result = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ASSERT
    lines = result.stdout.strip().split("\n")
    private_key = PrivateKey(value=lines[0])
    public_key = PublicKey(value=lines[1])
    assert public_key == private_key.calculate_public_key(), "Public key should match private key."


async def test_is_deterministic(cli_tester_locked: CLITester) -> None:
    """Check clive generate key-from-seed command gives same output multiple times."""
    # ARRANGE
    first = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ACT
    second = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED
    )

    # ASSERT
    assert first.output == second.output, (
        "The key should be the same across different `clive generate key-from-seed` runs."
    )


async def test_generate_only_private_key(cli_tester_locked: CLITester) -> None:
    """Check clive generate key-from-seed command with `only-private-key` option."""
    # ACT
    result = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_private_key=True
    )

    # ASSERT
    value = result.stdout.strip()
    assert "\n" not in value, "There should be only one line in output."
    PrivateKey.validate(value)


async def test_generate_only_public_key(cli_tester_locked: CLITester) -> None:
    """Check clive generate key-from-seed command with `only-public-key` option."""
    # ACT
    result = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_public_key=True
    )

    # ASSERT
    value = result.stdout.strip()
    assert "\n" not in value, "There should be only one line in output."
    PublicKey.validate(value)


async def test_generate_public_key_matches_private_key(cli_tester_locked: CLITester) -> None:
    """Check that clive generate key-from-seed generates private key matching public key."""
    # ARRANGE
    result_public_key = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_public_key=True
    )
    public_key = PublicKey(value=result_public_key.stdout.strip())

    # ACT
    result_private_key = cli_tester_locked.generate_key_from_seed(
        account_name=WATCHED_ACCOUNTS_NAMES[0], role=ROLE, password_stdin=SEED, only_private_key=True
    )
    private_key = PrivateKey(value=result_private_key.stdout.strip())

    # ASSERT
    assert private_key.calculate_public_key() == public_key, (
        "Generated private key should match previously generated public key."
    )


SECRET_PHRASE_SEED: Final[str] = (
    "WHALING ZYGOMA AVERA FERRITE GRINNER KATYDID LITHELY SAMMEL RECHAR FLOSS ALIKE MUSH COPPLED STIGMAI MOIRE CLINAL"
)


# keys should remain unchanged and unique here regardless of any changes in clive
# because keys are derived from seed in deterministic way
@pytest.mark.parametrize(
    ("seed", "account_name", "role", "expected_public_key"),
    [
        ("", "alice", "owner", "STM5r64gbv5qPQtPQgJjmHqzEedPBKxaWvxg3jdNeGLirzjWC8Qgy"),
        ("", "alice", "active", "STM6HY4V7Eqa5MevEbYcGxgZASsDQTVBBJ9bpqUtgb32gWuuYFFHz"),
        ("", "alice", "posting", "STM4yj8TyGNJeP32iDmvrjVSWHFS6z6ANjYWD9zp9kp1eRJRGYvYb"),
        ("", "alice", "memo", "STM8hiq9fKuJhTdRt7HzbJEAxhYncXAWzVZWzzxhxCGKAV3uEB3n4"),
        ("", "mary", "owner", "STM5Ar8sUTfzCcS418TTyzJbBUn4yQjBjGMYSuwapCmJqXQwhWTS1"),
        ("", "mary", "active", "STM7AwXFBT8ehevpy9x9tNvTzFATxbQynTnhRB6udFyzF7DcYni9g"),
        ("other secret phrase", "alice", "active", "STM8VrgutWTUyqcmKGRSauXDKsS6wmnn4e7FCqQqXdtpE1DE3TqkK"),
        ("other secret phrase 2", "alice", "active", "STM7gq6Ho3GpbbVzkMoKvfw9MKGEoVZd11Qmo7T861mvo4oY7HD6A"),
        ("password", "someaccount", "owner", "STM5q3W9JUFHVvNZZnGdnsAcpbWwjVD9EE2HXQCgzfwnYkYtNzkpv"),
    ],
)
async def test_generate_key_from_seed_hardcoded(
    cli_tester_locked: CLITester, seed: str, account_name: str, role: str, expected_public_key: str
) -> None:
    """Check clive generate key-from-seed command for different seed, account_name and role."""
    # ACT
    seed_ = seed or SECRET_PHRASE_SEED
    result = cli_tester_locked.generate_key_from_seed(
        account_name=account_name, role=role, password_stdin=seed_, only_private_key=True
    )

    # ASSERT
    value = result.stdout.strip()
    actual_public_key = PrivateKey(value=value).calculate_public_key()
    assert actual_public_key == expected_public_key, (
        f"Actual public key `{actual_public_key}`)` doesn't match expected `{expected_public_key}`."
    )
