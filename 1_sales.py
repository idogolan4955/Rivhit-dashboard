"""
Sales Page — עמוד מכירות
════════════════════════
Displays sales documents, KPIs, charts, and filterable table.
"""
from __future__ import annotations

import calendar
from datetime import date

import pandas as pd
import streamlit as st

import config
from components.charts import sales_by_agent, sales_by_day, sales_by_doc_type
from components.filters import agent_filter, doc_type_filter, month_year_selector, text_search
from components.kpi_cards import render_sales_kpis
from services.data_processor import build_sales_dataframe, SALES_COLUMNS
from services.rivhit_api import get_document_list, RivhitAPIError
from utils.formatters import fmt_currency, fmt_date

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="מכירות | " + config.APP_TITLE,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<h2 style="text-align:right;">📈 עמוד מכירות</h2>',
    unsafe_allow_html=True,
)

# ── Sidebar filters ─────────────────────────────────────────
with st.sidebar:
    st.header("🔧 סינון נתונים")
    year, month = month_year_selector("sales")

    from_date = date(year, month, 1).strftime(config.RIVHIT_DATE_FORMAT)
    last_day = calendar.monthrange(year, month)[1]
    to_date = date(year, month, last_day).strftime(config.RIVHIT_DATE_FORMAT)

    load_btn = st.button("🔄 טען נתונים", type="primary", use_container_width=True)

# ── Load data ────────────────────────────────────────────────


@st.cache_data(ttl=300, show_spinner="טוען נתוני מכירות...")
def _fetch_sales(fd: str, td: str) -> pd.DataFrame:
    raw = get_document_list(from_date=fd, to_date=td)
    return build_sales_dataframe(raw)


if "sales_df" not in st.session_state:
    st.session_state["sales_df"] = pd.DataFrame()

if load_btn:
    try:
        st.session_state["sales_df"] = _fetch_sales(from_date, to_date)
    except RivhitAPIError as exc:
        st.error(f"שגיאת API: {exc.client_msg}")
    except Exception as exc:
        st.error(f"שגיאה: {exc}")

df = st.session_state["sales_df"]

if df.empty:
    st.info("לחץ על 'טען נתונים' כדי להציג מכירות לחודש הנבחר.")
    st.stop()

# ── Inline filters ───────────────────────────────────────────
with st.sidebar:
    st.divider()
    selected_types = doc_type_filter(df, key="s_doc_type")
    selected_agents = agent_filter(df, key="s_agent")
    search_text = text_search(key="s_search")

# ── Apply filters ────────────────────────────────────────────
filtered = df.copy()

if selected_types:
    filtered = filtered[filtered["document_type_display"].isin(selected_types)]
if selected_agents:
    filtered = filtered[filtered["agent_name"].isin(selected_agents)]
if search_text:
    mask = filtered.apply(
        lambda row: search_text.lower() in " ".join(row.astype(str).values).lower(),
        axis=1,
    )
    filtered = filtered[mask]

# ── KPIs ─────────────────────────────────────────────────────
total = filtered["amount"].sum()
total_ex_vat = filtered["amount_without_vat"].sum()
doc_count = len(filtered)
avg_per_doc = total / doc_count if doc_count else 0

render_sales_kpis(total, total_ex_vat, doc_count, avg_per_doc)

# ── Charts ───────────────────────────────────────────────────
st.divider()
chart_cols = st.columns(3)
with chart_cols[0]:
    sales_by_day(filtered)
with chart_cols[1]:
    sales_by_doc_type(filtered)
with chart_cols[2]:
    sales_by_agent(filtered)

# ── Data Table ───────────────────────────────────────────────
st.divider()
st.subheader("טבלת מכירות")

display_cols = list(SALES_COLUMNS.keys())
display_df = filtered[[c for c in display_cols if c in filtered.columns]].copy()

# Format for display
if "document_date" in display_df.columns:
    display_df["document_date"] = display_df["document_date"].apply(fmt_date)
if "amount" in display_df.columns:
    display_df["amount"] = display_df["amount"].apply(lambda v: fmt_currency(v))
if "amount_without_vat" in display_df.columns:
    display_df["amount_without_vat"] = display_df["amount_without_vat"].apply(lambda v: fmt_currency(v))

display_df = display_df.rename(columns=SALES_COLUMNS)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=min(600, 40 + 35 * len(display_df)),
)

st.caption(f"מציג {len(display_df)} מסמכים מתוך {len(df)} סה״כ.")
