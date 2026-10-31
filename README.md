# the_contract_watch — Job-Search Agent, layer 1 (watch)

Implements the fetch / state / persona parts of `CONTRACT.md`. The rule judge and Claude verdicts are **not** built in this layer.

## Setup
```
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest
```

## Usage
```
python -m agent.run --label live                                    # fetch live, diff against state
python -m agent.run --from-file <path> --label seeded-earlier       # run against a saved response
python -m agent.fetch <label>                                       # fetch-only; saves raw, does not touch state
```

## Layout
- `agent/fetch.py`: allow-list (`ALLOWED_HOSTS = {"boards-api.greenhouse.io"}`), checked before any network call; raw response bytes saved unmodified to `evidence/raw/<UTC>_<label>.json`.
- `agent/state.py`: `state/seen_ids.json`; new = ids in response not in state; no state file = baseline (zero new).
- `agent/persona.py`: refuses to run unless `personal.location` and `skills` exist, every email is `@example.com`, every phone uses the 555 exchange. Refusal messages name fields, never values.
- `agent/validate.py`: standalone justification validator and alignment checker (CONTRACT.md wrong versions 1 and 2), tested on CONSTRUCTED fake verdicts.
- `agent/rule_judge.py`: CONTRACT.md "The rule", deterministic, no model. Output `kind="RECORD"`. Clause 1 is case-insensitive as the contract states; clauses 2 and 3 are applied as written (case-sensitive substring).
- `agent/claude_judge.py`: one fresh, stateless Claude call per posting (Anthropic SDK if `ANTHROPIC_API_KEY` is set, else `claude -p --output-format json` with no tools, no session persistence, no settings, run from a temp dir). Model from `JUDGE_MODEL`, default `claude-sonnet-5-5`, recorded in every output. Prompts: `prompts/judge_v1.txt` (user message) and `prompts/system_v1.txt` (system prompt, sent verbatim); every instruction the model sees lives in `prompts/`. Output `kind="JUDGMENT"` (model output, not fact). Every call is logged to `evidence/claude_calls.jsonl`.
- `agent/validator.py`: strict check of Claude output; one retry, then `verdict="INVALID"` with raw text. Never repairs output.
- `python -m agent.run --rejudge <run.json>` re-runs both judges on a saved run's new postings and writes `<run>_verdicts.json`; state is untouched.
- `scripts/make_seeded.py`: builds the SEEDED earlier snapshot.
- `resume/persona.json`: fictional persona Priya Nair, copied unmodified from the-reallocation-engine `search/examples/priya-nair/resume.example.json`.

## Evidence notes: SEEDED / CONSTRUCTED artifacts
Both runs happened on 2026-10-31, so the "earlier" snapshot is constructed, not observed.

| File | Status |
|---|---|
| `evidence/raw/20261031T182100Z_live.json` | **Real** live response from Greenhouse board `cloudflare`, unmodified (464 jobs). |
| `evidence/raw/SEEDED_earlier.json` | **SEEDED / CONSTRUCTED.** The live response above with exactly 5 postings removed: the last 5 by sorted numeric id (8332361, 8335069, 8335468, 8335469, 8338018). The other 459 jobs and `meta` are unchanged, so `meta.total` still says 464. Re-serialized with indentation. |
| `evidence/runs/20261031T182105Z_seeded-earlier.json` | Run 1 (baseline, no prior state) against the **SEEDED** file: 459 postings, 0 new. |
| `evidence/runs/20261031T182105Z_live-vs-SEEDED-baseline.json` | Run 2 against the real live response, diffed against state from the **SEEDED** baseline: 5 new, exactly the 5 removed ids. |
| `evidence/runs/20261031T182105Z_live-vs-SEEDED-baseline_verdicts.json` | Rule (RECORD) and Claude (JUDGMENT) verdicts for run 2's 5 new postings, produced by `--rejudge` at 2026-10-31T18:39Z. These postings are new only relative to the SEEDED baseline. |
| `evidence/claude_calls.jsonl` | Log of the 5 real Claude calls behind those verdicts. Those 5 lines have no `system_prompt_file` field: they were made while the system prompt was still hard-coded in `agent/claude_judge.py`, with the same text now in `prompts/system_v1.txt` ("You are a strict classifier. Follow the user's instructions exactly."). They were not re-run. Calls made after that move record `system_prompt_file`. |
| `state/seen_ids.json` | State after run 2 (464 ids). |

The 5 "new" postings are new only relative to the SEEDED baseline, not new on the board since an earlier real fetch.

All posting data in `tests/` is CONSTRUCTED fake data; the `*_WRONG` functions there are CONSTRUCTED wrong implementations used to show the tests catch each wrong version in CONTRACT.md.
