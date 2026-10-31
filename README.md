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
| `state/seen_ids.json` | State after run 2 (464 ids). |

The 5 "new" postings are new only relative to the SEEDED baseline, not new on the board since an earlier real fetch.

All posting data in `tests/` is CONSTRUCTED fake data; the `*_WRONG` functions there are CONSTRUCTED wrong implementations used to show the tests catch each wrong version in CONTRACT.md.

## Open contract items
`CONTRACT.md` still contains `BOARD_TOKEN_HERE` and `CITY_HERE`. The board token used is `cloudflare` (from the assignment prompt's URL). `CITY_HERE` is only used by rule clause 2, which is not built in this layer.
