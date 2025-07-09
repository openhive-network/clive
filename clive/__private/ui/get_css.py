from __future__ import annotations

from pathlib import Path


def get_relative_css_path(file_path: str | Path, *, name: str = "") -> Path:
    """
    Get the relative path to the css file.

    Args:
        file_path: The path to the file next to which the css file is located.
        name: Explicit name of the css file.

    Example:
    -------
    >>> get_relative_css_path("some_parent/some_file.py")
    Path('some_parent/some_file.scss')

    >>> get_relative_css_path("some_parent/some_file.py", name="some_name")
    Path('some_parent/some_name.scss')

    Returns:
        The relative path to the css file.
    """
    file_stem = name if name else Path(file_path).stem
    css_file_name = f"{file_stem}.scss"
    return Path(file_path).parent / css_file_name


def get_css_from_relative_path(file_path: str | Path, *, name: str = "") -> str:
    """Get the css from file. For more info check `get_relative_css_path`."""
    return get_relative_css_path(file_path, name=name).read_text()
