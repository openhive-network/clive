from __future__ import annotations
import decimal



def decimal_multi(a: str, b: str) -> str:
    decimal.getcontext().prec = 50
    dec_a = decimal.Decimal(a)
    dec_b = decimal.Decimal(b)
    result = dec_a * dec_b
    return format(result, 'f') 
