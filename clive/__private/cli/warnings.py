from __future__ import annotations

import warnings
from contextlib import contextmanager
from typing import TYPE_CHECKING

from clive.__private.cli.print_cli import print_warning

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def typer_echo_warnings(category: type[Warning] | None = None, new_message: str | Warning = "") -> Iterator[None]:
    if category is None and new_message:
        raise AssertionError("'new_message' shouldn't be used without category")

    with warnings.catch_warnings(record=True) as catched_warnings:
        yield

        for warning in catched_warnings:
            if category is None:
                print_warning(str(warning.message))
                continue

            if issubclass(warning.category, category):
                print_warning(str(new_message) if new_message else str(warning.message))
            else:
                warnings.warn_explicit(
                    warning.message, warning.category, warning.filename, warning.lineno, warning.source
                )
