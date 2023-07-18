from __future__ import annotations

import os

from textual.cli._run import run_app
from textual.features import parse_features


def main() -> None:
    from clive.__private.before_launch import prepare_before_launch

    environment = dict(os.environ)

    features = set(parse_features(environment.get("TEXTUAL", "")))
    features.add("debug")
    features.add("devtools")

    environment["TEXTUAL"] = ",".join(sorted(features))

    prepare_before_launch()
    run_app("clive/main.py", [], environment)


if __name__ == "__main__":
    main()
