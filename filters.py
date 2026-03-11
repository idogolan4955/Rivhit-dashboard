"""
Filter Components
─────────────────
Reusable sidebar / inline filter widgets.
"""
from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st


def month_year_selector(key_prefix: str = "sales") -> tuple[int, int]:
    """
    Year + Month selectors. Returns (year, month).
    """
    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox(
            "שנה",
            options=list(range(today.year, today.year - 5, -1)),
            index=0,
            key=f"{key_prefix}_year",
        )
    with col2:
        month = st.selectbox(
            "חודש",
            options=list(range(1, 13)),
            format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
            index=today.month - 1,
            key=f"{key_prefix}_month",
        )
    return year, month


def doc_type_filter(df: pd.DataFrame, key: str = "doc_type_filter") -> list[str]:
    """Multi-select for document types present in the DataFrame."""
    if df.empty or "document_type_display" not in df.columns:
        return []
    options = sorted(df["document_type_display"].dropna().unique().tolist())
    selected = st.multiselect("סוג מסמך", options=options, default=options, key=key)
    return selected


def agent_filter(df: pd.DataFrame, key: str = "agent_filter") -> list:
    """Multi-select for agents present in the DataFrame."""
    if df.empty:
        return []
    col = "agent_name" if "agent_name" in df.columns else "agent_id"
    options = sorted(df[col].dropna().unique().tolist())
    selected = st.multiselect("סוכן", options=options, default=options, key=key)
    return selected


def text_search(key: str = "search") -> str:
    """Free-text search box."""
    return st.text_input("🔍 חיפוש חופשי", key=key, placeholder="הקלד לחיפוש...")


def positive_balance_toggle(key: str = "pos_bal") -> bool:
    """Checkbox to show only positive balances."""
    return st.checkbox("הצג רק יתרות חיוביות", value=True, key=key)
