"""Service entry point: run the agent, apply guardrails, write the audit record."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

from . import guardrails, tools

AUDIT_PATH = Path(__file__).resolve().parent.parent / "audit" / "audit_log.jsonl"


def triage(alert: dict, mode: str = "mock", audit: bool = False, **kwargs) -> dict:
    started = time.perf_counter()
    if mode == "live":
        from . import claude_agent as engine
    elif mode == "mock":
        from . import mock_agent as engine
    else:
        raise ValueError(f"unknown mode {mode!r}")

    run = engine.run(alert, **kwargs)

    # The service fetches the control inputs itself; it does not trust the
    # model's account of what the tools said.
    context = {
        "sanctions": tools.screen_sanctions(alert["counterparty"]),
        "profile": tools.get_customer_profile(alert["customer_id"]),
    }
    final, overrides = guardrails.apply(run["result"], context)

    record = {
        "alert_id": alert["alert_id"],
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model_output": run["result"],
        "final": final,
        "guardrail_overrides": overrides,
        "tool_calls": run["tool_calls"],
        "usage": run["usage"],
        "latency_s": round(time.perf_counter() - started, 3),
    }
    if audit:
        AUDIT_PATH.parent.mkdir(exist_ok=True)
        with open(AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
    return record
