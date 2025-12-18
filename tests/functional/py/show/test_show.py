from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.py import ClivePy
from clive_local_tools.testnet_block_log import WATCHED_ACCOUNTS_NAMES, WORKING_ACCOUNT_DATA, WORKING_ACCOUNT_NAME

if TYPE_CHECKING:
    from clive.__private.py.base import UnlockedClivePy


class TestShowProfiles:
    @pytest.mark.usefixtures("_prepare_profile_and_setup_wallet")
    async def test_show_profiles_returns_list(self) -> None:
        """Test that show.profiles() returns a list of profile names."""
        async with ClivePy() as clive:
            profiles = await clive.show.profiles()

        assert WORKING_ACCOUNT_NAME in profiles


class TestShowBalances:
    async def test_show_balances_returns_balances_object(
        self,
        unlocked_clive_py: UnlockedClivePy,
    ) -> None:
        """Test that show.balances() returns Balances dataclass."""
        balances = await unlocked_clive_py.show.balances(WORKING_ACCOUNT_NAME)

        # Verify balances match expected values from WORKING_ACCOUNT_DATA
        assert balances.hive_liquid.amount == WORKING_ACCOUNT_DATA.hives_liquid.amount
        assert balances.hbd_liquid.amount == WORKING_ACCOUNT_DATA.hbds_liquid.amount
        assert balances.hive_savings.amount == WORKING_ACCOUNT_DATA.hives_savings.amount
        # HBD savings has withdrawal in progress (200 - 10 = 190)
        expected_hbd_savings = (
            WORKING_ACCOUNT_DATA.hbds_savings.amount - WORKING_ACCOUNT_DATA.hbds_savings_withdrawal.amount
        )
        assert balances.hbd_savings.amount == expected_hbd_savings


class TestShowAccounts:
    async def test_show_accounts_returns_accounts_object(self, unlocked_clive_py: UnlockedClivePy) -> None:
        """Test that show.accounts() returns Accounts dataclass."""
        accounts = await unlocked_clive_py.show.accounts()

        assert accounts.working_account == WORKING_ACCOUNT_NAME
        # Tracked accounts = working account + watched accounts
        assert WORKING_ACCOUNT_NAME in accounts.tracked_accounts
        for watched in WATCHED_ACCOUNTS_NAMES:
            assert watched in accounts.tracked_accounts


class TestShowWitnesses:
    async def test_show_witnesses_returns_witnesses_result(
        self,
        unlocked_clive_py: UnlockedClivePy,
    ) -> None:
        """Test that show.witnesses() returns WitnessesResult with metadata."""
        result = await unlocked_clive_py.show.witnesses(WORKING_ACCOUNT_NAME, page_size=10, page_no=0)

        assert result.witnesses


class TestShowAuthority:
    async def test_show_owner_authority_returns_authority_info(
        self,
        unlocked_clive_py: UnlockedClivePy,
    ) -> None:
        """Test that show.owner_authority() returns AuthorityInfo dataclass."""
        authority = await unlocked_clive_py.show.owner_authority(WORKING_ACCOUNT_NAME)

        assert authority.authority_type == "owner"
        # Verify working account's public key is in the authority
        account_key = WORKING_ACCOUNT_DATA.account.public_key
        assert any(auth.account_or_public_key == account_key for auth in authority.authorities)

    async def test_show_active_authority_returns_authority_info(
        self,
        unlocked_clive_py: UnlockedClivePy,
    ) -> None:
        """Test that show.active_authority() returns AuthorityInfo dataclass."""
        authority = await unlocked_clive_py.show.active_authority(WORKING_ACCOUNT_NAME)

        assert authority.authority_type == "active"
        # Verify working account's public key is in the authority
        account_key = WORKING_ACCOUNT_DATA.account.public_key
        assert any(auth.account_or_public_key == account_key for auth in authority.authorities)

    async def test_show_posting_authority_returns_authority_info(
        self,
        unlocked_clive_py: UnlockedClivePy,
    ) -> None:
        """Test that show.posting_authority() returns AuthorityInfo dataclass."""
        authority = await unlocked_clive_py.show.posting_authority(WORKING_ACCOUNT_NAME)

        assert authority.authority_type == "posting"
        # Verify working account's public key is in the authority
        account_key = WORKING_ACCOUNT_DATA.account.public_key
        assert any(auth.account_or_public_key == account_key for auth in authority.authorities)


class TestProcessStubbed:
    async def test_process_raises_not_implemented(self, unlocked_clive_py: UnlockedClivePy) -> None:
        """Test that process property raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            _ = unlocked_clive_py.process

        assert "not yet available" in str(exc_info.value)
