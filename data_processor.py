"""
Data Processor
──────────────
Normalises raw Rivhit API responses into clean pandas DataFrames.
Handles missing fields, type conversions, and column renaming.
"""
from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

import config

logger = logging.getLogger(__name__)

# ── Column mapping: API field → Hebrew display name ──────────


SALES_COLUMNS = {
    "customer_name": "שם לקוח",
    "customer_id": "מספר לקוח",
    "agent_name": "שם סוכן",
    "agent_id": "מספר סוכן",
    "document_type_display": "סוג מסמך",
    "document_number": "מספר מסמך",
    "amount": "סכום כולל",
    "amount_without_vat": "סכום ללא מע״מ",
    "document_date": "תאריך",
}

BALANCE_COLUMNS = {
    "customer_name": "שם לקוח",
    "customer_id": "מספר לקוח",
    "balance": "יתרה",
    "agent_id": "מספר סוכן",
}


# ── Sales DataFrame builder ────────────────────────────────────


def build_sales_dataframe(raw_docs: list[dict]) -> pd.DataFrame:
    """
    Convert raw Document.List items into a tidy DataFrame.
    Filters to relevant sales document types only.
    """
    if not raw_docs:
        return _empty_sales_df()

    df = pd.DataFrame(raw_docs)

    # --- keep only target doc types ---
    target_types = set(config.SALES_DOC_TYPE_IDS)
    if "document_type" in df.columns:
        df = df[df["document_type"].isin(target_types)].copy()

    if df.empty:
        return _empty_sales_df()

    # --- filter cancelled ---
    if "is_cancelled" in df.columns:
        df = df[df["is_cancelled"] != True].copy()  # noqa: E712

    # --- document type display name ---
    df["document_type_display"] = df["document_type"].map(
        lambda t: config.SALES_DOC_TYPES.get(t, df.loc[df["document_type"] == t, "document_type_name"].iloc[0]
            if "document_type_name" in df.columns and not df.loc[df["document_type"] == t].empty
            else str(t))
    )

    # --- compute amount without VAT ---
    df["amount"] = pd.to_numeric(df.get("amount", 0), errors="coerce").fillna(0)
    df["total_vat"] = pd.to_numeric(df.get("total_vat", 0), errors="coerce").fillna(0)
    df["amount_without_vat"] = df["amount"] - df["total_vat"]

    # --- parse dates ---
    df["document_date"] = _parse_dates(df.get("document_date"))

    # --- agent name placeholder (API returns only agent_id) ---
    df["agent_id"] = pd.to_numeric(df.get("agent_id", 0), errors="coerce").fillna(0).astype(int)
    df["agent_name"] = df["agent_id"].apply(lambda x: f"סוכן {x}" if x else "ללא סוכן")

    # --- customer ---
    df["customer_id"] = pd.to_numeric(df.get("customer_id", 0), errors="coerce").fillna(0).astype(int)
    df["customer_name"] = df.get("customer_name", "").fillna("לא ידוע")

    # --- document number ---
    df["document_number"] = pd.to_numeric(df.get("document_number", 0), errors="coerce").fillna(0).astype(int)

    return df


def _empty_sales_df() -> pd.DataFrame:
    cols = list(SALES_COLUMNS.keys())
    return pd.DataFrame(columns=cols)


# ── Balances DataFrame builder ──────────────────────────────────


def build_balances_dataframe(customers: list[dict], balances: dict[int, float]) -> pd.DataFrame:
    """
    Merge customer list with their balances into a DataFrame.
    `balances` maps customer_id → balance amount.
    """
    if not customers:
        return _empty_balance_df()

    df = pd.DataFrame(customers)

    df["customer_id"] = pd.to_numeric(df.get("customer_id", 0), errors="coerce").fillna(0).astype(int)
    if "customer_name" in df.columns:
        df["customer_name"] = df["customer_name"].fillna("")
    elif "last_name" in df.columns or "first_name" in df.columns:
        ln = df["last_name"].fillna("").astype(str) if "last_name" in df.columns else pd.Series("", index=df.index)
        fn = df["first_name"].fillna("").astype(str) if "first_name" in df.columns else pd.Series("", index=df.index)
        df["customer_name"] = (ln + " " + fn)
    else:
        df["customer_name"] = ""
    df["customer_name"] = df["customer_name"].astype(str).str.strip()
    df.loc[df["customer_name"] == "", "customer_name"] = "לא ידוע"
    df["agent_id"] = pd.to_numeric(df.get("agent_id", 0), errors="coerce").fillna(0).astype(int)

    df["balance"] = df["customer_id"].map(balances).fillna(0)

    return df[["customer_id", "customer_name", "agent_id", "balance"]].copy()


def build_balances_from_open_docs(open_docs: list[dict]) -> pd.DataFrame:
    """
    Alternative: build balances by aggregating Customer.OpenDocuments.
    Groups by customer and sums the balance field.
    """
    if not open_docs:
        return _empty_balance_df()

    df = pd.DataFrame(open_docs)

    df["customer_id"] = pd.to_numeric(df.get("customer_id", 0), errors="coerce").fillna(0).astype(int)
    df["customer_name"] = df.get("customer_name", "").fillna("לא ידוע")
    df["balance"] = pd.to_numeric(df.get("balance", 0), errors="coerce").fillna(0)

    grouped = (
        df.groupby(["customer_id", "customer_name"], as_index=False)
        .agg(balance=("balance", "sum"))
    )

    # agent_id isn't in open_documents — set to 0
    grouped["agent_id"] = 0
    return grouped


def _empty_balance_df() -> pd.DataFrame:
    return pd.DataFrame(columns=["customer_id", "customer_name", "agent_id", "balance"])


# ── Date parsing helper ─────────────────────────────────────────


def _parse_dates(series: pd.Series | None) -> pd.Series:
    """Try multiple date formats common in Rivhit responses."""
    if series is None:
        return pd.Series(dtype="datetime64[ns]")

    for fmt in (config.RIVHIT_DATE_FORMAT, "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return pd.to_datetime(series, format=fmt, errors="raise")
        except (ValueError, TypeError):
            continue

    return pd.to_datetime(series, errors="coerce")
