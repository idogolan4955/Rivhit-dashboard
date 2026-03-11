"""
Rivhit API Client
─────────────────
Handles all HTTP communication with the Rivhit Online API.
Each public function returns raw JSON (dict) or raises on fatal errors.
Retry logic and timeouts are handled internally.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import requests

import config

logger = logging.getLogger(__name__)


class RivhitAPIError(Exception):
    """Raised when the Rivhit API returns a non-zero error_code."""

    def __init__(self, error_code: int, client_msg: str, debug_msg: str):
        self.error_code = error_code
        self.client_msg = client_msg
        self.debug_msg = debug_msg
        super().__init__(f"Rivhit API error {error_code}: {client_msg} | {debug_msg}")


# ── low-level POST helper ──────────────────────────────────────


def _post(endpoint: str, payload: dict[str, Any]) -> dict:
    """
    POST to a Rivhit endpoint with retry + timeout.
    Returns the parsed JSON response dict.
    """
    url = f"{config.RIVHIT_BASE_URL}/{endpoint}"
    payload["api_token"] = config.RIVHIT_API_TOKEN

    last_exc: Exception | None = None
    for attempt in range(1, config.API_MAX_RETRIES + 1):
        try:
            logger.info("POST %s  (attempt %d)", endpoint, attempt)
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=config.API_TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()

            err = data.get("error_code", 0)
            if err and err != 0:
                raise RivhitAPIError(
                    err,
                    data.get("client_message", ""),
                    data.get("debug_message", ""),
                )
            return data

        except requests.exceptions.Timeout as exc:
            logger.warning("Timeout on %s (attempt %d)", endpoint, attempt)
            last_exc = exc
        except requests.exceptions.ConnectionError as exc:
            logger.warning("Connection error on %s (attempt %d)", endpoint, attempt)
            last_exc = exc
        except RivhitAPIError:
            raise  # don't retry business errors
        except Exception as exc:
            logger.error("Unexpected error on %s: %s", endpoint, exc)
            last_exc = exc

        if attempt < config.API_MAX_RETRIES:
            time.sleep(min(2 ** attempt, 8))

    raise RuntimeError(
        f"Failed after {config.API_MAX_RETRIES} retries on {endpoint}"
    ) from last_exc


# ── Public API methods ──────────────────────────────────────────


def get_document_list(
    from_date: str,
    to_date: str,
    from_doc_type: int | None = None,
    to_doc_type: int | None = None,
    from_agent_id: int | None = None,
    to_agent_id: int | None = None,
) -> list[dict]:
    """
    Fetch documents within a date range.
    Dates should be in dd/MM/yyyy format (Rivhit default).
    Returns list of document dicts.
    """
    payload: dict[str, Any] = {
        "from_date": from_date,
        "to_date": to_date,
    }
    if from_doc_type is not None:
        payload["from_document_type"] = from_doc_type
    if to_doc_type is not None:
        payload["to_document_type"] = to_doc_type
    if from_agent_id is not None:
        payload["from_agent_id"] = from_agent_id
    if to_agent_id is not None:
        payload["to_agent_id"] = to_agent_id

    data = _post("Document.List", payload)
    docs = (data.get("data") or {}).get("document_list") or []
    return docs


def get_document_type_list() -> list[dict]:
    """Fetch available document types for the account."""
    data = _post("Document.TypeList", {})
    return (data.get("data") or {}).get("document_type_list") or []


def get_customer_list(agent_id: int | None = None) -> list[dict]:
    """Fetch list of customers, optionally filtered by agent."""
    payload: dict[str, Any] = {}
    if agent_id is not None:
        payload["agent_id"] = agent_id
    data = _post("Customer.List", payload)
    return (data.get("data") or {}).get("customer_list") or []


def get_customer_balance(customer_id: int) -> float:
    """Return the balance for a single customer."""
    data = _post("Customer.Balance", {"customer_id": customer_id})
    return float((data.get("data") or {}).get("balance", 0))


def get_customer_open_documents(
    from_date: str | None = None,
    until_date: str | None = None,
    agent_id: int | None = None,
) -> list[dict]:
    """
    Fetch open (unpaid) documents across all customers.
    Useful for the collection / balances page.
    """
    payload: dict[str, Any] = {}
    if from_date:
        payload["from_date"] = from_date
    if until_date:
        payload["until_date"] = until_date
    if agent_id is not None:
        payload["agent_id"] = agent_id

    data = _post("Customer.OpenDocuments", payload)
    return (data.get("data") or {}).get("open_documents") or []


def get_company_details() -> dict:
    """Fetch company profile (name, address, etc.)."""
    data = _post("Company.Details", {})
    return data.get("data") or {}
