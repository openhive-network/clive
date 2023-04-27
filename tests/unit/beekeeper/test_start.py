from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper


def test_proper_closing(beekeeper: Beekeeper) -> None:
    # ARRANGE, ACT & ASSERT
    assert beekeeper is not None  # dummy assertion


@pytest.mark.random_fail  # can't diagnose, potentially segmentation fault, but can't be sure
@pytest.mark.parametrize("wallet_name", ("test", "123", "test"))
def test_clean_dirs(beekeeper: Beekeeper, wallet_name: str) -> None:
    test_file = beekeeper.config.wallet_dir / wallet_name
    assert not test_file.exists()
    test_file.touch()
