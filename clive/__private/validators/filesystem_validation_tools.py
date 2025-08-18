from __future__ import annotations

from pathlib import Path

from pathvalidate import is_valid_filename


def validate_path(path: str | Path) -> bool:
    try:
        Path(path).resolve()
    except (OSError, RuntimeError):
        return False
    return True


def validate_path_exists(path: str | Path) -> bool:
    return Path(path).exists()


def validate_path_is_file(path: str | Path) -> bool:
    return Path(path).is_file()


def validate_path_is_directory(path: str | Path) -> bool:
    return Path(path).is_dir()


def validate_is_file_or_directory(path: str | Path) -> bool:
    return validate_path_is_file(path) or validate_path_is_directory(path)


def validate_can_be_file(path: str | Path) -> bool:
    return not validate_path_is_directory(path)


def validate_can_be_directory(path: str | Path) -> bool:
    return not validate_path_is_file(path)


def validate_is_file_or_can_be_file(path: str | Path) -> bool:
    return validate_path_is_file(path) or validate_can_be_file(path)


def validate_is_directory_or_can_be_directory(path: str | Path) -> bool:
    return validate_path_is_directory(path) or validate_can_be_directory(path)


def validate_filename(value: str | Path) -> bool:
    """
    Validate if the given value has a valid filename.

    If value is a string, it is used as the filename.
    If value is a Path, its name is used as the filename.
    Beware of passing filename as a Path object as it could lead to
    false positive  because `Path("dir/name")` will validate only the `name` part of the path.

    Args:
        value: The filename or path to validate.

    Returns:
        True if the filename is valid, False otherwise.
    """
    filename = value if isinstance(value, str) else value.name
    return is_valid_filename(filename)
