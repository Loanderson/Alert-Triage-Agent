"""Turn baseline and pilot numbers into a sponsor-ready ROI summary.

    python -m roi.roi_model
    python -m roi.roi_model --assumptions my_numbers.json
"""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def compute(a: dict, savings_scale: float = 1.0) -> dict:
    alerts = a["alerts_per_month"] * a["in_scope_share"]
    minutes_saved = (a["baseline_handle_minutes"] - a["pilot_handle_minutes"]) * savings_scale
    hours_saved = alerts * minutes_saved / 60
    gross = hours_saved * a["analyst_loaded_cost_per_hour"]
    run_cost = alerts * a["model_cost_per_alert"] + a["platform_cost_per_month"]
    net = gross - run_cost
    return {
        "in_scope_alerts_per_month": alerts,
        "handle_time_reduction": minutes_saved / a["baseline_handle_minutes"],
        "hours_saved_per_month": hours_saved,
        "fte_capacity_released": hours_saved / a["analyst_productive_hours_per_month"],
        "gross_value_per_month": gross,
        "run_cost_per_month": run_cost,
        "net_value_per_month": net,
        "payback_months": a["implementation_cost"] / net if net > 0 else None,
        "first_year_net": net * 12 - a["implementation_cost"],
    }


def render(a: dict) -> str:
    base = compute(a)
    payback = f"{base['payback_months']:.1f} months" if base["payback_months"] else "never"
    out = [
        "AML triage agent — ROI summary (illustrative)",
        "",
        f"  In-scope alerts / month     {base['in_scope_alerts_per_month']:,.0f}",
        f"  Handle-time reduction       {base['handle_time_reduction']:.0%}",
        f"  Analyst hours saved / month {base['hours_saved_per_month']:,.0f}",
        f"  Capacity released           {base['fte_capacity_released']:.1f} FTE",
        f"  Gross value / month         ${base['gross_value_per_month']:,.0f}",
        f"  Run cost / month            ${base['run_cost_per_month']:,.0f}",
        f"  Net value / month           ${base['net_value_per_month']:,.0f}",
        f"  Payback                     {payback}",
        f"  First-year net              ${base['first_year_net']:,.0f}",
        "",
        "Sensitivity: what if the time savings are smaller or larger than targeted?",
        "",
        "  savings   FTE released   net / month   payback",
    ]
    for scale in (0.5, 0.75, 1.0, 1.25):
        r = compute(a, scale)
        pb = f"{r['payback_months']:.1f} mo" if r["payback_months"] else "never"
        out.append(f"  {scale:>5.0%}   {r['fte_capacity_released']:>12.1f}   "
                   f"${r['net_value_per_month']:>10,.0f}   {pb:>7}")
    return "\n".join(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--assumptions", default=str(HERE / "assumptions.json"))
    args = p.parse_args(argv)
    a = json.loads(Path(args.assumptions).read_text(encoding="utf-8"))
    print(render(a))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
