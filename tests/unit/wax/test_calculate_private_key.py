from __future__ import annotations

import wax


def test_different_keys() -> None:
    assert wax.generate_private_key().result != wax.generate_private_key().result
