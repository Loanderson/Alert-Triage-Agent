"""Offline stand-in for the Claude agent.

It calls the same tools and returns the same output shape, so the eval
harness, guardrails and CI run without an API key. It encodes policy rules
1-7 and 9 directly. It deliberately does NOT encode rule 8 (high-risk
customers can't be closed), so the eval report shows the code guardrail
catching what the agent missed (ALT-1013).

History: v0.1 also lacked rule 7 (Policy 4.3). The eval harness caught it on
ALT-1017, close precision fell to 87.5% and the release gate failed. The fix
was to add the rule, not to lower the gate. See docs/04-evaluation-plan.md §6.
"""

from . import policy, tools


def run(alert: dict) -> dict:
    calls = []

    def call(name, args):
        out = tools.TOOL_FUNCTIONS[name](args)
        calls.append({"tool": name, "input": args, "output": out})
        return out

    profile = call("get_customer_profile", {"customer_id": alert["customer_id"]})
    history = call("get_transaction_history", {"customer_id": alert["customer_id"]})
    sanctions = call("screen_sanctions", {"name": alert["counterparty"]})

    amount = alert["amount"]
    country = alert["counterparty_country"]
    expected = profile["expected_monthly_volume"]
    ratio = amount / expected if expected else float("inf")
    new_country = country != profile["home_country"] and country not in history["countries_12m"]
    near = tools.near_threshold_deposits(alert.get("cash_deposits", []))

    evidence = [
        f"[get_customer_profile] {profile['segment']}, risk {profile['risk_rating']}, "
        f"expected ${expected:,}/month",
        f"[get_transaction_history] max single txn ${history['max_single_txn_12m']:,}; "
        f"countries {', '.join(history['countries_12m'])}; "
        f"{history['prior_escalations_12m']} prior escalations",
        f"[screen_sanctions] '{alert['counterparty']}': "
        + (f"MATCH {sanctions['matched_name']} ({sanctions['list']})" if sanctions["match"] else "no match"),
    ]

    if sanctions["match"]:
        rec, score, why = "escalate", 95, "Counterparty matches a sanctions watchlist entry."
    elif country in policy.HIGH_RISK_COUNTRIES:
        rec, score, why = "escalate", 90, f"Counterparty is in a high-risk jurisdiction ({country})."
    elif len(near) >= policy.STRUCTURING_MIN_DEPOSITS:
        rec, score, why = "escalate", 85, (
            f"{len(near)} cash deposits just under ${policy.CTR_THRESHOLD:,} suggest possible structuring.")
    elif ratio > policy.UNEXPLAINED_RATIO_ESCALATE and new_country:
        rec, score, why = "escalate", 80, (
            f"Amount is {ratio:.1f}x expected monthly volume to a jurisdiction not used in 12 months.")
    elif (ratio > policy.UNEXPLAINED_RATIO_INFO
          and amount > history["max_single_txn_12m"] * policy.HISTORY_TOLERANCE):
        rec, score, why = "request_info", 55, (
            f"Amount is {ratio:.1f}x expected volume and above the 12-month high; documentation needed.")
    elif new_country and ratio > 2:
        rec, score, why = "request_info", 50, f"New jurisdiction ({country}) at {ratio:.1f}x expected volume."
    elif country in policy.ELEVATED_RISK_COUNTRIES and amount > policy.OFFSHORE_DOC_THRESHOLD:
        rec, score, why = "request_info", 45, (
            f"Policy 4.3: transfer over ${policy.OFFSHORE_DOC_THRESHOLD:,} to {country} "
            "requires beneficial-owner documentation.")
    else:
        rec, score, why = "close", 15, "Activity is consistent with the customer's profile and history."

    if near:
        evidence.append(f"[alert] {len(near)} of {len(alert['cash_deposits'])} cash deposits near threshold")

    result = {"recommendation": rec, "risk_score": score, "rationale": why, "evidence": evidence}
    return {"result": result, "tool_calls": calls, "usage": None}
