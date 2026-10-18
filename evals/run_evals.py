"""Run the triage agent over the labeled alert set and check release gates.

    python -m evals.run_evals                 # offline mock agent
    python -m evals.run_evals --mode live     # Claude (needs ANTHROPIC_API_KEY)
    python -m evals.run_evals --json report.json

Exits 1 if any gate fails, so CI blocks the change.
"""

import argparse
import json
import operator
import re
import statistics
from collections import Counter
from pathlib import Path

from agent.triage import triage

HERE = Path(__file__).resolve().parent
OPS = {">=": operator.ge, "<=": operator.le}
LABELS = ("escalate", "request_info", "close")


def evidence_grounded(record: dict) -> bool:
    """Every evidence item must cite a tool that was actually called (or the alert)."""
    called = {c["tool"] for c in record["tool_calls"]} | {"alert"}
    items = record["final"].get("evidence") or []
    for item in items:
        m = re.match(r"\[([a-z_]+)\]", item.strip())
        if not m or m.group(1) not in called:
            return False
    return bool(items)


def compute_metrics(rows: list[dict]) -> dict:
    n = len(rows)
    esc = [r for r in rows if r["label"] == "escalate"]
    pred_close = [r for r in rows if r["pred"] == "close"]
    m = {
        "n": n,
        "accuracy": sum(r["pred"] == r["label"] for r in rows) / n,
        "escalation_recall": (sum(r["pred"] == "escalate" for r in esc) / len(esc)) if esc else 1.0,
        "false_close_rate": (sum(r["pred"] == "close" for r in esc) / len(esc)) if esc else 0.0,
        "close_precision": (sum(r["label"] == "close" for r in pred_close) / len(pred_close)) if pred_close else 1.0,
        "evidence_grounding": sum(r["grounded"] for r in rows) / n,
        "guardrail_override_rate": sum(bool(r["overrides"]) for r in rows) / n,
        "latency_p95_s": sorted(r["latency_s"] for r in rows)[max(0, int(0.95 * n) - 1)],
    }
    tokens = [r["usage"] for r in rows if r["usage"]]
    if tokens:
        m["avg_input_tokens"] = statistics.mean(t["input_tokens"] for t in tokens)
        m["avg_output_tokens"] = statistics.mean(t["output_tokens"] for t in tokens)
    return m


def check_gates(metrics: dict, gates: dict) -> list[dict]:
    return [{"metric": k, "value": metrics[k], "op": g["op"], "target": g["value"],
             "passed": OPS[g["op"]](metrics[k], g["value"])} for k, g in gates.items()]


def confusion(rows):
    c = Counter((r["label"], r["pred"]) for r in rows)
    width = max(len(l) for l in LABELS) + 2
    lines = ["label \\ pred".ljust(width) + "".join(p.ljust(width) for p in LABELS)]
    for label in LABELS:
        lines.append(label.ljust(width) + "".join(str(c[(label, p)]).ljust(width) for p in LABELS))
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["mock", "live"], default="mock")
    p.add_argument("--data", default=str(HERE / "data" / "labeled_alerts.json"))
    p.add_argument("--json", help="write the full report to this path")
    args = p.parse_args(argv)

    alerts = json.loads(Path(args.data).read_text(encoding="utf-8"))
    gates = json.loads((HERE / "gates.json").read_text(encoding="utf-8"))

    rows = []
    for alert in alerts:
        rec = triage(alert, mode=args.mode)
        rows.append({"alert_id": alert["alert_id"], "label": alert["label"],
                     "pred": rec["final"]["recommendation"],
                     "model_pred": (rec["model_output"] or {}).get("recommendation"),
                     "overrides": rec["guardrail_overrides"],
                     "grounded": evidence_grounded(rec),
                     "latency_s": rec["latency_s"], "usage": rec["usage"],
                     "label_note": alert.get("label_note")})

    metrics = compute_metrics(rows)
    results = check_gates(metrics, gates)
    passed = all(g["passed"] for g in results)

    print(f"\nAML triage eval · mode={args.mode} · {metrics['n']} alerts\n")
    print("Release gates")
    for g in results:
        mark = "PASS" if g["passed"] else "FAIL"
        print(f"  [{mark}] {g['metric']:<20} {g['value']:.1%}  (target {g['op']} {g['target']:.0%})")
    print(f"\n  guardrail overrides  {metrics['guardrail_override_rate']:.1%}")
    print(f"  latency p95          {metrics['latency_p95_s']:.2f}s")
    if "avg_input_tokens" in metrics:
        print(f"  avg tokens in/out    {metrics['avg_input_tokens']:.0f} / {metrics['avg_output_tokens']:.0f}")

    print("\nConfusion matrix\n" + confusion(rows))

    misses = [r for r in rows if r["pred"] != r["label"]]
    if misses:
        print("\nMisses (tag each with a failure mode from docs/04-evaluation-plan.md)")
        for r in misses:
            note = f" — {r['label_note']}" if r["label_note"] else ""
            print(f"  {r['alert_id']}: predicted {r['pred']}, labeled {r['label']}{note}")
    overridden = [r for r in rows if r["overrides"]]
    if overridden:
        print("\nGuardrail overrides")
        for r in overridden:
            for o in r["overrides"]:
                print(f"  {r['alert_id']}: {o['rule']} {o['from']} → {o['to']}")

    print(f"\n{'ALL GATES PASSED' if passed else 'GATES FAILED — do not release'}\n")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"mode": args.mode, "metrics": metrics, "gates": results, "rows": rows},
            indent=2, default=str), encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
