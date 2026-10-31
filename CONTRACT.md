# CONTRACT — Job-Search Agent 1

Written by Meena on 2026-10-31, before any code was generated.

## In
- Board: Greenhouse board token `<token>`, fetched from host `boards-api.greenhouse.io` (the only host on the allow-list).
- Résumé: one fictional persona JSON at `resume/persona.json`, copied from the-reallocation-engine `search/examples/<file>`. It must contain the fields `<field-for-target-titles>`, `<field-for-location>`, `<field-for-years-or-level>`, `<field-for-skills>`. If any is missing, the agent refuses to run.
- State: `state/seen_ids.json` from the previous run (absent on the baseline run).

## Out (per new posting)
- `posting_id`, `rule_verdict` (relevant | not_relevant), `rule_justification`, `claude_verdict`, `claude_justification`.
- Every justification names at least one résumé field and at least one posting field by exact key path (e.g. `resume.<field>`, `posting.title`, `posting.location.name`), and every named field exists in the inputs.
- The rule verdict is labeled RECORD. The Claude verdict is labeled JUDGMENT (model output, not fact).

## Refuses
- Fetching any host not on the allow-list.
- Running on a résumé that is not the fictional persona (refuses any email not ending in @example.com and any phone not using 555).
- Printing or committing a real résumé.
- Presenting a Claude verdict as fact, or emitting a Claude verdict that fails the validator.
- Applying, emailing, messaging, or logging in anywhere.

## The rule (a TA can apply this by hand)
A posting is RELEVANT if and only if all three hold:
1. `posting.title` contains, case-insensitive, at least one keyword from `resume.<target-titles-field>` (<list them here>).
2. `posting.location.name` contains `<persona city>` or the word "Remote".
3. `posting.title` does not contain Senior, Sr., Staff, Principal, Lead, Director, Head, or Manager <unless persona has ≥ N years — decide>.
Otherwise NOT RELEVANT. The justification names which clause failed, or all three that passed.

## Wrong versions my tests must catch
1. Misaligned labels: verdicts paired with the wrong posting (e.g. an off-by-one zip). Caught by a test that checks every justification quotes the title belonging to its own `posting_id`.
2. Empty or fake citation: a justification that names no field, or names a field that does not exist in the résumé or posting. Caught by a validator test.
3. <optional third: "new" computed by title instead of id, or the baseline run reporting postings as new.>

## What a failure looks like
2026-10-31: <one sentence, e.g. "Failure is any run that reports a posting id already in the previous state as new, or any verdict whose justification cites a field that does not exist in its inputs.">