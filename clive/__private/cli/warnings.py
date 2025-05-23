from __future__ import annotations

import warnings
from contextlib import contextmanager
from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def typer_echo_warnings() -> Iterator[None]:
    with warnings.catch_warnings(record=True) as catched_warnings:
        yield

        for warning in catched_warnings:
            typer.secho(f"Warning:\n{warning.message}\n", fg=typer.colors.YELLOW)
