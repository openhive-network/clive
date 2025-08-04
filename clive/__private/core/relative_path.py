from __future__ import annotations

from pathlib import Path

from clive.exceptions import NotRelativePathError


def get_relative_path_to_root(whole_path: Path, root_path: Path) -> Path:
    """
    Return a path relative to a given root, prefixed with the root directory name.

    This function takes an `whole_path` and a `root_path`, then computes
    the relative path of `whole_path` with respect to `root_path`. The returned
    path always starts with the last component (`name`) of the `root_path`.

    Args:
        whole_path: The full path.
        root_path: The root path to compute the relative path from.

    Returns:
        The relative path starting with the root directory name.

    Example:
        >>> from pathlib import Path
        >>> get_relative_path_to_root(
        ...     whole_path=Path('/home/user/some/path'),
        ...     root_path=Path('/home/user')
        ... )
        Path('user/some/path')

        >>> get_relative_path_to_root(
        ...     whole_path=Path('/home/user'),
        ...     root_path=Path('/home/user')
        ... )
        Path('user')

    Raises:
        NotRelativePathError: If `whole_path` is not relative to `root_path`.
    """
    if whole_path == root_path:
        return Path(root_path.name)
    if not whole_path.is_relative_to(root_path):
        raise NotRelativePathError(whole_path, root_path)

    relative_path = whole_path.relative_to(root_path)
    return Path(root_path.name) / relative_path
