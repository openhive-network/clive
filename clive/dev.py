from __future__ import annotations

from textual.cli.cli import run_app


def main() -> None:
    from clive.__private.util import prepare_before_launch

    prepare_before_launch()
    run_app(["--dev", "clive.__private.ui.app:clive_app"])


if __name__ == "__main__":
    main()
