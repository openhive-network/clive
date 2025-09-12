from __future__ import annotations

from decimal_add import decimal_add
from decimal_multi import decimal_multi


def compose(a: str, b: str) -> str:
    return decimal_add(a, b) + " " + decimal_multi(a, b)

if __name__ == "__main__":
    print(compose("1.1", "2.2"))
