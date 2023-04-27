from __future__ import annotations

import re
import shutil
import warnings
from typing import TYPE_CHECKING, Final, cast

import pytest

from clive.__private.config import settings
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.world import World
from clive.__private.storage.mock_database import PrivateKeyAlias
from clive.__private.util import prepare_before_launch
from tests import WalletInfo

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    fixture_name: Final[str] = f"random_fail_fixture_{hash(metafunc)}"
    random_fail_fixture_name: Final[str] = "random_fail"
    amount_of_retries: Final[int] = 10

    for marker in metafunc.definition.own_markers:
        if random_fail_fixture_name == marker.name:
            metafunc.fixturenames.append(fixture_name)
            metafunc.parametrize(fixture_name, range(amount_of_retries))


def __convert_test_name_to_directory_name(test_name: str) -> str:
    parametrized_test_match = re.match(r"([\w_]+)\[(.*)\]", test_name)
    if parametrized_test_match:
        test_name = f"{parametrized_test_match[1]}_with_parameters_{parametrized_test_match[2]}"
    final_test_name = ""

    for character in test_name:
        char = character
        if not (character.isalnum() or character in "-_"):
            char = f"-0x{ord(character):X}-"
        final_test_name += char

    return final_test_name


@pytest.fixture(autouse=True, scope="function")
def run_prepare_before_launch(working_directory: Path) -> None:
    settings.data_path = working_directory
    settings.log_path = working_directory / "logs"
    prepare_before_launch()


@pytest.fixture
def working_directory(request: pytest.FixtureRequest) -> Path:
    test_signature: Final[str] = __convert_test_name_to_directory_name(request.node.name)
    test_path_directory: Final[Path] = request.path.parent

    generated_directory = test_path_directory / "generated"
    generated_directory.mkdir(exist_ok=True)

    test_path = generated_directory / test_signature
    if test_path.exists():
        warnings.warn("removing datadir", stacklevel=1)
        shutil.rmtree(test_path)
    test_path.mkdir()
    return test_path


@pytest.fixture
def wallet_name() -> str:
    return "wallet"


@pytest.fixture
def pubkey(beekeeper: Beekeeper, wallet: WalletInfo) -> PrivateKeyAlias:
    return PrivateKeyAlias(beekeeper.api.create_key(wallet_name=wallet.name).public_key)


@pytest.fixture
def world(wallet_name: str) -> Iterator[World]:
    w = World(profile_name=wallet_name)
    yield w
    w.close()


@pytest.fixture
def wallet(world: World, wallet_name: str) -> WalletInfo:
    return WalletInfo(
        password=world.beekeeper.api.create(wallet_name=wallet_name).password,
        name=wallet_name,
    )


@pytest.fixture
def beekeeper(world: World) -> Beekeeper:
    return cast(Beekeeper, world.beekeeper)
