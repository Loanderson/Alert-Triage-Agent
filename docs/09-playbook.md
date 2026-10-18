# 09 — Reusable Delivery Playbook

What carries over from this engagement to the next regulated agent deployment, whatever the industry.

## The sequence

1. **Shadow the work before scoping it.** Measure where the time actually goes. Here it was gathering, not judging, which changed the MVP.
2. **Find the asymmetric metric.** Every regulated workflow has one error that is much worse than the others (missed escalation, wrong dose, mis-sold product). Make it the hard gate; let everything else be a target.
3. **Build the labeled set before the agent.** Use the customer's experts, measure their agreement, and fix the policy if they disagree.
4. **Put controls in code, after the model.** Prompts guide; guardrails control. Guardrails can only make an output more cautious, and every override is logged.
5. **Start all approvals in parallel, early.** Model risk, security, legal and architecture reviews are usually the critical path, not engineering.
6. **Shadow mode, then a controlled pilot.** Never a straight before/after.
7. **Report value as the sponsor's problem, solved.** Risk outcomes first, then capacity, then dollars.

## Templates in this repo

| Need | Template |
|---|---|
| Discovery write-up | `01-discovery.md` |
| SOW with value hypotheses | `02-sow.md` |
| Architecture + decision log | `03-architecture.md` |
| Eval plan + failure taxonomy | `04-evaluation-plan.md` |
| Pilot design + KPIs | `05-value-measurement.md` |
| Security / MRM pack + risk register | `06-risk-and-compliance.md` |
| Cadence, RACI, status, change control | `07-delivery-ops.md` |
| One-page exec brief | `08-executive-briefing.md` |
| Eval harness with CI gates | `evals/` |
| ROI calculator with sensitivity | `roi/` |

## How it adapts

| Vertical | Workflow | Asymmetric metric | Key approver |
|---|---|---|---|
| Banking (this repo) | AML alert triage | Missed escalation | Model Risk Mgmt |
| Insurance | Claims fraud referral | Missed fraud referral | Special Investigations Unit |
| Pharma | Adverse event intake | Missed serious adverse event | Pharmacovigilance / QA |
| Healthcare payer | Prior authorization | Wrongful denial | Medical director |
| Retail | Supplier compliance review | Missed restricted-substance flag | Product safety |
