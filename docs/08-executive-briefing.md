# 08 — Executive Briefing

**To:** Chief Compliance Officer, Meridian Regional Bank
**Re:** AML Alert Triage Agent — pilot plan and decision points
**Length:** one page, by design

---

**The ask.** Approve a 14-week pilot of an AI agent that prepares L1 AML alert reviews for analysts, starting with the three monitoring rules that make up 64% of alert volume.

**Why now.** The 11-day backlog is tied to an open regulatory finding. Analysts spend about 70% of each review gathering data from four systems, which is mechanical work an agent can do reliably.

**What changes for analysts.** When an analyst opens an alert, the evidence is already gathered, with a recommended action and the reasons behind it. The analyst still decides. Nothing is closed, escalated or filed automatically.

**How we keep it safe.**
- A release gate requires the agent to catch **100%** of alerts that should be escalated on a 500-alert test set built by your analysts and adjudicated by your BSA Officer.
- Sanctions hits are always escalated by hard-coded rules, regardless of what the model suggests.
- Model Risk Management validates the agent before analysts see it.
- Every step is logged for examiners.

**What success looks like (week 14).**

| Measure | Today | Pilot target |
|---|---|---|
| Missed escalations | — | Zero |
| Median review time | 22 min | ≤ 13 min |
| QA rejection rate | 8% | ≤ 3% |
| Backlog age | 11 days | ≤ 3 days |

At target, that frees roughly the capacity of 5 analysts at current volume (see `roi/` for the model and sensitivity range).

**Decisions we need from you.**
1. Name the long-term owner: FIU Operations or the central AI platform team (by week 4).
2. Endorse the staged validation approach with MRM (by week 5).

**What would make us stop.** Any missed escalation in the test set or the pilot, or a high-severity MRM finding. We'd fix the cause in shadow mode rather than lower the bar.
