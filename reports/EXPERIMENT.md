# Prompt experiment: judge_v1 baseline on dev

- Date (UTC): 2026-10-31, run `20261031T191349Z`
- Model: `claude-sonnet-5-5` (default (JUDGE_MODEL not set))
- Prompts: `prompts/system_v1.txt` (system), `prompts/judge_v1.txt` (user)
- One judgment per dev posting (validator allows one retry on invalid output; 0 retries used, 0 INVALID). Calls logged to `evidence/claude_calls.jsonl` (tag `experiment_v1_dev_20261031T191349Z`).
- Raw results: `evidence/runs/20261031T191349Z_experiment_v1_dev.json`
- v1 verdicts are JUDGMENT (model output, not fact). Rule verdicts are RECORD.

## My label counts per split

| split | relevant | not_relevant |
|---|---|---|
| dev | 0 | 10 |
| heldout | 0 | 10 |

## Dev results

| posting_id | my_label | rule verdict (RECORD) | v1 verdict (JUDGMENT) | match |
|---|---|---|---|---|
| 7572075 | not_relevant | not_relevant | not_relevant | yes |
| 8043974 | not_relevant | not_relevant | not_relevant | yes |
| 8050813 | not_relevant | not_relevant | not_relevant | yes |
| 8158617 | not_relevant | not_relevant | not_relevant | yes |
| 8184169 | not_relevant | not_relevant | not_relevant | yes |
| 8204353 | not_relevant | not_relevant | not_relevant | yes |
| 8221248 | not_relevant | not_relevant | not_relevant | yes |
| 8223736 | not_relevant | not_relevant | not_relevant | yes |
| 8248907 | not_relevant | not_relevant | not_relevant | yes |
| 8311376 | not_relevant | not_relevant | not_relevant | yes |

## Pass rate

- judge_v1 vs my labels: **10/10**
- Baseline to beat: a constant `not_relevant` judge scores **10/10** on dev.
- For reference, the rule judge (RECORD) vs my labels: 10/10.
- Because every dev label is `not_relevant`, the constant baseline is already at the maximum (10/10). On this dev set no judge can beat it, only tie it.

## Misses

None: v1 matched my label on all 10 dev postings.

## The one change I chose and why

**The observation.** judge_v1 matched 10/10 on dev, but every dev label is `not_relevant` (seniority, non-target function, or non-US location), so a constant "not_relevant" judge also scores 10/10. v1 made no dev errors, so this change is not motivated by an observed miss; it is motivated by reading v1's justifications. In `prompts/judge_v1.txt`, Clause 2 reads:

"2. Full-time early career: it is a full-time position (not an internship, co-op, or temp role) and asks for 0-2 years of experience. Senior, staff, principal, lead, or managerial roles are not relevant."

The justifications lean on title keywords and stated years. Postings can omit seniority words from the title (e.g. "Systems Engineer") while asking for 3–5+ years in the body, and Clause 2 does not say how to treat a posting that states no experience requirement at all.

**The single change.** In `prompts/judge_v2.txt`, Clause 2 is replaced with:

"2. Full-time early career: it is a full-time position (not an internship, co-op, or temp role) and explicitly asks for 0-2 years of experience (or is designated entry-level/new grad). If the posting requires 3+ years of full-time experience, or if the title contains Senior, Staff, Principal, Lead, or Manager, label it not_relevant."

This is one clause, but it changes two behaviors: a missing experience requirement now defaults to not_relevant, and 3+ years is now an explicit reject.

**What I expect, stated before running held-out.** I expect v2 to be at least as conservative as v1. On this data that cannot show improvement: with all-negative dev labels, a stricter prompt can only tie v1 on dev. The held-out run tests whether v2 wrongly rejects any posting I labeled relevant. If held-out also has no relevant labels, this experiment cannot distinguish v1, v2, and a constant judge, and I will report that.
