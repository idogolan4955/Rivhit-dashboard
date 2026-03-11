"""
Chart Components
────────────────
Plotly-based charts for Sales and Collection dashboards.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ── Shared layout defaults ──────────────────────────────────────

_LAYOUT = dict(
    font=dict(family="Assistant, Heebo, Arial, sans-serif", size=13),
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=340,
)

_COLORS = px.colors.qualitative.Set2


def _apply_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**_LAYOUT, title=dict(text=title, x=0.5, xanchor="center"))
    return fig


# ── Sales charts ────────────────────────────────────────────────


def sales_by_day(df: pd.DataFrame):
    """Bar chart: total sales per day in the selected month."""
    if df.empty or "document_date" not in df.columns:
        st.info("אין נתונים להצגה")
        return
    daily = df.groupby(df["document_date"].dt.date, as_index=False).agg(
        total=("amount", "sum")
    )
    daily.columns = ["יום", "סכום"]
    fig = px.bar(daily, x="יום", y="סכום", color_discrete_sequence=_COLORS)
    fig = _apply_layout(fig, "מכירות לפי יום")
    fig.update_xaxes(tickformat="%d/%m")
    st.plotly_chart(fig, use_container_width=True)


def sales_by_doc_type(df: pd.DataFrame):
    """Pie chart: sales breakdown by document type."""
    if df.empty:
        st.info("אין נתונים להצגה")
        return
    grouped = df.groupby("document_type_display", as_index=False).agg(total=("amount", "sum"))
    grouped.columns = ["סוג מסמך", "סכום"]
    fig = px.pie(grouped, names="סוג מסמך", values="סכום", color_discrete_sequence=_COLORS)
    fig = _apply_layout(fig, "חלוקה לפי סוג מסמך")
    st.plotly_chart(fig, use_container_width=True)


def sales_by_agent(df: pd.DataFrame):
    """Bar chart: sales breakdown by agent."""
    if df.empty:
        st.info("אין נתונים להצגה")
        return
    grouped = df.groupby("agent_name", as_index=False).agg(total=("amount", "sum"))
    grouped.columns = ["סוכן", "סכום"]
    grouped = grouped.sort_values("סכום", ascending=False)
    fig = px.bar(grouped, x="סוכן", y="סכום", color_discrete_sequence=_COLORS)
    fig = _apply_layout(fig, "מכירות לפי סוכן")
    st.plotly_chart(fig, use_container_width=True)


# ── Collection charts ───────────────────────────────────────────


def balances_by_agent(df: pd.DataFrame):
    """Bar chart: total balances by agent."""
    if df.empty or "agent_id" not in df.columns:
        st.info("אין נתונים להצגה")
        return
    grouped = (
        df[df["balance"] > 0]
        .groupby("agent_id", as_index=False)
        .agg(total=("balance", "sum"))
    )
    grouped["agent_label"] = grouped["agent_id"].apply(
        lambda x: f"סוכן {x}" if x else "ללא סוכן"
    )
    grouped.columns = ["agent_id", "סכום", "סוכן"]
    fig = px.bar(grouped, x="סוכן", y="סכום", color_discrete_sequence=_COLORS)
    fig = _apply_layout(fig, "יתרות לפי סוכן")
    st.plotly_chart(fig, use_container_width=True)
