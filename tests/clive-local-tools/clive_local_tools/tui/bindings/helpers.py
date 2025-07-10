from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from clive.__private.settings import safe_settings

DEFAULT_BINDINGS_FILE_PATH: Final[Path] = Path(__file__).parent / "default_bindings.toml"


def _copy_prepared_bindings(src: Path) -> Path:
    dst_file_name = "test_" + src.name
    dst = safe_settings.data_path / dst_file_name
    shutil.copyfile(src, dst)
    return dst


def copy_custom_bindings() -> Path:
    return _copy_prepared_bindings(Path(__file__).parent / "custom_bindings.toml")


def copy_empty_bindings() -> Path:
    return _copy_prepared_bindings(Path(__file__).parent / "empty_bindings.toml")


def copy_default_bindings() -> Path:
    return _copy_prepared_bindings(DEFAULT_BINDINGS_FILE_PATH)
