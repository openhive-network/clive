from __future__ import annotations


def is_in_dev_mode() -> bool:
    from clive.__private.config import settings

    return settings.get("dev", False)  # type: ignore[no-any-return]


def main() -> None:
    import os

    from textual.features import parse_features
    from textual_dev.tools.run import run_app

    environment = dict(os.environ)

    features = set(parse_features(environment.get("TEXTUAL", "")))
    features.add("debug")
    features.add("devtools")

    environment["TEXTUAL"] = ",".join(sorted(features))
    environment["CLIVE_DEV"] = "1"

    run_app("clive/main.py", [], environment)


if __name__ == "__main__":
    main()
