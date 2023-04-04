from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import clive.__private.config as config  # noqa: PLR0402
from clive.__private.storage.mock_database import ProfileData

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(autouse=True)
def mock_data_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "DATA_DIRECTORY", tmp_path)
    monkeypatch.setattr(ProfileData, "_STORAGE_FILE_PATH", tmp_path)
