"""
Rivhit Business Dashboard
══════════════════════════
Main entry point.  Run with:  streamlit run app.py
"""
import streamlit as st
import config

# ── Page config (must be the first Streamlit command) ───────
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS for RTL + professional styling ───────────────
st.markdown(
    """
    <style>
    /* ── RTL support ── */
    .stApp, .stMarkdown, .stDataFrame,
    .stMetric, .stSelectbox, .stMultiSelect,
    .stTextInput, .stCheckbox {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stMetricValue"] {
        direction: ltr;       /* numbers stay LTR */
        text-align: center;
    }
    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8f9fc 0%, #eef1f8 100%);
        border: 1px solid #e2e6ef;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #5a6884;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1a2744;
    }
    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, #1a2744 0%, #2d4a7a 100%);
        color: white;
        padding: 1.2rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .main-header p {
        margin: 0.3rem 0 0;
        font-size: 0.95rem;
        opacity: 0.85;
    }
    /* ── Sidebar ── */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    /* ── Table adjustments ── */
    .stDataFrame table {
        direction: rtl;
    }
    .stDataFrame th {
        text-align: right !important;
        background-color: #f0f2f6 !important;
    }
    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 24px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Validate API token ──────────────────────────────────────
if not config.RIVHIT_API_TOKEN:
    st.error(
        "⚠️ לא הוגדר API Token!\n\n"
        "יש להגדיר את המשתנה `RIVHIT_API_TOKEN` בקובץ `.env` או במשתני הסביבה של Render."
    )
    st.stop()

# ── Header ──────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="main-header">
        <h1>{config.PAGE_ICON} {config.APP_TITLE}</h1>
        <p>ניהול מכירות וגבייה בזמן אמת</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Navigation ──────────────────────────────────────────────
st.markdown(
    """
    > 📂 בחר עמוד מתפריט הצד (Sidebar) משמאל, או השתמש בניווט למטה.
    """
)

col1, col2 = st.columns(2)
with col1:
    if st.button("📈  עמוד מכירות", use_container_width=True, type="primary"):
        st.switch_page("pages/1_sales.py")
with col2:
    if st.button("💰  עמוד גבייה", use_container_width=True, type="primary"):
        st.switch_page("pages/2_collection.py")

st.divider()
st.caption("Rivhit Business Dashboard v1.0  •  Built with Streamlit  •  Data from Rivhit Online API")
