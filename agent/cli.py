"""Triage a single alert from the command line.

    python -m agent.cli --alert ALT-1003
    python -m agent.cli --alert ALT-1003 --mode live
"""

import argparse
import json
import sys
from pathlib import Path

from .triage import triage

ALERTS = Path(__file__).resolve().parent.parent / "evals" / "data" / "labeled_alerts.json"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="AML alert triage agent")
    p.add_argument("--alert", required=True, help="alert id, e.g. ALT-1003")
    p.add_argument("--mode", choices=["mock", "live"], default="mock")
    p.add_argument("--json", action="store_true", help="print the full audit record")
    args = p.parse_args(argv)

    alerts = {a["alert_id"]: a for a in json.loads(ALERTS.read_text(encoding="utf-8"))}
    if args.alert not in alerts:
        print(f"Unknown alert {args.alert}. Known: {', '.join(alerts)}", file=sys.stderr)
        return 2

    record = triage(alerts[args.alert], mode=args.mode, audit=True)
    if args.json:
        print(json.dumps(record, indent=2, default=str))
        return 0

    final = record["final"]
    print(f"{record['alert_id']}  →  {final['recommendation'].upper()}  (risk {final['risk_score']})")
    print(f"\n{final['rationale']}\n")
    for item in final["evidence"]:
        print(f"  • {item}")
    for o in record["guardrail_overrides"]:
        print(f"\n  ⚠ guardrail {o['rule']}: {o['from']} → {o['to']}")
    print("\nRequires analyst review: yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
