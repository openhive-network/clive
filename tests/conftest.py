from __future__ import annotations

import re
import shutil
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

import pytest

from clive.__private.config import settings
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.world import World
from clive.__private.storage.mock_database import PrivateKeyAlias
from tests import WalletInfo

if TYPE_CHECKING:
    from collections.abc import Iterator


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


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--beekeeper", default="/workspace/clive/clive/beekeeper", help="path to beekeeper executable")


@pytest.fixture
def beekeeper_executable_path(request: pytest.FixtureRequest) -> Path:
    return Path(request.config.getoption("--beekeeper"))


@pytest.fixture
def wallet_name() -> str:
    return "wallet"


@pytest.fixture
def pubkey(beekeeper: Beekeeper, wallet: WalletInfo) -> PrivateKeyAlias:
    return PrivateKeyAlias(beekeeper.api.create_key(wallet_name=wallet.name).public_key)


@pytest.fixture
def world(wallet_name: str, working_directory: Path, beekeeper_executable_path: Path) -> Iterator[World]:
    settings.beekeeper = {"path": beekeeper_executable_path}
    settings.data_path = working_directory
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
