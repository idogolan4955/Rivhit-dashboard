"""
Formatting Utilities
────────────────────
Number, currency, and date display helpers.
"""
from __future__ import annotations


def fmt_currency(value: float, symbol: str = "₪") -> str:
    """Format a number as Israeli currency: ₪ 1,234.56"""
    if value < 0:
        return f"-{symbol} {abs(value):,.2f}"
    return f"{symbol} {value:,.2f}"


def fmt_number(value: float | int) -> str:
    """Format a number with thousands separator."""
    if isinstance(value, float):
        return f"{value:,.2f}"
    return f"{value:,}"


def fmt_date(dt) -> str:
    """Format a datetime to dd/mm/yyyy."""
    try:
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(dt) if dt else ""
