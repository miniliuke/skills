#!/usr/bin/env python3
"""Thin compatibility wrapper for Claude/AGY CLI delegation (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import locale
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from typing import Any

SCHEMA_VERSION = 1
FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.I | re.S)
MOJIBAKE = ("\ufffd", "锟斤拷")
PERMISSION_WORDS = ("permission", "sandbox", "access denied", "operation not permitted", "blocked")


def decode(data: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", locale.getpreferredencoding(False)):
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            pass
    return data.decode("utf-8", errors="replace")


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 30) -> tuple[int, str, str, int]:
    start = time.monotonic()
    try:
        p = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False,
        )
        return p.returncode, decode(p.stdout), decode(p.stderr), int((time.monotonic() - start) * 1000)
    except subprocess.TimeoutExpired as e:
        return 124, decode(e.stdout or b""), decode(e.stderr or b"") + "\nwrapper: timeout", int((time.monotonic() - start) * 1000)


def cache_root() -> Path:
    if os.name == "nt" and os.environ.get("LOCALAPPDATA"):
        root = Path(os.environ["LOCALAPPDATA"]) / "miniliuke-skills" / "external-agent"
    else:
        root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "miniliuke-skills" / "external-agent"
    root.mkdir(parents=True, exist_ok=True)
    return root


def capabilities(help_text: str) -> dict[str, bool]:
    return {
        "prompt": bool(re.search(r"(^|\s)-p(?:[\s,]|$)", help_text)),
        "output_format": "--output-format" in help_text,
        "mode": "--mode" in help_text,
        "cwd": "--cwd" in help_text,
        "sandbox": "--sandbox" in help_text,
        "dangerous": "--dangerously-skip-permissions" in help_text,
    }


def discover(agent: str, refresh: bool = False) -> dict[str, Any]:
    exe = shutil.which(agent)
    if not exe:
        return {"ok": False, "error": {"code": "cli_not_found", "message": agent}}
    _, vo, ve, _ = run([exe, "--version"], timeout=15)
    version = next((x.strip() for x in (vo or ve).splitlines() if x.strip()), "unknown")
    key = hashlib.sha256(f"{exe}\0{version}".encode()).hexdigest()[:16]
    cache = cache_root() / f"{agent}-{key}.json"
    if cache.exists() and not refresh:
        try:
            info = json.loads(cache.read_text(encoding="utf-8"))
            info["cache_hit"] = True
            return {"ok": True, "cli": info}
        except (OSError, json.JSONDecodeError):
            pass
    _, ho, he, _ = run([exe, "--help"], timeout=15)
    info = {"executable": exe, "version": version, "capabilities": capabilities(ho or he), "cache_hit": False}
    try:
        cache.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass
    return {"ok": True, "cli": info}


def jsonish(text: str) -> Any:
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for line in reversed(text.splitlines()):
        try:
            return json.loads(line.strip())
        except (json.JSONDecodeError, TypeError):
            pass
    if "{" in text and "}" in text:
        try:
            return json.loads(text[text.find("{"): text.rfind("}") + 1])
        except json.JSONDecodeError:
            pass
    return None


def semantic(value: Any) -> tuple[Any, list[str]]:
    if not isinstance(value, str):
        return value, []
    text = value.strip()
    warnings: list[str] = []
    m = FENCE.match(text)
    if m:
        text = m.group(1).strip()
        warnings.append("RESULT_CODE_FENCE_STRIPPED")
    parsed = jsonish(text)
    return (parsed if parsed is not None else text), warnings


def first(d: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if d.get(key) is not None:
            return d[key]
    return None


def runtime_meta(outer: dict[str, Any]) -> dict[str, Any]:
    runtime: dict[str, Any] = {}
    model_usage = first(outer, "modelUsage", "model_usage")
    if isinstance(model_usage, dict):
        models = [str(k) for k in model_usage]
        runtime["actual_model"] = models[0] if len(models) == 1 else models
        runtime["model_usage"] = model_usage
    model = first(outer, "model", "modelName", "model_name", "actual_model")
    if model is not None and "actual_model" not in runtime:
        runtime["actual_model"] = model
    tier = first(outer, "service_tier", "serviceTier", "tier")
    if tier is not None:
        runtime["service_tier"] = tier
    cost = first(outer, "cost_usd", "total_cost_usd", "totalCostUsd", "costUSD", "costUsd")
    if cost is not None:
        try:
            runtime["cost_usd"] = float(cost)
        except (TypeError, ValueError):
            runtime["cost_usd"] = cost
    usage = first(outer, "usage", "tokenUsage", "token_usage")
    if usage is not None:
        runtime["usage"] = usage
    return runtime


def parse_transport(stdout: str) -> tuple[Any, dict[str, Any], list[str]]:
    outer = jsonish(stdout)
    if not isinstance(outer, dict):
        return (stdout.strip() if outer is None else outer), {}, ([] if outer is not None else ["OUTER_JSON_PARSE_FAILED"])
    result, warnings = semantic(outer.get("result", outer))
    meta = {k: outer[k] for k in ("session_id", "sessionId", "duration_ms", "durationMs", "num_turns", "is_error", "error") if k in outer}
    runtime = runtime_meta(outer)
    if runtime:
        meta["runtime"] = runtime
    return result, meta, warnings


def suspicious_strings(value: Any) -> list[str]:
    found: list[str] = []
    def walk(x: Any) -> None:
        if isinstance(x, str) and any(m in x for m in MOJIBAKE):
            found.append(x)
        elif isinstance(x, dict):
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(value)
    return found[:10]


def make_prompt(task: str, mode: str, result_format: str) -> str:
    edit_rule = "Do not edit files." if mode == "read-only" else "Edit only explicitly requested documentation files; do not edit source code."
    out_rule = "Return compact JSON only, without Markdown fences; use UTF-8 paths." if result_format == "json" else "Return a compact result; use UTF-8 paths."
    return f"{task.rstrip()}\n\nWrapper constraints:\n- {edit_rule}\n- {out_rule}"


def build_command(agent: str, cli: dict[str, Any], task: str, args: argparse.Namespace) -> list[str]:
    caps = cli["capabilities"]
    if not caps.get("prompt"):
        raise ValueError(f"{agent} does not advertise -p; adapter update required")
    cmd = [cli["executable"], "-p", make_prompt(task, args.mode, args.result_format)]
    if caps.get("output_format"):
        cmd += ["--output-format", "json"]
    if agent == "agy" and caps.get("mode"):
        cmd += ["--mode=plan" if args.mode == "read-only" else "--mode=accept-edits"]
    if args.permission_mode == "dangerous":
        if agent != "agy" or not args.ack_dangerous_permissions:
            raise ValueError("dangerous mode requires AGY and --ack-dangerous-permissions")
        if not caps.get("dangerous"):
            raise ValueError("installed AGY does not advertise --dangerously-skip-permissions")
        cmd += ["--dangerously-skip-permissions"]
    return cmd


def load_task(args: argparse.Namespace) -> str:
    return args.task if args.task is not None else Path(args.task_file).read_text(encoding="utf-8")


def invoke(args: argparse.Namespace) -> dict[str, Any]:
    d = discover(args.agent, args.refresh_capabilities)
    if not d.get("ok"):
        return {"schema_version": SCHEMA_VERSION, "ok": False, "agent": args.agent, **d}
    cli = d["cli"]
    workdir = Path(args.workdir).expanduser().resolve()
    if not workdir.is_dir():
        return {"schema_version": SCHEMA_VERSION, "ok": False, "agent": args.agent, "error": {"code": "invalid_workdir", "message": str(workdir)}}
    try:
        cmd = build_command(args.agent, cli, load_task(args), args)
    except (OSError, ValueError) as e:
        return {"schema_version": SCHEMA_VERSION, "ok": False, "agent": args.agent, "error": {"code": "wrapper_configuration", "message": str(e)}}

    if args.dry_run:
        preview = cmd[:]
        preview[2] = "<task prompt omitted>"
        return {"schema_version": SCHEMA_VERSION, "ok": True, "agent": args.agent, "dry_run": True, "cli": cli, "workdir": str(workdir), "command_preview": preview}

    rc, stdout, stderr, elapsed = run(cmd, workdir, args.timeout)
    result, transport, warnings = parse_transport(stdout)
    runtime = transport.pop("runtime", {}) if transport else {}
    suspects = suspicious_strings(result)
    if suspects:
        warnings.append("PATH_OR_TEXT_ENCODING_SUSPECT")
    cost = runtime.get("cost_usd") if isinstance(runtime, dict) else None
    if args.max_cost_usd is not None and isinstance(cost, (int, float)) and cost > args.max_cost_usd:
        warnings.append("COST_BUDGET_EXCEEDED")

    permission_blocked = rc != 0 and any(w in f"{stderr}\n{stdout}".lower() for w in PERMISSION_WORDS)
    error = None
    if rc != 0:
        error = {"code": "permission_blocked" if permission_blocked else "cli_failed", "message": stderr.strip() or f"exit {rc}"}
        if permission_blocked and args.agent == "agy" and cli["capabilities"].get("dangerous"):
            error.update({"retry_hint": "dangerous_permission_mode_available", "requires_explicit_authorization": True})

    return {
        "schema_version": SCHEMA_VERSION, "ok": rc == 0, "agent": args.agent,
        "cli": {"executable": cli["executable"], "version": cli["version"], "capabilities_cache_hit": cli.get("cache_hit", False)},
        "execution": {"workdir": str(workdir), "exit_code": rc, "duration_ms": elapsed, "mode": args.mode, "permission_mode": args.permission_mode},
        "runtime": runtime, "transport": transport, "result": result,
        "warnings": sorted(set(warnings)), "encoding_suspects": suspects, "error": error,
    }


def health(args: argparse.Namespace) -> dict[str, Any]:
    d = discover(args.agent, args.refresh_capabilities)
    return {"schema_version": SCHEMA_VERSION, "ok": bool(d.get("ok")), "agent": args.agent, "health": "local_only", "cli": d.get("cli"), "error": d.get("error")}


def self_test() -> dict[str, Any]:
    sample = json.dumps({
        "result": "```json\n{\"status\":\"ok\",\"path\":\"测试.txt\"}\n```",
        "modelUsage": {"deepseek-v4-flash": {"inputTokens": 10, "outputTokens": 5}},
        "total_cost_usd": 0.215, "service_tier": "standard",
    }, ensure_ascii=False)
    result, meta, warnings = parse_transport(sample)
    runtime = meta.get("runtime", {})
    ok = result.get("status") == "ok" and runtime.get("actual_model") == "deepseek-v4-flash" and runtime.get("cost_usd") == 0.215
    return {"schema_version": SCHEMA_VERSION, "ok": ok, "self_test": "passed" if ok else "failed", "result": result, "runtime": runtime, "warnings": warnings}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Normalize Claude/AGY CLI invocation and output")
    p.add_argument("agent", nargs="?", choices=("claude", "agy"))
    p.add_argument("--task"); p.add_argument("--task-file")
    p.add_argument("--workdir", default=".")
    p.add_argument("--mode", choices=("read-only", "docs-edit"), default="read-only")
    p.add_argument("--result-format", choices=("json", "text"), default="json")
    p.add_argument("--permission-mode", choices=("normal", "dangerous"), default="normal")
    p.add_argument("--ack-dangerous-permissions", action="store_true")
    p.add_argument("--max-cost-usd", type=float); p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--health", action="store_true", help="local-only; never calls a model")
    p.add_argument("--dry-run", action="store_true", help="validate/build command; never calls a model")
    p.add_argument("--refresh-capabilities", action="store_true")
    p.add_argument("--self-test", action="store_true"); p.add_argument("--pretty", action="store_true")
    return p


def main() -> int:
    p = parser(); args = p.parse_args()
    if args.self_test:
        payload = self_test()
    else:
        if not args.agent: p.error("agent is required unless --self-test is used")
        if args.health:
            payload = health(args)
        else:
            if bool(args.task) == bool(args.task_file): p.error("provide exactly one of --task or --task-file")
            payload = invoke(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
