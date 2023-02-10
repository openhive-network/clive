from __future__ import annotations


def run_tui() -> None:
    from clive.ui.get_clive import get_clive
    from clive.util import prepare_before_launch

    prepare_before_launch()
    get_clive().run()
