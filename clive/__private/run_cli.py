from __future__ import annotations


def run_cli() -> None:
    from clive.__private.cli import cli
    from clive.__private.util import prepare_before_launch

    prepare_before_launch()
    cli()
