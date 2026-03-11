"""
Collection Page — עמוד גבייה / יתרות לקוחות
════════════════════════════════════════════
Displays customer balances with selection, filtering, KPIs, and charts.
"""
from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

import config
from components.charts import balances_by_agent
from components.filters import agent_filter, positive_balance_toggle, text_search
from components.kpi_cards import render_collection_kpis
from services.data_processor import build_balances_dataframe, BALANCE_COLUMNS
from services.rivhit_api import (
    RivhitAPIError,
    get_customer_balance,
    get_customer_list,
)
from utils.formatters import fmt_currency

logger = logging.getLogger(__name__)

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="גבייה | " + config.APP_TITLE,
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<h2 style="text-align:right;">💰 עמוד גבייה / יתרות לקוחות</h2>',
    unsafe_allow_html=True,
)


# ── Data loading ─────────────────────────────────────────────


@st.cache_data(ttl=600, show_spinner="טוען רשימת לקוחות...")
def _fetch_customers_and_balances() -> pd.DataFrame:
    """
    Fetch all customers, then get balance for each.
    NOTE: For accounts with many customers this can be slow
    because Customer.Balance requires one call per customer.
    Consider caching aggressively or using Customer.OpenDocuments instead.
    """
    customers = get_customer_list()
    if not customers:
        return pd.DataFrame(columns=["customer_id", "customer_name", "agent_id", "balance"])

    balances: dict[int, float] = {}
    progress = st.progress(0, text="טוען יתרות לקוחות...")
    total = len(customers)

    for i, cust in enumerate(customers):
        cid = cust.get("customer_id")
        if cid:
            try:
                balances[cid] = get_customer_balance(cid)
            except Exception as exc:
                logger.warning("Failed to get balance for customer %s: %s", cid, exc)
                balances[cid] = 0.0
        progress.progress((i + 1) / total, text=f"טוען יתרות... ({i + 1}/{total})")

    progress.empty()
    return build_balances_dataframe(customers, balances)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("🔧 סינון נתונים")
    load_btn = st.button("🔄 טען נתוני גבייה", type="primary", use_container_width=True)

if "balances_df" not in st.session_state:
    st.session_state["balances_df"] = pd.DataFrame()

if load_btn:
    try:
        st.session_state["balances_df"] = _fetch_customers_and_balances()
    except RivhitAPIError as exc:
        st.error(f"שגיאת API: {exc.client_msg}")
    except Exception as exc:
        st.error(f"שגיאה: {exc}")

df = st.session_state["balances_df"]

if df.empty:
    st.info("לחץ על 'טען נתוני גבייה' כדי להציג יתרות לקוחות.")
    st.stop()

# ── Sidebar filters ──────────────────────────────────────────
with st.sidebar:
    st.divider()
    # Agent filter — need to build agent labels
    df["agent_label"] = df["agent_id"].apply(lambda x: f"סוכן {x}" if x else "ללא סוכן")
    agent_options = sorted(df["agent_label"].unique().tolist())
    selected_agents = st.multiselect("סוכן", options=agent_options, default=agent_options, key="c_agent")
    pos_only = positive_balance_toggle(key="c_pos")
    search_text = text_search(key="c_search")

# ── Apply filters ────────────────────────────────────────────
filtered = df.copy()

if selected_agents:
    filtered = filtered[filtered["agent_label"].isin(selected_agents)]
if pos_only:
    filtered = filtered[filtered["balance"] > 0]
if search_text:
    mask = filtered.apply(
        lambda row: search_text.lower() in " ".join(row.astype(str).values).lower(),
        axis=1,
    )
    filtered = filtered[mask]

# ── Editable table with checkboxes ───────────────────────────
st.divider()
st.subheader("טבלת יתרות לקוחות")

if filtered.empty:
    st.warning("אין לקוחות להצגה עם הסינונים הנוכחיים.")
    st.stop()

# Prepare display dataframe
display_df = filtered[["customer_id", "customer_name", "agent_label", "balance"]].copy()
display_df = display_df.sort_values("balance", ascending=False).reset_index(drop=True)

# Use st.data_editor for checkboxes
display_df.insert(0, "סמן", False)

edited = st.data_editor(
    display_df.rename(columns={
        "customer_id": "מספר לקוח",
        "customer_name": "שם לקוח",
        "agent_label": "סוכן",
        "balance": "יתרה",
    }),
    use_container_width=True,
    hide_index=True,
    column_config={
        "סמן": st.column_config.CheckboxColumn("✅", default=False, width="small"),
        "יתרה": st.column_config.NumberColumn("יתרה", format="₪ %.2f"),
        "מספר לקוח": st.column_config.NumberColumn("מספר לקוח", format="%d"),
    },
    disabled=["מספר לקוח", "שם לקוח", "סוכן", "יתרה"],
    height=min(600, 45 + 35 * len(display_df)),
    key="balance_table",
)

# ── Calculate selected total ─────────────────────────────────
selected_mask = edited["סמן"] == True  # noqa: E712
selected_total = edited.loc[selected_mask, "יתרה"].sum() if selected_mask.any() else 0.0

# ── KPIs (above table via rerun context — placed after table for state) ──
total_displayed = filtered["balance"].sum()
customer_count = len(filtered[filtered["balance"] > 0])

# We render KPIs using a placeholder set before the table
# For better UX, use st.container to place KPIs at top

kpi_container = st.container()
with kpi_container:
    pass  # filled below

# Since Streamlit is top-down, let's reorder using columns at top
# Actually, let's use the pattern: compute first, display after

# ── Render KPIs at top (using empty containers) ──────────────
# We already displayed the table. For proper ordering we use
# st.empty / placeholder. Instead, let's place KPIs in sidebar summary.

with st.sidebar:
    st.divider()
    st.subheader("📊 סיכום")
    st.metric("סה״כ יתרות מוצגות", fmt_currency(total_displayed))
    st.metric("לקוחות עם יתרה", str(customer_count))
    st.metric("סכום מסומנים", fmt_currency(selected_total))

# ── Chart ────────────────────────────────────────────────────
st.divider()
balances_by_agent(filtered)

st.caption(f"מציג {len(filtered)} לקוחות.")
