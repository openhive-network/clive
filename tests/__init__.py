from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WalletInfo:
    password: str
    name: str
