"""Deterministic controls applied after the model. They can only make a
recommendation more cautious, and every change is recorded."""

from . import policy

_CAUTION = {"close": 0, "request_info": 1, "escalate": 2}


def _raise_to(result: dict, target: str, rule: str, overrides: list) -> None:
    if _CAUTION[target] > _CAUTION[result["recommendation"]]:
        overrides.append({"rule": rule, "from": result["recommendation"], "to": target})
        result["recommendation"] = target


def apply(result: dict | None, context: dict) -> tuple[dict, list]:
    """context holds tool results the service fetched itself (not the model's
    claims): 'sanctions' and 'profile'."""
    overrides: list = []

    if not isinstance(result, dict) or result.get("recommendation") not in policy.RECOMMENDATIONS:
        result = {"recommendation": "request_info", "risk_score": 50,
                  "rationale": "Agent output was missing or invalid; routed to analyst.",
                  "evidence": []}
        overrides.append({"rule": "G4_schema_failure", "from": None, "to": "request_info"})
    else:
        result = dict(result)

    if context.get("sanctions", {}).get("match"):
        _raise_to(result, "escalate", "G1_sanctions_hit", overrides)

    if (context.get("profile", {}).get("risk_rating") == "high"
            and result["recommendation"] == "close"):
        _raise_to(result, "request_info", "G2_high_risk_no_close", overrides)

    if not result.get("evidence"):
        _raise_to(result, "request_info", "G3_no_evidence", overrides)

    result["requires_human_review"] = True  # G5: always true during the pilot
    return result, overrides
