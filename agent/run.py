"""CLI: python -m agent.run --label live | --from-file <path> --label <label>"""

import argparse
import json
import sys
from pathlib import Path

from agent import fetch, persona, state

RUNS_DIR = Path("evidence/runs")


def run(label: str, from_file: Path | None, state_path: Path, persona_path: Path,
        runs_dir: Path) -> dict:
    fetch.safe_label(label)
    persona.load_persona(persona_path)  # raises PersonaError: refuse before any fetch

    source = from_file if from_file else fetch.fetch_board(label)
    board = json.loads(Path(source).read_text())

    ids = state.posting_ids(board)
    seen = state.load_seen(state_path)
    new = state.new_ids(ids, seen)
    state.save_seen(ids, state_path)

    jobs = {j["id"]: j for j in board["jobs"]}
    result = {
        "label": label,
        "source": str(source),
        "fetched_live": from_file is None,
        "run_at_utc": fetch.utc_timestamp(),
        "baseline": seen is None,
        "previous_state_count": None if seen is None else len(seen),
        "postings_in_response": len(ids),
        "new_count": len(new),
        "new_postings": [
            {"id": i, "title": jobs[i]["title"],
             "location": (jobs[i].get("location") or {}).get("name")}
            for i in new
        ],
    }
    runs_dir.mkdir(parents=True, exist_ok=True)
    out = runs_dir / f"{result['run_at_utc']}_{label}.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    result["output"] = str(out)
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agent.run")
    p.add_argument("--label", required=True)
    p.add_argument("--from-file", type=Path, help="run against a saved response; no fetch")
    p.add_argument("--state", type=Path, default=state.STATE_PATH)
    p.add_argument("--persona", type=Path, default=persona.PERSONA_PATH)
    p.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    a = p.parse_args(argv)
    try:
        r = run(a.label, a.from_file, a.state, a.persona, a.runs_dir)
    except (persona.PersonaError, fetch.HostNotAllowedError) as e:
        print(e, file=sys.stderr)
        return 2
    kind = "BASELINE" if r["baseline"] else "RUN"
    print(f"{kind} label={r['label']} source={r['source']} "
          f"postings={r['postings_in_response']} new={r['new_count']}")
    for j in r["new_postings"]:
        print(f"  NEW {j['id']}  {j['title']}  [{j['location']}]")
    print(f"wrote {r['output']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
