from __future__ import annotations

import warnings
from contextlib import contextmanager
from typing import TYPE_CHECKING

import typer

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def typer_echo_warnings() -> Iterator[None]:
    """
    Context manager to catch warnings and print them using typer.secho.

    This function captures all warnings that occur within the context and prints them
    to the console in yellow color using `typer.secho`.

    Returns:
        Iterator[None]: A context manager that yields control to the block of code
            where warnings should be captured and printed.
    """
    with warnings.catch_warnings(record=True) as catched_warnings:
        yield

        for warning in catched_warnings:
            typer.secho(f"Warning:\n{warning.message}\n", fg=typer.colors.YELLOW)
