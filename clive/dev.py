from __future__ import annotations

from textual.cli.cli import run_app


def main() -> None:
    run_app(["--dev", "clive.ui.clive:clive"])


if __name__ == "__main__":
    main()
