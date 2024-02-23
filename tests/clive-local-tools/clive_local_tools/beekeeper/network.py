from __future__ import annotations

import socket


def get_port() -> int:
    """Return free port."""
    sock = socket.socket()
    sock.bind(("", 0))
    return int(sock.getsockname()[1])
