from __future__ import annotations

import os

from textual.features import parse_features
from textual_dev.tools.run import run_app


def main() -> None:
    environment = dict(os.environ)

    features = set(parse_features(environment.get("TEXTUAL", "")))
    features.add("debug")
    features.add("devtools")

    environment["TEXTUAL"] = ",".join(sorted(features))

    run_app("clive/main.py", [], environment)


if __name__ == "__main__":
    main()
