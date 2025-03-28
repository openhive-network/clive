from __future__ import annotations

import importlib.resources as pkg_resources
import shutil
from typing import TYPE_CHECKING, Final

import clive_local_tools.storage_migration.prepared_data as prepared_profiles

if TYPE_CHECKING:
    from importlib.abc import Traversable
    from pathlib import Path


ALL_PROFILES: Final[tuple[str, ...]] = tuple(sorted(["one", "two", "three", "mary"]))


def copy_recursively(src: Traversable, dst: Path) -> None:
    """Recursively copy from MultiplexedPath to real directory."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_recursively(item, target)
        else:
            with pkg_resources.as_file(item) as file_path:
                shutil.copy(file_path, target)


def copy_prepared_profiles_data(destination_dir: Path) -> None:
    package_path = pkg_resources.files(prepared_profiles)
    copy_recursively(package_path, destination_dir)
