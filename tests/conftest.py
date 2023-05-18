from __future__ import annotations

import re
import shutil
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

import pytest

from clive.__private.config import settings
from clive.__private.core.beekeeper import BeekeeperLocal
from clive.__private.core.world import World
from clive.__private.storage.mock_database import PrivateKeyAlias
from clive.__private.util import prepare_before_launch
from tests import WalletInfo

if TYPE_CHECKING:
    from collections.abc import Iterator


def __convert_test_name_to_directory_name(test_name: str) -> str:
    max_dir_name: Final[int] = 64
    parametrized_test_match = re.match(r"([\w_]+)\[(.*)\]", test_name)
    if parametrized_test_match:
        test_name = f"{parametrized_test_match[1]}_with_parameters_{parametrized_test_match[2]}"
    final_test_name = ""

    for character in test_name:
        char = character
        if not (character.isalnum() or character in "-_"):
            char = f"-0x{ord(character):X}-"
        final_test_name += char

    return final_test_name[:max_dir_name]


@pytest.fixture(autouse=True, scope="function")
def run_prepare_before_launch(working_directory: Path) -> None:
    settings.data_path = working_directory
    settings.log_path = working_directory / "logs"
    prepare_before_launch()


@pytest.fixture
def working_directory(request: pytest.FixtureRequest) -> Path:
    test_location = request.path.parent
    test_module_name = Path(request.module.__file__).stem
    final_path = (
        test_location / "generated" / test_module_name / __convert_test_name_to_directory_name(request.node.name)
    )

    if final_path.exists():
        warnings.warn("Test directory already exists, removing...", stacklevel=1)
        shutil.rmtree(final_path)  # delete non-empty directory

    final_path.mkdir(parents=True)
    return final_path


@pytest.fixture
def wallet_name() -> str:
    return "wallet"


@pytest.fixture
def pubkey(beekeeper: BeekeeperLocal, wallet: WalletInfo) -> PrivateKeyAlias:
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
def beekeeper(world: World) -> BeekeeperLocal:
    return cast(BeekeeperLocal, world.beekeeper)
