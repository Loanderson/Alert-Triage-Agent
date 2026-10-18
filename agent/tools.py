"""Read-only tools the agent can call. In production these wrap the bank's
KYC store, transaction warehouse and screening system; here they read the
synthetic JSON in /data."""

import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path

from . import policy

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache(maxsize=None)
def _load(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def _normalize(name: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()


def get_customer_profile(customer_id: str, as_of: str = "2026-10-18") -> dict:
    profile = _load("customers.json").get(customer_id)
    if profile is None:
        return {"error": f"unknown customer {customer_id}"}
    age = (date.fromisoformat(as_of) - date.fromisoformat(profile["kyc_last_updated"])).days
    return {**profile, "customer_id": customer_id, "kyc_age_days": age,
            "kyc_stale": age > policy.KYC_STALE_DAYS}


def get_transaction_history(customer_id: str) -> dict:
    history = _load("transactions.json").get(customer_id)
    if history is None:
        return {"error": f"no history for {customer_id}"}
    return {"customer_id": customer_id, **history}


def screen_sanctions(name: str) -> dict:
    """Token-overlap match against the watchlist. A real deployment calls the
    bank's certified screening system instead."""
    target = set(_normalize(name).split())
    best, best_score = None, 0.0
    for entry in _load("sanctions.json")["entries"]:
        tokens = set(_normalize(entry["name"]).split())
        score = len(target & tokens) / max(len(tokens), 1)
        if score > best_score:
            best, best_score = entry, score
    if best and best_score >= 0.67:
        return {"match": True, "score": round(best_score, 2),
                "matched_name": best["name"], "list": best["list"]}
    return {"match": False, "score": round(best_score, 2)}


def near_threshold_deposits(deposits: list[float]) -> list[float]:
    return [d for d in deposits
            if policy.NEAR_THRESHOLD_FLOOR <= d < policy.CTR_THRESHOLD]


TOOL_FUNCTIONS = {
    "get_customer_profile": lambda a: get_customer_profile(a["customer_id"]),
    "get_transaction_history": lambda a: get_transaction_history(a["customer_id"]),
    "screen_sanctions": lambda a: screen_sanctions(a["name"]),
}

# Schemas in the format the Claude Messages API expects.
TOOL_SCHEMAS = [
    {
        "name": "get_customer_profile",
        "description": "KYC profile: segment, risk rating, expected monthly volume, occupation, KYC age.",
        "input_schema": {"type": "object",
                         "properties": {"customer_id": {"type": "string"}},
                         "required": ["customer_id"]},
    },
    {
        "name": "get_transaction_history",
        "description": "12-month summary: average monthly volume, largest single transaction, countries used, prior alerts and escalations.",
        "input_schema": {"type": "object",
                         "properties": {"customer_id": {"type": "string"}},
                         "required": ["customer_id"]},
    },
    {
        "name": "screen_sanctions",
        "description": "Screen a person or entity name against sanctions and PEP watchlists.",
        "input_schema": {"type": "object",
                         "properties": {"name": {"type": "string"}},
                         "required": ["name"]},
    },
    {
        "name": "submit_recommendation",
        "description": "Submit the final triage recommendation. Call exactly once, last.",
        "input_schema": {
            "type": "object",
            "properties": {
                "recommendation": {"type": "string", "enum": list(policy.RECOMMENDATIONS)},
                "risk_score": {"type": "integer", "minimum": 0, "maximum": 100},
                "rationale": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["recommendation", "risk_score", "rationale", "evidence"],
        },
    },
]
