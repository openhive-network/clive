from __future__ import annotations

from typing import Final
from unittest.mock import MagicMock

import pytest

from clive.__private.core.commands.data_retrieval.update_node_data.clive_authority_data_provider import (
    CliveAuthorityDataProvider,
)
from clive.__private.models.schemas import Account
from schemas.fields.compound import Authority

ACCOUNT_NAME: Final[str] = "alice"
MEMO_KEY: Final[str] = "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCqTk"
KEY_A: Final[str] = "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCqTk"
KEY_B: Final[str] = "STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQa"
LAST_OWNER_UPDATE: Final[str] = "2024-01-15T10:30:00"
PREVIOUS_OWNER_UPDATE: Final[str] = "2023-06-20T08:00:00"
DEFAULT_AUTHORITY = Authority(weight_threshold=1, account_auths=[], key_auths=[(KEY_A, 1)])


def _create_mock_account(
    *,
    owner: Authority = DEFAULT_AUTHORITY,
    active: Authority = DEFAULT_AUTHORITY,
    posting: Authority = DEFAULT_AUTHORITY,
) -> Account:
    mock = MagicMock(spec=Account)
    mock.name = ACCOUNT_NAME
    mock.owner = owner
    mock.active = active
    mock.posting = posting
    mock.memo_key = MEMO_KEY
    mock.last_owner_update = LAST_OWNER_UPDATE
    mock.previous_owner_update = PREVIOUS_OWNER_UPDATE
    return mock


async def test_basic_authority_conversion() -> None:
    """Test that account authority data is correctly converted to wax format."""
    # ARRANGE
    account = _create_mock_account()
    provider = CliveAuthorityDataProvider(account)

    # ACT
    result = await provider.get_hive_authority_data(ACCOUNT_NAME)

    # ASSERT
    assert result.account == ACCOUNT_NAME
    assert result.memo_key == MEMO_KEY
    assert result.authorities.owner is not None
    assert result.authorities.active is not None
    assert result.authorities.posting is not None
    assert result.authorities.owner.weight_threshold == 1
    assert result.authorities.active.weight_threshold == 1
    assert result.authorities.posting.weight_threshold == 1


MULTISIG_WEIGHT_THRESHOLD: Final[int] = 2
OWNER_WEIGHT_THRESHOLD: Final[int] = 3
EXPECTED_OWNER_KEY_COUNT: Final[int] = 2
KEY_A_WEIGHT_IN_OWNER: Final[int] = 2


async def test_key_auths_conversion() -> None:
    """Test that key_auths are properly converted from list of tuples to mapping."""
    # ARRANGE
    owner = Authority(weight_threshold=MULTISIG_WEIGHT_THRESHOLD, account_auths=[], key_auths=[(KEY_A, 1), (KEY_B, 1)])
    account = _create_mock_account(owner=owner)
    provider = CliveAuthorityDataProvider(account)

    # ACT
    result = await provider.get_hive_authority_data(ACCOUNT_NAME)

    # ASSERT
    assert result.authorities.owner is not None
    owner_key_auths = dict(result.authorities.owner.key_auths)
    assert owner_key_auths == {KEY_A: 1, KEY_B: 1}
    assert result.authorities.owner.weight_threshold == MULTISIG_WEIGHT_THRESHOLD


async def test_account_auths_conversion() -> None:
    """Test that account_auths are properly converted from list of tuples to mapping."""
    # ARRANGE
    posting = Authority(weight_threshold=1, account_auths=[("bob", 1), ("charlie", 2)], key_auths=[(KEY_A, 1)])
    account = _create_mock_account(posting=posting)
    provider = CliveAuthorityDataProvider(account)

    # ACT
    result = await provider.get_hive_authority_data(ACCOUNT_NAME)

    # ASSERT
    assert result.authorities.posting is not None
    posting_account_auths = dict(result.authorities.posting.account_auths)
    assert posting_account_auths == {"bob": 1, "charlie": 2}


