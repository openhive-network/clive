from __future__ import annotations

from pathlib import Path


def validate_path(value: str) -> bool:
    try:
        Path(value).resolve()
    except (OSError, RuntimeError):
        return False
    return True


def validate_path_exists(value: str) -> bool:
    return Path(value).exists()


def validate_path_is_file(value: str) -> bool:
    return Path(value).is_file()


def validate_path_is_directory(value: str) -> bool:
    return Path(value).is_dir()


def validate_is_file_or_directory(value: str) -> bool:
    return validate_path_is_file(value) or validate_path_is_directory(value)


def validate_can_be_file(value: str) -> bool:
    return not validate_path_is_directory(value)


def validate_can_be_directory(value: str) -> bool:
    return not validate_path_is_file(value)


def validate_is_file_or_can_be_file(value: str) -> bool:
    return validate_path_is_file(value) or validate_can_be_file(value)


def validate_is_directory_or_can_be_directory(value: str) -> bool:
    return validate_path_is_directory(value) or validate_can_be_directory(value)
