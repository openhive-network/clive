from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

from clive.__private.core.constants.setting_identifiers import NODE_CHAIN_ID
from clive.__private.core.profile import InvalidChainIdError, Profile
from clive.__private.models import Asset, Transaction
from clive.__private.models.schemas import TransferOperation
from clive.__private.settings import safe_settings, settings
from clive_local_tools.data.constants import TESTNET_CHAIN_ID

if TYPE_CHECKING:
    from collections.abc import Iterator

    import test_tools as tt

    from clive import World
    from clive_local_tools.data.models import WalletInfo

DEFAULT_CHAIN_ID: Final[str] = "0" * 64


@pytest.fixture
def profile_with_default_chain_id_from_settings() -> Iterator[Profile]:
    chain_id_identifier = NODE_CHAIN_ID
    chain_id_before = safe_settings.node.chain_id
    settings.set(chain_id_identifier, DEFAULT_CHAIN_ID)
    yield Profile.create(name="test")
    settings.set(chain_id_identifier, chain_id_before)


def test_default_profile_chain_id_is_set_from_settings(
    profile_with_default_chain_id_from_settings: Profile,
) -> None:
    # ARRANGE
    profile = profile_with_default_chain_id_from_settings

    # ACT
    chain_id = profile.chain_id

    # ASSERT
    assert chain_id == DEFAULT_CHAIN_ID


def test_default_chain_id_is_overridden_with_explicitly_set(
    profile_with_default_chain_id_from_settings: Profile,
) -> None:
    # ARRANGE
    expected_chain_id = "1" * 64
    profile = profile_with_default_chain_id_from_settings

    # ACT
    profile.set_chain_id(expected_chain_id)

    # ASSERT
    assert profile.chain_id == expected_chain_id


def test_default_chain_id_could_be_unset(profile_with_default_chain_id_from_settings: Profile) -> None:
    # ARRANGE
    profile = profile_with_default_chain_id_from_settings

    # ACT
    profile.unset_chain_id()

    # ASSERT
    assert profile.chain_id is None


def test_setting_wrong_chain_id_raises_exception(profile_with_default_chain_id_from_settings: Profile) -> None:
    # ARRANGE
    profile = profile_with_default_chain_id_from_settings

    # ACT & ASSERT
    with pytest.raises(InvalidChainIdError):
        profile.set_chain_id("wrong_chain_id")

    assert profile.chain_id == DEFAULT_CHAIN_ID


async def test_chain_id_is_retrieved_from_api_if_not_set(
    world: World,
    wallet: WalletInfo,
    init_node: tt.InitNode,  # noqa: ARG001
) -> None:
    # ARRANGE
    # any transaction so we could sign it, and hope that chain id will be retrieved from the node api
    await world.set_wallet(next(w for w in await world.session.wallets_unlocked if w.name == wallet.name))
    transaction = Transaction(
        operations=[
            TransferOperation(from_="doesnt-matter", to="null", amount=Asset.hive(1), memo=""),
        ]
    )

    profile = world.profile
    profile.unset_chain_id()

    # unsetting because autouse fixture sets it to default value in other tests
    assert profile.chain_id is None, "chain id should be None if not set"

    # ACT
    # chain id should be retrieved from api when needed for the first time and set in profile
    await world.commands.sign(transaction=transaction, sign_with=wallet.public_key)

    # ASSERT
    assert profile.chain_id == TESTNET_CHAIN_ID