async def test_different_authorities_per_role() -> None:
    """Test that owner, active, and posting authorities can have different configurations."""
    # ARRANGE
    owner = Authority(
        weight_threshold=OWNER_WEIGHT_THRESHOLD,
        account_auths=[],
        key_auths=[(KEY_A, KEY_A_WEIGHT_IN_OWNER), (KEY_B, 1)],
    )
    active = Authority(weight_threshold=1, account_auths=[("delegatee", 1)], key_auths=[(KEY_A, 1)])
    posting = Authority(weight_threshold=1, account_auths=[], key_auths=[(KEY_B, 1)])
    account = _create_mock_account(owner=owner, active=active, posting=posting)
    provider = CliveAuthorityDataProvider(account)

    # ACT
    result = await provider.get_hive_authority_data(ACCOUNT_NAME)

    # ASSERT
    assert result.authorities.owner is not None
    assert result.authorities.active is not None
    assert result.authorities.posting is not None
    assert result.authorities.owner.weight_threshold == OWNER_WEIGHT_THRESHOLD
    assert len(result.authorities.owner.key_auths) == EXPECTED_OWNER_KEY_COUNT

    assert result.authorities.active.weight_threshold == 1
    assert dict(result.authorities.active.account_auths) == {"delegatee": 1}

    assert result.authorities.posting.weight_threshold == 1
    assert dict(result.authorities.posting.key_auths) == {KEY_B: 1}


async def test_empty_auths() -> None:
    """Test conversion when account_auths and key_auths are empty."""
    # ARRANGE
    empty_auth = Authority(weight_threshold=1, account_auths=[], key_auths=[])
    account = _create_mock_account(owner=empty_auth, active=empty_auth, posting=empty_auth)
    provider = CliveAuthorityDataProvider(account)

    # ACT
    result = await provider.get_hive_authority_data(ACCOUNT_NAME)

    # ASSERT
    assert result.authorities.owner is not None
    assert result.authorities.active is not None
    assert result.authorities.posting is not None
    assert len(result.authorities.owner.key_auths) == 0
    assert len(result.authorities.owner.account_auths) == 0
    assert len(result.authorities.active.key_auths) == 0
    assert len(result.authorities.posting.key_auths) == 0


async def test_timestamps_conversion() -> None:
    """Test that last_owner_update and previous_owner_update are preserved."""
    # ARRANGE
    account = _create_mock_account()
    provider = CliveAuthorityDataProvider(account)

    # ACT
    result = await provider.get_hive_authority_data(ACCOUNT_NAME)

    # ASSERT
    assert LAST_OWNER_UPDATE.replace("T", " ") in str(result.last_owner_update)
    assert PREVIOUS_OWNER_UPDATE.replace("T", " ") in str(result.previous_owner_update)


async def test_wrong_account_name_raises_assertion() -> None:
    """Test that querying for wrong account name raises AssertionError."""
    # ARRANGE
    account = _create_mock_account()
    provider = CliveAuthorityDataProvider(account)

    # ACT & ASSERT
    with pytest.raises(AssertionError, match="wrong account"):
        await provider.get_hive_authority_data("bob")


async def test_duplicate_key_auths_raises_assertion() -> None:
    """Test that duplicate keys in key_auths trigger an assertion."""
    # ARRANGE
    owner = Authority(weight_threshold=1, account_auths=[], key_auths=[(KEY_A, 1), (KEY_A, 2)])
    account = _create_mock_account(owner=owner)
    provider = CliveAuthorityDataProvider(account)

    # ACT & ASSERT
    with pytest.raises(AssertionError, match="Duplicate key"):
        await provider.get_hive_authority_data(ACCOUNT_NAME)


async def test_duplicate_account_auths_raises_assertion() -> None:
    """Test that duplicate account names in account_auths trigger an assertion."""
    # ARRANGE
    posting = Authority(weight_threshold=1, account_auths=[("bob", 1), ("bob", 2)], key_auths=[(KEY_A, 1)])
    account = _create_mock_account(posting=posting)
    provider = CliveAuthorityDataProvider(account)

    # ACT & ASSERT
    with pytest.raises(AssertionError, match="Duplicate key"):
        await provider.get_hive_authority_data(ACCOUNT_NAME)
