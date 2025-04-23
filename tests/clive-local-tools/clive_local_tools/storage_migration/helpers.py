from __future__ import annotations

import importlib.resources as pkg_resources
import shutil
from typing import TYPE_CHECKING, Final

from clive_local_tools.storage_migration import (
    prepared_data,
    with_alarms,
    with_operations,
    without_alarms_and_operations,
)

if TYPE_CHECKING:
    from importlib.abc import Traversable
    from pathlib import Path


BLANK_PROFILES: Final[tuple[str, ...]] = tuple(sorted(["one", "two", "three", "mary"]))


def _copy_recursively(src: Traversable, dst: Path) -> None:
    """Recursively copy from MultiplexedPath to real directory."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            _copy_recursively(item, target)
        elif item.name != "__init__.py":
            with pkg_resources.as_file(item) as file_path:
                shutil.copy(file_path, target)


def copy_blank_profile_files(destination_dir: Path) -> None:
    package_path = pkg_resources.files(prepared_data)
    _copy_recursively(package_path, destination_dir)


def copy_profile_with_alarms(destination_dir: Path) -> None:
    package_path = pkg_resources.files(with_alarms)
    _copy_recursively(package_path, destination_dir)


def copy_profile_with_operations(destination_dir: Path) -> None:
    package_path = pkg_resources.files(with_operations)
    _copy_recursively(package_path, destination_dir)


def copy_profile_without_alarms_and_operations(destination_dir: Path) -> None:
    package_path = pkg_resources.files(without_alarms_and_operations)
    _copy_recursively(package_path, destination_dir)
