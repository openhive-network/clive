from __future__ import annotations


def generate_wallet_name(number: int = 0) -> str:
    return f"wallet-{number}"


def generate_wallet_password(number: int = 0) -> str:
    return f"password-{number}"


def generate_witness_name(i: int = 0) -> str:
    return f"witness-{i:02d}"


def generate_proposal_name(c: str) -> str:
    return f"proposal-{c}"
