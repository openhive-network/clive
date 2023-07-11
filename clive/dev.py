from __future__ import annotations

from textual.cli.cli import run_app


def main() -> None:
    from clive.__private.before_launch import prepare_before_launch

    prepare_before_launch()
    run_app(["--dev", "clive.dev_import:clive_app"])


if __name__ == "__main__":
    main()
