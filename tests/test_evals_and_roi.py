import json
import unittest
from pathlib import Path

from evals import run_evals
from roi import roi_model

ROOT = Path(__file__).resolve().parent.parent


class EvalTests(unittest.TestCase):
    def test_metrics_on_known_rows(self):
        rows = [
            {"label": "escalate", "pred": "escalate", "grounded": True, "overrides": [], "latency_s": 1, "usage": None},
            {"label": "escalate", "pred": "close", "grounded": True, "overrides": [], "latency_s": 1, "usage": None},
            {"label": "close", "pred": "close", "grounded": False, "overrides": [], "latency_s": 1, "usage": None},
        ]
        m = run_evals.compute_metrics(rows)
        self.assertAlmostEqual(m["escalation_recall"], 0.5)
        self.assertAlmostEqual(m["false_close_rate"], 0.5)
        self.assertAlmostEqual(m["close_precision"], 0.5)

    def test_grounding_rejects_uncited_evidence(self):
        rec = {"tool_calls": [{"tool": "screen_sanctions"}],
               "final": {"evidence": ["[get_customer_profile] made up"]}}
        self.assertFalse(run_evals.evidence_grounded(rec))

    def test_mock_agent_passes_release_gates(self):
        self.assertEqual(run_evals.main(["--mode", "mock"]), 0)


class RoiTests(unittest.TestCase):
    def setUp(self):
        self.a = json.loads((ROOT / "roi" / "assumptions.json").read_text())

    def test_hours_saved(self):
        r = roi_model.compute(self.a)
        expected = 9000 * 0.64 * (22 - 13) / 60
        self.assertAlmostEqual(r["hours_saved_per_month"], expected)

    def test_no_savings_means_no_payback(self):
        a = dict(self.a, pilot_handle_minutes=self.a["baseline_handle_minutes"])
        self.assertIsNone(roi_model.compute(a)["payback_months"])


if __name__ == "__main__":
    unittest.main()
