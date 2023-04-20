from __future__ import annotations

from typing import Final

from dunamai import Version


def __get_version() -> Version:
    try:
        return Version.from_git()
    except RuntimeError:
        from importlib.metadata import version

        return Version.parse(version("clive"))


VERSION: Final[Version] = __get_version()


def __get_commit_part() -> str:
    return f" ({VERSION.commit})" if VERSION.commit else ""


def __get_dirty_part() -> str:
    return " dirty!" if VERSION.dirty else ""


VERSION_INFO: Final[str] = f"{VERSION.base}{__get_commit_part()}{__get_dirty_part()}"
