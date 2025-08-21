from __future__ import annotations

from pathlib import Path

from clive.exceptions import CliveError


class NotRelativePathError(CliveError):
    """
    Raised when a path is not relative to the expected root path.

    Args:
        whole_path: The full path that is expected to be relative.
        root_path: The root path against which the relative check is made.
    """

    def __init__(self, whole_path: str | Path, root_path: str | Path) -> None:
        message = f"The whole_path {whole_path} is not relative to the root_path {root_path}."
        super().__init__(message)


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


def get_relative_or_whole_path(whole_path: Path, root_path: Path) -> Path:
    """
    Return a path relative to a given root if possible; otherwise return the whole path.

    For more details, look into `get_relative_path_to_root`.

    Args:
        whole_path: The full path.
        root_path: The root path to compute the relative path from.

    Examples:
        >>> get_relative_or_whole_path(
        ...     whole_path=Path('/home/user/some/path'),
        ...     root_path=Path('/home/user')
        ... )
        Path('user/some/path')
        >>> get_relative_or_whole_path(
        ...     whole_path=Path('/etc/config'),
        ...     root_path=Path('/home/user')
        ... )
        Path('/etc/config')
        >>> get_relative_or_whole_path(
        ...     whole_path=Path('/home/user'),
        ...     root_path=Path('/home/user')
        ... )
        Path('user')

    Returns:
        The relative path if possible, otherwise the whole path.
    """
    try:
        return get_relative_path_to_root(whole_path, root_path)
    except NotRelativePathError:
        return whole_path
