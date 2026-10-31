# Action surface: three ways to judge posting 8335469 against CONTRACT.md

Date: 2026-10-31. Posting 8335469 is "Territory Account Executive, Saskatchewan / Manitoba", `posting.location.name` "Remote", from the live response `evidence/raw/20261031T182100Z_live.json`.

| # | Surface | Evidence |
|---|---|---|
| 1 | **Chat paste**: Meena, by hand in claude.ai | `evidence/surface_chat_prompt.txt`, `evidence/surface_chat_2026-10-31.txt` |
| 2 | **File read**: `claude -p` with a read-only tool, run by `scripts/surface_file_read.py` | `evidence/surface_file_posting.json`, `evidence/surface_file_prompt.txt`, `evidence/surface_file_output.json` |
| 3 | **Agent**: the full pipeline in `agent/run.py` | `evidence/runs/20261031T182105Z_live-vs-SEEDED-baseline_verdicts.json`, `evidence/claude_calls.jsonl` |

The agent was not re-run for this report. Its verdicts on 8335469 are the ones it produced on 2026-10-31 at 18:39Z (`--rejudge` of run 2). A fresh agent run would fetch the live board and overwrite `state/seen_ids.json`.

## 1. Chat paste

The prompt contains the contract's rule text, `resume.personal.location = "Boston, MA"`, and three posting fields typed in by hand: `posting.id`, `posting.title`, `posting.location.name`. The response file records: `claude.ai fresh chat, 2026-10-31, <3.43 pm>, model: <what the selector showed>`. The time and model fields still contain those placeholders, so the model used is **not recorded**.

| | |
|---|---|
| **Can read** | The pasted text. Anything else claude.ai had enabled in that chat (search, connectors, memory) is not recorded in the evidence files. |
| **Can write** | Nothing on this machine. The conversation is stored in the claude.ai account. |
| **Network** | The browser sends the pasted text to claude.ai. |
| **Authority / credentials** | Meena's claude.ai login. No repo, filesystem or API key. |
| **What could go wrong** | (a) **Transcription:** the posting fields are copied by hand, and nothing checks them against the raw response. (b) **No provenance:** the model and time were not filled in (the placeholders above), so the result cannot be tied to a model. (c) **Fails the contract:** the justification cites only `posting.title`. Run through `agent/validate.py` it fails with `['no resume field cited']`; CONTRACT.md requires a résumé field too. (d) **No checks or log:** no validator or retry runs, and the only record is the hand-saved text file. (e) **Less to see:** only 3 posting fields are visible, so the model cannot see `posting.content`. |

## 2. File read

`scripts/surface_file_read.py` saved the posting unmodified (the full Greenhouse object) to `evidence/surface_file_posting.json`. It then ran `claude -p` in a fresh temp directory containing only a copy of that file; `temp_dir_listing` and matching sha256 values are recorded in the output. Settings:

- **Tools:** `--tools Read --allowedTools Read --permission-mode dontAsk --restricted --strict-mcp-config --setting-sources "" --no-session-persistence`.
- **System prompt:** `prompts/system_v1.txt`.
- **User prompt:** `evidence/surface_file_prompt.txt`, the chat prompt with only the three pasted posting lines replaced by a pointer to the file (`diff`: lines 14-16 become one line).
- **Model:** `claude-sonnet-5-5` was requested (default, `JUDGE_MODEL` not set) and reported.
- **What it did:** 2 turns; 1 tool call, `Read` of the temp copy; `permission_denials: []`.

| | |
|---|---|
| **Can read** | Files via the `Read` tool. Its working directory held only the posting copy. Whether `dontAsk` blocks a `Read` of an absolute path outside that directory was **not tested here**. |
| **Can write** | Nothing: no Write, Edit, Bash or other code-running tool was available. The calling script, not the model, wrote the evidence files. |
| **Network** | The `claude` CLI sends the prompt, the file contents it reads and its replies to Anthropic. The model had no WebFetch, WebSearch or MCP tools. |
| **Authority / credentials** | The Claude Code login on this machine (`ANTHROPIC_API_KEY` is not set). |
| **What could go wrong** | (a) **Injection:** `posting.content` is employer-written HTML, and the model reads it in full. A prompt injection there can at most request more `Read` calls, but if the working directory were the repo instead of a temp directory, those reads could reach `labels/postings_20.csv` (including held-out labels), `evidence/claude_calls.jsonl` and `resume/persona.json`. (b) **Unchecked output:** the output is free text, not the JSON contract, so no validator ran in the loop; the check below was run afterwards. (c) **Possible guessing:** a model could answer without reading the file. Here the transcript shows the `Read` call. |

