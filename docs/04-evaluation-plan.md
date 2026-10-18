# 04 — Evaluation Plan

## 1. Why evals come first

In a regulated deployment, the eval suite *is* the acceptance test. It is the evidence MRM reviews, the gate every model or prompt change must pass, and the baseline for monitoring drift. We build the labeled set in weeks 2–4, before the agent is tuned, so we can't unconsciously fit the set to the agent.

## 2. The labeled set

| Item | Plan |
|---|---|
| Size | 500 historical alerts (this repo ships a 20-alert synthetic sample in `evals/data/`) |
| Sampling | Stratified by rule (R-101, R-204, R-317) and by historical outcome; true escalations oversampled to 20% so recall is measurable |
| Labeling | Two analysts label independently; BSA Officer adjudicates disagreements |
| Agreement | Cohen's kappa reported; if < 0.7, the policy itself is ambiguous and we fix the policy before the agent |
| Hold-out | 20% held out and only run at milestone gates |

## 3. Metrics

| Metric | Definition | Gate |
|---|---|---|
| **Escalation recall** | Of alerts labeled `escalate`, share the agent recommends `escalate` | **= 100%** |
| **False-close rate** | Share of `escalate` alerts the agent recommends `close` | **= 0%** |
| Accuracy | Exact match with label | ≥ 80% |
| Close precision | Of agent `close` recommendations, share labeled `close` | ≥ 90% |
| Evidence grounding | Every evidence item traces to a tool result | 100% |
| Guardrail override rate | Share of outputs changed by guardrails | Reported, not gated; rising trend is a warning |
| Cost per alert | Tokens × price | Reported; target < $0.15 |
| Latency p95 | Wall-clock | < 60 s |

Escalation recall is the one that matters most. Over-escalating costs L2 time; under-escalating is a regulatory failure. The gates are deliberately lopsided.

## 4. Failure-mode taxonomy

Every eval miss gets one tag, so we fix causes rather than individual cases:

| Tag | Example | Usual fix |
|---|---|---|
| `missed-signal` | Agent didn't notice amounts just under $10k | Tool returns a derived feature; policy prompt names the pattern |
| `over-trust-narrative` | Customer's stated reason accepted without checking activity | Policy: narrative is a claim, not evidence |
| `policy-gap` | Label and agent both defensible | Fix the written policy, then relabel |
| `stale-data` | Profile outdated | Staleness flag handling |
| `format` | Schema invalid | Usually a prompt or tool-schema issue |

## 5. Running it

```bash
python -m evals.run_evals                 # mock agent, offline
python -m evals.run_evals --mode live     # Claude, needs ANTHROPIC_API_KEY
python -m evals.run_evals --json report.json
```

The script exits non-zero if any gate fails, so CI blocks merges that break recall.

## 6. Worked example: a gate that did its job

The first version of the offline agent passed the recall gate but failed **close precision** (87.5% vs. a 90% gate).

| Step | What happened |
|---|---|
| Miss | ALT-1017: $600k to a Cayman affiliate, recommended `close`, labeled `request_info` |
| Tag | `missed-signal`: Policy 4.3 requires beneficial-owner documentation for offshore transfers over $500k |
| Fix | Added rule 7 to the agent's policy logic |
| Not done | Lowering the gate, or relabeling the alert to match the agent |
| Result | All gates green; accuracy 95% → 100% on the sample set |

The guardrail log still shows one override (ALT-1013, a high-risk customer the agent would have closed). That is intended: it shows the code control catching what the model misses.

## 7. From offline to production

1. **Offline gates** on the labeled set (M2).
2. **Shadow mode** on live alerts for 2 weeks: the agent runs, analysts never see it, and we compare against analyst decisions (M5).
3. **Controlled pilot** with treatment and control analysts (M6).
4. **Ongoing:** 10% QA sample of recommendations, weekly drift check, quarterly re-validation with MRM.
