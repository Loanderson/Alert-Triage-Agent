# 07 — Delivery Operations

## 1. Cadence

| Ceremony | When | Who | Output |
|---|---|---|---|
| Stand-up | Daily, 15 min | FDEs, customer engineers, TDL | Blockers named with an owner |
| Sprint planning | Every 2 weeks | Delivery team + FIU Ops product owner | Committed backlog |
| Eval review | Weekly | TDL, FDE lead, 1 analyst SME | Failure-mode tags triaged |
| Milestone review | At each milestone | Sponsor delegate + approvers | Written acceptance |
| Steering committee | Weekly, 30 min | CCO, BSA Officer, Head of FIU Ops, TDL | Decisions and escalations |

## 2. RACI

| Activity | TDL | FDEs | Customer Eng | FIU Ops | BSA Officer | MRM | InfoSec |
|---|---|---|---|---|---|---|---|
| SOW and plan | **A/R** | C | C | C | C | I | I |
| Agent build | A | **R** | C | I | I | I | I |
| UI integration | A | C | **R** | C | I | I | I |
| Eval set labeling | A | C | I | **R** | C | I | I |
| Release gates | **A** | R | I | C | C | C | I |
| Security approval | R | C | C | I | I | I | **A** |
| Model validation | R | C | I | I | C | **A** | I |
| Go / no-go | R | I | I | C | C | C | C |

A = accountable · R = responsible · C = consulted · I = informed. The CCO is accountable for go / no-go.

## 3. Weekly status report (template)

```
AML Triage Agent — Week N status                          Overall: 🟢 / 🟡 / 🔴

Headline: one sentence on where we are against the plan.

Milestones          M2 ✅  M3 🟡 (InfoSec Qs open, due Fri)  M4 ⏳
This week           - ...
Next week           - ...
Eval gates          Recall 100% · False-close 0% · Accuracy 86% · Grounding 100%
Decisions needed    - [Owner, by date] ...
Risks changed       - R4 ↑ KYC feed slipped; fallback in place
```

## 4. Change requests

Requirements change; the point is to make the trade-off visible.

1. Anyone can raise a change request (one paragraph: what, why, who asked).
2. TDL assesses impact on scope, timeline, eval set, approvals and cost within 3 business days.
3. Steering committee decides: accept (with what moves out), defer to phase 2, or decline.
4. Accepted changes that affect contract scope get a written SOW amendment through Procurement.

**Example:** FIU Ops asked to add rule R-422 (rapid movement of funds) mid-build. Impact: +150 labeled alerts, +2 weeks, new MRM scope. Decision: deferred to phase 2; R-317 kept because its labeling was complete.

## 5. Handover

By week 14 the named owner has: the runbook, on-call guide, eval suite in their CI, dashboard access, the model doc, and two paired weeks with the FDEs. "Done" means they've run a gate and handled a simulated outage without us.
