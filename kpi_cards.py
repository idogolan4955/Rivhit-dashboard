"""
KPI Card Components
───────────────────
Reusable KPI metric cards for Streamlit dashboards.
"""
from __future__ import annotations

import streamlit as st

from utils.formatters import fmt_currency, fmt_number


def render_sales_kpis(total: float, total_ex_vat: float, doc_count: int, avg_per_doc: float):
    """Show four KPI cards for the Sales page."""
    cols = st.columns(4)
    with cols[0]:
        st.metric("סה״כ כולל מע״מ", fmt_currency(total))
    with cols[1]:
        st.metric("סה״כ ללא מע״מ", fmt_currency(total_ex_vat))
    with cols[2]:
        st.metric("מספר מסמכים", fmt_number(doc_count))
    with cols[3]:
        st.metric("ממוצע למסמך", fmt_currency(avg_per_doc))


def render_collection_kpis(
    total_displayed: float,
    customer_count: int,
    selected_total: float,
):
    """Show KPI cards for the Collection page."""
    cols = st.columns(3)
    with cols[0]:
        st.metric("סה״כ יתרות מוצגות", fmt_currency(total_displayed))
    with cols[1]:
        st.metric("לקוחות עם יתרה", fmt_number(customer_count))
    with cols[2]:
        st.metric("סכום מסומנים", fmt_currency(selected_total))
