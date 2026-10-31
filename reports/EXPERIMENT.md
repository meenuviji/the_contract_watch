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

- **The change:** In `prompts/judge_v2.txt`, I tightened Clause 2 to explicitly mandate an automatic `not_relevant` verdict if the posting requires 3+ years of professional experience or contains senior-level scope, preventing the model from falsely accepting mid-level roles that omit seniority markers from the title.
- **Outcome:** The held-out split contained 0 relevant ground-truth labels, which resulted in `judge_v1`, `judge_v2`, and the constant `not_relevant` baseline all achieving identical 10/10 scores. Because there were no positive instances in either the dev or held-out sets, this experiment cannot empirically demonstrate whether the change to Clause 2 helped or hurt classifier performance.