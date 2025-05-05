from __future__ import annotations

import shutil
from pathlib import Path
from typing import Final

from clive_local_tools.storage_migration import (
    blank_profile_files,
    with_alarms,
    with_operations,
    without_alarms_and_operations,
)

BLANK_PROFILES: Final[tuple[str, ...]] = (
    "versioned_older_and_newer_profile",
    "versioned_profile",
    "versioned_profile_and_older_backup",
    "legacy_profile",
)


def _copy_recursively(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.pyc", "__pycache__", "__init__.py"))


def copy_blank_profile_files(destination_dir: Path) -> None:
    package_path = Path(blank_profile_files.__file__).parent
    _copy_recursively(package_path, destination_dir)


def copy_profile_with_alarms(destination_dir: Path) -> None:
    package_path = Path(with_alarms.__file__).parent
    _copy_recursively(package_path, destination_dir)


def copy_profile_with_operations(destination_dir: Path) -> None:
    package_path = Path(with_operations.__file__).parent
    _copy_recursively(package_path, destination_dir)


def copy_profile_without_alarms_and_operations(destination_dir: Path) -> None:
    package_path = Path(without_alarms_and_operations.__file__).parent
    _copy_recursively(package_path, destination_dir)
