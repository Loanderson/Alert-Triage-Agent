# 05 — Value Measurement & ROI

## 1. Principles

- **Baseline before build.** Baselines were captured in discovery from 6 months of system data, not estimated in a workshop.
- **Control group, not before/after.** Backlog pressure and seasonal volume change over time; a concurrent control group separates the agent's effect from everything else.
- **Report the miss.** If a hypothesis fails, the read-out says so and explains why.

## 2. Pilot design

| Element | Design |
|---|---|
| Treatment | 6 L1 analysts with the agent panel |
| Control | 8 L1 analysts without it, same queues |
| Assignment | Alerts randomly routed between groups by the case management system |
| Duration | 4 weeks (≈ 2,300 alerts per group at current volume) |
| Novelty effect | Week 1 reported separately; ROI computed on weeks 2–4 |

## 3. KPIs

| KPI | Source | Frequency | Owner |
|---|---|---|---|
| Median and p90 handle time | Case management time-in-state | Daily | FIU Ops |
| Escalation recall (QA sample) | QA reviewer labels | Weekly | BSA Officer |
| QA rejection rate | QA system | Weekly | QA lead |
| Acceptance without edit | Agent service log | Daily | TDL |
| Override reasons | Analyst override capture | Weekly | TDL |
| Backlog age | Ops dashboard | Daily | FIU Ops |
| Cost per alert | Gateway logs | Weekly | TDL |

## 4. ROI model

`roi/roi_model.py` takes the baseline and pilot numbers in `roi/assumptions.json` and produces:

- Analyst hours saved per month
- Equivalent FTE capacity released
- Net monthly value after model and platform costs
- Payback period on implementation cost
- A sensitivity table (what if handle-time savings are only half as large?)

```bash
python -m roi.roi_model
python -m roi.roi_model --assumptions my_numbers.json
```

The numbers in `assumptions.json` are illustrative pilot targets, not results.

## 5. How value is framed for the sponsor

"Capacity released" is the honest framing here. The bank isn't cutting analysts; it is clearing a backlog that drew a regulatory finding and absorbing volume growth without new hires. The read-out leads with risk outcomes (recall, QA quality, backlog age), then capacity, then dollars.
