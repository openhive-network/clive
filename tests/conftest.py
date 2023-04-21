from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

from clive.__private import config
from clive.__private.core.beekeeper import Beekeeper
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.mock_database import PrivateKeyAlias
from tests import WalletInfo

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def mock_data_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "DATA_DIRECTORY", tmp_path)
    monkeypatch.setattr(ProfileData, "_STORAGE_FILE_PATH", tmp_path)


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
        shutil.rmtree(test_path)
    test_path.mkdir()
    return test_path


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--beekeeper", default="/workspace/clive/clive/beekeeper", help="path to beekeeper executable")


@pytest.fixture
def beekeeper_executable_path(request: pytest.FixtureRequest) -> Path:
    return Path(request.config.getoption("--beekeeper"))


@pytest.fixture
def beekeeper(working_directory: Path, beekeeper_executable_path: Path) -> Iterator[Beekeeper]:
    keeper = Beekeeper(executable=beekeeper_executable_path)
    keeper.config.wallet_dir = working_directory
    keeper.run()
    yield keeper
    keeper.close()


@pytest.fixture
def wallet_name() -> str:
    return "wallet"


@pytest.fixture
def wallet(beekeeper: Beekeeper, wallet_name: str) -> WalletInfo:
    return WalletInfo(
        password=beekeeper.api.create(wallet_name=wallet_name).password,
        name=wallet_name,
        pub=PrivateKeyAlias(key_name=beekeeper.api.get_public_keys().keys[0])
    )
