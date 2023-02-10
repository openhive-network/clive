from __future__ import annotations


def run_cli() -> None:
    from clive.cli import cli
    from clive.util import prepare_before_launch

    prepare_before_launch()
    cli()