## 3. Agent (`agent/run.py`)

| | |
|---|---|
| **Can read** | `resume/persona.json`, `state/seen_ids.json`, `prompts/*`, saved raw responses (`--from-file`, `--rejudge`). |
| **Can write** | `evidence/raw/*` (raw responses), `evidence/runs/*` (run and verdict files), `state/seen_ids.json`, `evidence/claude_calls.jsonl`. |
| **Network** | HTTPS GET to `boards-api.greenhouse.io` (the only allow-listed host). Claude calls through `claude -p` with no tools, or through the Anthropic API if `ANTHROPIC_API_KEY` is set. Every Claude call sends the full persona and the full posting. |
| **Authority / credentials** | None for Greenhouse (public board API). The Claude Code login on this machine, or an Anthropic API key. Filesystem write access to the repo. |
| **What could go wrong** | Concrete, from the code and from this project's history: (a) **Redirects:** the allow-list checks only the requested URL. `fetch.py` calls `requests.get(url, timeout=30)`, which follows redirects by default, and does not check the final `resp.url`, so a redirect to another host would be fetched and saved. (b) **State written too early:** state is saved (`run.py:64`) before the judges run (`run.py:87`). If judging fails partway, those postings are already marked seen and will not be reported as new again. (c) **Validator gap:** a nonexistent indexed path in justification text, e.g. `resume.experience.7.title`, passes both `agent/validate.py` and `agent/validator.py` (tested on 2026-10-31: both returned `[]`). The text regex stops at the numeric segment and checks only `resume.experience`. (d) **Evidence contamination:** the write surface includes evidence files. This already happened once: a test wrote a fake call line into `evidence/claude_calls.jsonl` (found and removed before the real calls; guard test added). (e) **Truth not checked:** the validator checks that cited fields exist, not that what the justification says about them is true. |

## Verdicts on 8335469

| Source | Criteria applied | Verdict | Fields cited | `agent/validate.py` on the justification |
|---|---|---|---|---|
| Rule judge (RECORD), agent | CONTRACT.md rule, deterministic | not_relevant: clause 1 failed; 2, 3 passed | `posting.title`, `posting.location.name`, `resume.personal.location` | `[]` (passes) |
| 1. Chat paste (JUDGMENT) | CONTRACT.md rule (pasted) | not_relevant: "fails clause 1" | `posting.title` | `['no resume field cited']` |
| 2. File read (JUDGMENT) | CONTRACT.md rule (same text) | not_relevant: clause 1 failed; 2, 3 passed | `posting.title`, `posting.location.name`, `resume.personal.location` | `[]` (passes) |
| 3. Agent, Claude judge (JUDGMENT) | `prompts/judge_v1.txt` (LABELING.md criteria, not the contract rule) | not_relevant | `posting.content`, `posting.metadata`, `resume.experience(.0.title)`, `resume.skills.languages` | `[]` (passes) |

All four say `not_relevant`. Surfaces 1 and 2 apply the same rule as the rule judge, and both name clause 1 as the failing clause, matching it. Surface 2 also reports clauses 2 and 3 as passed, which matches the rule judge's result for every clause. The agent's Claude judge answers a different question (LABELING.md criteria via judge_v1), so its agreement is on the verdict only, not on the reasoning. One posting is one case: this table shows that the surfaces agree on 8335469, not that they agree in general.

## Least autonomy that suffices

> **DRAFT: Meena will rewrite this section.**
>
> The task "judge posting 8335469 against CONTRACT.md" is fully specified by the rule, and the rule is deterministic: `agent/rule_judge.py` applies it with no model, no network and no write access, reading two inputs. For this task that is the least autonomy that suffices, and the three model surfaces add nothing to the verdict except a second opinion that is itself a JUDGMENT.
>
> If a model judgment is wanted (for example, the LABELING.md criteria, which need `posting.content`), the file-read surface is enough. It sees the whole posting (unlike the chat paste), leaves a transcript showing what it read, and cannot write or browse. Its one real exposure is what sits in its working directory, which is why it ran in a temp directory with a single file.
>
> The agent's extra authority is network fetch, state writes and evidence writes. That authority is needed for the job of watching the board for new postings, not for judging a posting. Each extra capability brought a concrete risk above: redirects past the allow-list, state committed before judging, evidence written by a test. The chat paste has the least machine authority but the weakest record: a hand-copied input, a model that was not recorded, and a justification that fails the contract's validator.
>
> So: grant network and write access only to the fetch-and-state step, and run judging with read-only access to exactly the inputs it needs.
