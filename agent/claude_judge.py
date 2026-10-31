"""Claude judge: one fresh, stateless call per posting. Output kind=JUDGMENT (model output, not fact).

Backend: Anthropic SDK if ANTHROPIC_API_KEY is set, else `claude -p --output-format json`.
Model: env JUDGE_MODEL, default claude-sonnet-5-5; recorded in every output and log line.
"""

import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from agent.validator import validate_claude_output

DEFAULT_MODEL = "claude-sonnet-5-5"
PROMPT_PATH = Path("prompts/judge_v1.txt")
CALLS_LOG = Path("evidence/claude_calls.jsonl")
SYSTEM = "You are a strict classifier. Follow the user's instructions exactly."
MAX_ATTEMPTS = 2  # first call + one retry
JUDGMENT_LABEL = "JUDGMENT (model output, not fact)"


def judge_model() -> tuple[str, str]:
    m = os.environ.get("JUDGE_MODEL")
    return (m, "env JUDGE_MODEL") if m else (DEFAULT_MODEL, "default (JUDGE_MODEL not set)")


def backend() -> str:
    return "anthropic-sdk" if os.environ.get("ANTHROPIC_API_KEY") else "claude-cli"


def build_prompt(template: str, posting: dict, persona: dict) -> str:
    return (template
            .replace("{{PERSONA_JSON}}", json.dumps(persona, indent=2, ensure_ascii=False))
            .replace("{{POSTING_JSON}}", json.dumps(posting, indent=2, ensure_ascii=False))
            .replace("{{POSTING_ID}}", str(posting["id"])))


def call_sdk(prompt: str, model: str) -> tuple[str, dict]:
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model=model, max_tokens=1024, system=SYSTEM,
        messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in msg.content if b.type == "text")
    return text, {"model_reported": [msg.model], "stop_reason": msg.stop_reason}


def call_cli(prompt: str, model: str) -> tuple[str, dict]:
    cmd = ["claude", "-p", "--output-format", "json", "--model", model,
           "--tools", "", "--no-session-persistence", "--strict-mcp-config",
           "--setting-sources", "", "--system-prompt", SYSTEM]
    with tempfile.TemporaryDirectory() as cwd:  # no project context leaks into the call
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                              cwd=cwd, timeout=300)
    try:
        envelope = json.loads(proc.stdout)
    except ValueError:
        return proc.stdout + proc.stderr, {"cli_returncode": proc.returncode,
                                           "cli_envelope": "unparseable"}
    return envelope.get("result", ""), {
        "model_reported": sorted(envelope.get("modelUsage", {})),
        "cli_is_error": envelope.get("is_error"),
        "session_id": envelope.get("session_id"),
    }


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def judge(posting: dict, persona: dict, *, call=None, prompt_path: Path | None = None,
          log_path: Path | None = None) -> dict:
    prompt_path = prompt_path or PROMPT_PATH
    log_path = log_path or CALLS_LOG
    model, model_source = judge_model()
    if call is None:
        call = call_sdk if backend() == "anthropic-sdk" else call_cli
        be = backend()
    else:
        be = "injected"
    prompt = build_prompt(prompt_path.read_text(), posting, persona)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    raws, all_errors = [], []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        raw, meta = call(prompt, model)
        parsed, errors = validate_claude_output(raw, posting, persona)
        with log_path.open("a") as f:
            f.write(json.dumps({
                "ts_utc": _now(), "model": model, "model_source": model_source,
                "backend": be, "prompt_file": prompt_path.name,
                "posting_id": posting["id"], "attempt": attempt,
                "raw_response": raw,
                "validator": {"ok": not errors, "errors": errors},
                **meta,
            }, ensure_ascii=False) + "\n")
        raws.append(raw)
        all_errors.append(errors)
        if parsed is not None:
            break

    base = {"posting_id": posting["id"], "kind": "JUDGMENT", "label": JUDGMENT_LABEL,
            "model": model, "model_source": model_source, "backend": be,
            "prompt_file": prompt_path.name, "attempts": len(raws)}
    if parsed is None:
        return {**base, "verdict": "INVALID", "justification": None,
                "resume_fields": [], "posting_fields": [],
                "raw_text": raws, "validator_errors": all_errors}
    return {**base, "verdict": parsed["verdict"], "justification": parsed["justification"],
            "resume_fields": parsed["resume_fields"], "posting_fields": parsed["posting_fields"],
            "validator_errors": all_errors}
