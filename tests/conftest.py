from __future__ import annotations

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


@pytest.fixture
def working_directory(request: pytest.FixtureRequest) -> Path:
    test_hash = abs(hash(request.node.name))
    test_signature: Final[str] = (
        request.node.name.translate({ord(char): ord("_") for char in list("[]; {}<>!@#$%^&*-/*-+,./?:;'\"~`")}).strip(
            "_"
        )
        + "_"
        + str(test_hash)[:8]
    )
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
