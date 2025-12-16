from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from clive.__private.py.base import PyWorld, UnlockedClivePy
from clive.__private.py.data_classes import Accounts, AuthorityInfo, Balances, Witness, WitnessesResult
from clive.py import ClivePy

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from clive.__private.core.world import World


@pytest.fixture
async def py_world(
    world_with_remote_beekeeper: World, _prepare_profile_and_setup_wallet: None
) -> AsyncGenerator[PyWorld]:
    """Create PyWorld that uses the test beekeeper.

    Note: We must read settings from world_with_remote_beekeeper using the settings property
    (not direct attribute access) because the fixture yields an already-setup world.
    """
    py_world = PyWorld()
    # Set beekeeper settings before entering context manager (before setup)
    # Read from the already-setup world using settings property
    py_world.beekeeper_manager.settings.http_endpoint = (
        world_with_remote_beekeeper.beekeeper_manager.beekeeper.settings.http_endpoint
    )
    py_world.beekeeper_manager.settings.use_existing_session = (
        world_with_remote_beekeeper.beekeeper_manager.beekeeper.settings.use_existing_session
    )
    async with py_world:
        yield py_world


class TestShowProfiles:
    async def test_show_profiles_returns_list(self) -> None:
        """Test that show.profiles() returns a list of profile names."""
        async with ClivePy() as clive:
            profiles = await clive.show.profiles()

        assert isinstance(profiles, list)


class TestShowBalances:
    async def test_show_balances_returns_balances_object(
        self,
        py_world: PyWorld,
        node: None,  # noqa: ARG002
    ) -> None:
        """Test that show.balances() returns Balances dataclass."""
        py = UnlockedClivePy()
        py._world = py_world
        py._is_setup_called = True

        balances = await py.show.balances("alice")

        assert isinstance(balances, Balances)
        assert hasattr(balances, "hbd_liquid")
        assert hasattr(balances, "hive_liquid")
        assert hasattr(balances, "hbd_savings")
        assert hasattr(balances, "hive_savings")


class TestShowAccounts:
    async def test_show_accounts_returns_accounts_object(self, py_world: PyWorld) -> None:
        """Test that show.accounts() returns Accounts dataclass."""
        py = UnlockedClivePy()
        py._world = py_world
        py._is_setup_called = True

        accounts = await py.show.accounts()

        assert isinstance(accounts, Accounts)
        assert hasattr(accounts, "working_account")
        assert hasattr(accounts, "tracked_accounts")
        assert hasattr(accounts, "known_accounts")
        assert isinstance(accounts.tracked_accounts, list)
        assert isinstance(accounts.known_accounts, list)


class TestShowWitnesses:
    async def test_show_witnesses_returns_witnesses_result(
        self,
        py_world: PyWorld,
        node: None,  # noqa: ARG002
    ) -> None:
        """Test that show.witnesses() returns WitnessesResult with metadata."""
        py = UnlockedClivePy()
        py._world = py_world
        py._is_setup_called = True

        result = await py.show.witnesses("alice", page_size=10, page_no=0)

        assert isinstance(result, WitnessesResult)
        assert hasattr(result, "witnesses")
        assert hasattr(result, "total_count")
        assert hasattr(result, "proxy")
        assert isinstance(result.witnesses, list)
        assert isinstance(result.total_count, int)
        if len(result.witnesses) > 0:
            assert isinstance(result.witnesses[0], Witness)
            assert hasattr(result.witnesses[0], "witness_name")
            assert hasattr(result.witnesses[0], "votes")
            assert hasattr(result.witnesses[0], "voted")


class TestShowAuthority:
    async def test_show_owner_authority_returns_authority_info(
        self,
        py_world: PyWorld,
        node: None,  # noqa: ARG002
    ) -> None:
        """Test that show.owner_authority() returns AuthorityInfo dataclass."""
        py = UnlockedClivePy()
        py._world = py_world
        py._is_setup_called = True

        authority = await py.show.owner_authority("alice")

        assert isinstance(authority, AuthorityInfo)
        assert authority.authority_type == "owner"
        assert hasattr(authority, "weight_threshold")
        assert hasattr(authority, "authorities")

    async def test_show_active_authority_returns_authority_info(
        self,
        py_world: PyWorld,
        node: None,  # noqa: ARG002
    ) -> None:
        """Test that show.active_authority() returns AuthorityInfo dataclass."""
        py = UnlockedClivePy()
        py._world = py_world
        py._is_setup_called = True

        authority = await py.show.active_authority("alice")

        assert isinstance(authority, AuthorityInfo)
        assert authority.authority_type == "active"

    async def test_show_posting_authority_returns_authority_info(
        self,
        py_world: PyWorld,
        node: None,  # noqa: ARG002
    ) -> None:
        """Test that show.posting_authority() returns AuthorityInfo dataclass."""
        py = UnlockedClivePy()
        py._world = py_world
        py._is_setup_called = True

        authority = await py.show.posting_authority("alice")

        assert isinstance(authority, AuthorityInfo)
        assert authority.authority_type == "posting"


class TestProcessStubbed:
    async def test_process_raises_not_implemented(self) -> None:
        """Test that process property raises NotImplementedError."""
        py = UnlockedClivePy()
        py._is_setup_called = True

        with pytest.raises(NotImplementedError) as exc_info:
            _ = py.process

        assert "not yet available" in str(exc_info.value)
