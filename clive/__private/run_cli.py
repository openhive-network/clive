from __future__ import annotations


def run_cli() -> None:
    from clive.__private.cli import cli
    from clive.__private.util import prepare_before_launch, spawn_thread_pool

    with spawn_thread_pool() as executor:
        prepare_before_launch(executor=executor, enable_textual_logger=False)
        cli()
