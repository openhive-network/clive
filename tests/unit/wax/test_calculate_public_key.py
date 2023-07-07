from __future__ import annotations

import pytest

import wax


@pytest.mark.parametrize(
    ("pv", "pub"),
    [
        (b"5HrsWGvAPXxSt8UbAoosaaNXqwZqSbPcu51AZts5sbWP4FRK75h", b"5G7HFCyKq3onQZn2nVGphKfzYpRyLR8bBP1jQewtaNDA76n1RE"),
        (b"5JN1fKJ8Zdrn6NmwCtBx1ktALaUCTxdmVgtE8ZwVyxMiRjwE1Dh", b"8hCsdMnyrffbo1UPBn2XLQC5TPbZ8PnBNzRgUVwp3e19JHrWTA"),
        (b"5KPSLEcntyCQ3GL85tq22e4aYPQQAeofGBUMzBwRa338GGPkoaE", b"6w5YXbTT2dXNjbfUw6AuFnmtHjoHKVuH6Se21nsjiQDxsAafFt"),
        (b"5HufMWCkd6VSoTWY4Vac7GYZnijmBnahYw4WRFAVWM5WCg41btp", b"5bmHcoCxiwL7NB7sAZ3CdcrnS3xjZ1aenxAth7Zh3DHfZwZqu2"),
        (b"5JVpkan3wmfp739qqnHB74SFtquYnbSJKKSNw6eav9FSiSaUZ51", b"6cJuz8XUkYMDgAWfjnhCTMTyf19T9hMiqBdnhKt6ZDtSW4eSbn"),
        (b"5JQZYQEC6td4Qgix5XjvVPndn9KPg4s36bYs6GB1RfRKoVcyRbg", b"8ed5aCG1z4ytR6SXGu4NP8u5t2NPnjApus1DzTEFhaaJaNTchr"),
        (b"5JWWf8VHH4fgYqWSwkzqFv9bVwfLCKihWDgLUG8VhaSzJK6vgGb", b"6SgC7CiAUKnrPPE2xZM26LBvaccpUg8GEw2KTGxzcKas1FQa6o"),
        (b"5KA8z1BDz4Tx1Rv3dkyUE8ySPg5q9iZ47JQtZV9LCkU9WpkT5jx", b"8ijGkwArT88m6u93iBrb8HPtBdkfLT2ZqyHa3nGzPKiwyrMGkQ"),
        (b"5KULwD6ifh2kDVfoJzMDiab7dWt1Xm5B3tyacXS2AtAdTTtw8ZR", b"4zkfhmsWY1LkUQTRqqMcCkcTYGmwWa66iu9DxpdGf2Fide1MfV"),
        (b"5K9NbgGuV1ptFNXFdD6qtXnZ9cXmnJx9MstkJefK3uVGm92QRMM", b"6Ti6u3nyvd1mcRQtXbKCxXXuWVNRpzxudtioTtCtGstfkuDxve"),
    ],
)
def test_proper_calculations(pv: bytes, pub: bytes) -> None:
    assert wax.calculate_public_key(pv).result == pub
