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

SCHEMA_VERSION = 2
FENCE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.I | re.S)
MOJIBAKE = ("\ufffd", "锟斤拷")
PERMISSION_WORDS = ("permission", "sandbox", "access denied", "operation not permitted", "blocked")
RUNTIME_ACCOUNTING_FIELDS = ("actual_model", "cost_usd")


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
            cmd,
            cwd=str(cwd) if cwd else None,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return p.returncode, decode(p.stdout), decode(p.stderr), int((time.monotonic() - start) * 1000)
    except subprocess.TimeoutExpired as e:
        return (
            124,
            decode(e.stdout or b""),
            decode(e.stderr or b"") + "\nwrapper: timeout",
            int((time.monotonic() - start) * 1000),
        )


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
    info = {
        "executable": exe,
        "version": version,
        "capabilities": capabilities(ho or he),
        "cache_hit": False,
    }
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


def semantic(value: Any) -> tuple[Any, list[str], bool]:
    """Return normalized result, warnings, and whether a string payload parsed as JSON."""
    if not isinstance(value, str):
        return value, [], True
    text = value.strip()
    warnings: list[str] = []
    m = FENCE.match(text)
    if m:
        text = m.group(1).strip()
        warnings.append("RESULT_CODE_FENCE_STRIPPED")
    parsed = jsonish(text)
    if parsed is None:
        return text, warnings, False
    return parsed, warnings, True


def first(d: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if d.get(key) is not None:
            return d[key]
    return None


def empty_runtime() -> dict[str, Any]:
    return {
        "metadata_status": "missing",
        "actual_model": None,
        "service_tier": None,
        "cost_usd": None,
        "usage": None,
        "missing": list(RUNTIME_ACCOUNTING_FIELDS),
    }


def runtime_meta(outer: dict[str, Any]) -> dict[str, Any]:
    runtime = empty_runtime()
    model_usage = first(outer, "modelUsage", "model_usage")
    if isinstance(model_usage, dict):
        models = [str(k) for k in model_usage]
        runtime["actual_model"] = models[0] if len(models) == 1 else models
        runtime["model_usage"] = model_usage
    model = first(outer, "model", "modelName", "model_name", "actual_model")
    if model is not None and runtime["actual_model"] is None:
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

    missing = [field for field in RUNTIME_ACCOUNTING_FIELDS if runtime.get(field) is None]
    runtime["missing"] = missing
    reported = [
        field
        for field in ("actual_model", "service_tier", "cost_usd", "usage", "model_usage")
        if runtime.get(field) is not None
    ]
    runtime["reported_fields"] = reported
    if not reported:
        runtime["metadata_status"] = "missing"
    elif missing:
        runtime["metadata_status"] = "partial"
    else:
        runtime["metadata_status"] = "complete"
    return runtime


def parse_transport(stdout: str) -> tuple[Any, dict[str, Any], list[str], bool]:
    outer = jsonish(stdout)
    if not isinstance(outer, dict):
        result = stdout.strip() if outer is None else outer
        return result, {"runtime": empty_runtime()}, ([] if outer is not None else ["OUTER_JSON_PARSE_FAILED"]), outer is not None

    result, warnings, semantic_json = semantic(outer.get("result", outer))
    meta = {
        k: outer[k]
        for k in ("session_id", "sessionId", "duration_ms", "durationMs", "num_turns", "is_error", "error")
        if k in outer
    }
    meta["runtime"] = runtime_meta(outer)
    return result, meta, warnings, semantic_json


def dotted_value(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def parse_required_values(items: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"--require-value must be FIELD=VALUE: {item}")
        field, raw = item.split("=", 1)
        field = field.strip()
        if not field:
            raise ValueError(f"--require-value field is empty: {item}")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        parsed[field] = value
    return parsed


def validate_result(
    result: Any,
    expected_type: str,
    required_fields: list[str],
    required_values: dict[str, Any],
    semantic_json: bool,
) -> tuple[bool, dict[str, Any], list[str]]:
    warnings: list[str] = []
    type_ok = True

    if expected_type == "object":
        type_ok = isinstance(result, dict)
    elif expected_type == "array":
        type_ok = isinstance(result, list)
    elif expected_type == "json":
        type_ok = semantic_json and not isinstance(result, str)
    elif expected_type == "text":
        type_ok = isinstance(result, str)

    if not type_ok:
        warnings.append("RESULT_SCHEMA_UNEXPECTED")

    missing_fields: list[str] = []
    if required_fields:
        if isinstance(result, dict):
            for field in required_fields:
                exists, _ = dotted_value(result, field)
                if not exists:
                    missing_fields.append(field)
        else:
            missing_fields = list(required_fields)
        if missing_fields:
            warnings.append("RESULT_REQUIRED_FIELDS_MISSING")

    value_mismatches: list[dict[str, Any]] = []
    if required_values:
        if isinstance(result, dict):
            for field, expected in required_values.items():
                exists, actual = dotted_value(result, field)
                if not exists or actual != expected:
                    value_mismatches.append(
                        {
                            "field": field,
                            "expected": expected,
                            "actual": actual if exists else None,
                            "missing": not exists,
                        }
                    )
        else:
            value_mismatches = [
                {"field": field, "expected": expected, "actual": None, "missing": True}
                for field, expected in required_values.items()
            ]
        if value_mismatches:
            warnings.append("RESULT_REQUIRED_VALUE_MISMATCH")

    contract = {
        "valid": type_ok and not missing_fields and not value_mismatches,
        "expected_type": expected_type,
        "required_fields": required_fields,
        "required_values": required_values,
        "missing_fields": missing_fields,
        "value_mismatches": value_mismatches,
        "actual_type": type(result).__name__,
    }
    return contract["valid"], contract, warnings


def suspicious_strings(value: Any) -> list[str]:
    found: list[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, str) and any(m in x for m in MOJIBAKE):
            found.append(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(value)
    return found[:10]


def make_prompt(
    task: str,
    mode: str,
    result_format: str,
    expected_type: str,
    required_fields: list[str],
    required_values: dict[str, Any],
) -> str:
    edit_rule = (
        "Do not edit files."
        if mode == "read-only"
        else "Edit only explicitly requested documentation files; do not edit source code."
    )
    if result_format == "json":
        shape = {
            "object": "a compact JSON object",
            "array": "a compact JSON array",
            "json": "compact valid JSON",
        }.get(expected_type, "compact valid JSON")
        out_rule = f"Return {shape} only, without Markdown fences; use UTF-8 paths."
        if required_fields:
            out_rule += " Required fields: " + ", ".join(required_fields) + "."
        if required_values:
            out_rule += " Required values: " + ", ".join(
                f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in required_values.items()
            ) + "."
    else:
        out_rule = "Return a compact text result; use UTF-8 paths."
    return f"{task.rstrip()}\n\nWrapper constraints:\n- {edit_rule}\n- {out_rule}"


def build_command(agent: str, cli: dict[str, Any], task: str, args: argparse.Namespace) -> list[str]:
    caps = cli["capabilities"]
    if not caps.get("prompt"):
        raise ValueError(f"{agent} does not advertise -p; adapter update required")
    cmd = [
        cli["executable"],
        "-p",
        make_prompt(
            task,
            args.mode,
            args.result_format,
            expected_result_type(args),
            args.require_field,
            parse_required_values(args.require_value),
        ),
    ]
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


def expected_result_type(args: argparse.Namespace) -> str:
    if args.expect_result:
        return args.expect_result
    return "object" if args.result_format == "json" else "text"


def load_task(args: argparse.Namespace) -> str:
    return args.task if args.task is not None else Path(args.task_file).read_text(encoding="utf-8")


def invoke(args: argparse.Namespace) -> dict[str, Any]:
    d = discover(args.agent, args.refresh_capabilities)
    if not d.get("ok"):
        return {"schema_version": SCHEMA_VERSION, "ok": False, "agent": args.agent, **d}
    cli = d["cli"]
    workdir = Path(args.workdir).expanduser().resolve()
    if not workdir.is_dir():
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "agent": args.agent,
            "error": {"code": "invalid_workdir", "message": str(workdir)},
        }
    try:
        cmd = build_command(args.agent, cli, load_task(args), args)
    except (OSError, ValueError) as e:
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": False,
            "agent": args.agent,
            "error": {"code": "wrapper_configuration", "message": str(e)},
        }

    if args.dry_run:
        preview = cmd[:]
        preview[2] = "<task prompt omitted>"
        return {
            "schema_version": SCHEMA_VERSION,
            "ok": True,
            "agent": args.agent,
            "dry_run": True,
            "cli": cli,
            "workdir": str(workdir),
            "result_contract": {
                "expected_type": expected_result_type(args),
                "required_fields": args.require_field,
                "required_values": parse_required_values(args.require_value),
            },
            "command_preview": preview,
        }

    rc, stdout, stderr, elapsed = run(cmd, workdir, args.timeout)
    result, transport, warnings, semantic_json = parse_transport(stdout)
    runtime = transport.pop("runtime", empty_runtime())
    result_valid, result_contract, contract_warnings = validate_result(
        result,
        expected_result_type(args),
        args.require_field,
        parse_required_values(args.require_value),
        semantic_json,
    )
    warnings.extend(contract_warnings)

    if args.agent == "claude":
        if runtime.get("actual_model") is None:
            warnings.append("RUNTIME_MODEL_METADATA_MISSING")
        if runtime.get("cost_usd") is None:
            warnings.append("RUNTIME_COST_METADATA_MISSING")

    suspects = suspicious_strings(result)
    if suspects:
        warnings.append("PATH_OR_TEXT_ENCODING_SUSPECT")

    cost = runtime.get("cost_usd") if isinstance(runtime, dict) else None
    if args.max_cost_usd is not None and isinstance(cost, (int, float)) and cost > args.max_cost_usd:
        warnings.append("COST_BUDGET_EXCEEDED")

    permission_blocked = rc != 0 and any(w in f"{stderr}\n{stdout}".lower() for w in PERMISSION_WORDS)
    transport_failed = transport.get("is_error") is True or bool(transport.get("error"))
    error = None
    if rc != 0:
        error = {
            "code": "permission_blocked" if permission_blocked else "cli_failed",
            "message": stderr.strip() or f"exit {rc}",
        }
        if permission_blocked and args.agent == "agy" and cli["capabilities"].get("dangerous"):
            error.update(
                {
                    "retry_hint": "dangerous_permission_mode_available",
                    "requires_explicit_authorization": True,
                }
            )
    elif transport_failed:
        error = {
            "code": "transport_error",
            "message": str(transport.get("error") or "CLI transport reported is_error=true"),
        }
    elif not result_valid:
        error = {
            "code": "result_contract_failed",
            "message": "CLI exited successfully but result did not satisfy the declared result contract",
            "details": result_contract,
        }

    ok = rc == 0 and not transport_failed and result_valid
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": ok,
        "agent": args.agent,
        "cli": {
            "executable": cli["executable"],
            "version": cli["version"],
            "capabilities_cache_hit": cli.get("cache_hit", False),
        },
        "execution": {
            "workdir": str(workdir),
            "exit_code": rc,
            "duration_ms": elapsed,
            "mode": args.mode,
            "permission_mode": args.permission_mode,
        },
        "runtime": runtime,
        "transport": transport,
        "result_contract": result_contract,
        "result": result,
        "warnings": sorted(set(warnings)),
        "encoding_suspects": suspects,
        "error": error,
    }


def health(args: argparse.Namespace) -> dict[str, Any]:
    d = discover(args.agent, args.refresh_capabilities)
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": bool(d.get("ok")),
        "agent": args.agent,
        "health": "local_only",
        "cli": d.get("cli"),
        "error": d.get("error"),
    }


def self_test() -> dict[str, Any]:
    failures: list[str] = []

    sample = json.dumps(
        {
            "result": "```json\n{\"status\":\"ok\",\"path\":\"测试.txt\"}\n```",
            "modelUsage": {"deepseek-v4-flash": {"inputTokens": 10, "outputTokens": 5}},
            "total_cost_usd": 0.215,
            "service_tier": "standard",
        },
        ensure_ascii=False,
    )
    result, meta, warnings, semantic_json = parse_transport(sample)
    runtime = meta.get("runtime", {})
    valid, contract, contract_warnings = validate_result(
        result,
        "object",
        ["status"],
        {"status": "ok"},
        semantic_json,
    )
    if not valid or result.get("status") != "ok":
        failures.append("valid_object_contract")
    if runtime.get("actual_model") != "deepseek-v4-flash" or runtime.get("cost_usd") != 0.215:
        failures.append("runtime_metadata")
    if "RESULT_CODE_FENCE_STRIPPED" not in warnings:
        failures.append("fence_warning")

    plain = json.dumps({"result": "plain text"})
    result2, meta2, _, semantic_json2 = parse_transport(plain)
    valid2, _, warnings2 = validate_result(result2, "object", [], {}, semantic_json2)
    if valid2 or "RESULT_SCHEMA_UNEXPECTED" not in warnings2:
        failures.append("unexpected_string_schema")
    runtime2 = meta2.get("runtime", {})
    if runtime2.get("metadata_status") != "missing" or set(runtime2.get("missing", [])) != set(RUNTIME_ACCOUNTING_FIELDS):
        failures.append("missing_runtime_metadata")

    valid3, contract3, warnings3 = validate_result(
        {"status": "ok"},
        "object",
        ["status", "findings"],
        {},
        True,
    )
    if valid3 or contract3.get("missing_fields") != ["findings"] or "RESULT_REQUIRED_FIELDS_MISSING" not in warnings3:
        failures.append("required_fields")

    valid4, contract4, warnings4 = validate_result(
        {"status": "failed"},
        "object",
        ["status"],
        {"status": "ok"},
        True,
    )
    if valid4 or not contract4.get("value_mismatches") or "RESULT_REQUIRED_VALUE_MISMATCH" not in warnings4:
        failures.append("required_values")

    ok = not failures
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": ok,
        "self_test": "passed" if ok else "failed",
        "failures": failures,
        "result": result,
        "runtime": runtime,
        "result_contract": contract,
        "warnings": sorted(set(warnings + contract_warnings)),
    }


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Normalize Claude/AGY CLI invocation and output")
    p.add_argument("agent", nargs="?", choices=("claude", "agy"))
    p.add_argument("--task")
    p.add_argument("--task-file")
    p.add_argument("--workdir", default=".")
    p.add_argument("--mode", choices=("read-only", "docs-edit"), default="read-only")
    p.add_argument("--result-format", choices=("json", "text"), default="json")
    p.add_argument(
        "--expect-result",
        choices=("object", "array", "json", "text"),
        help="expected semantic result type; defaults to object for json and text for text",
    )
    p.add_argument(
        "--require-field",
        action="append",
        default=[],
        help="required dotted field in JSON object result; repeat for multiple fields",
    )
    p.add_argument(
        "--require-value",
        action="append",
        default=[],
        metavar="FIELD=VALUE",
        help="required dotted field value; VALUE is parsed as JSON when possible",
    )
    p.add_argument("--permission-mode", choices=("normal", "dangerous"), default="normal")
    p.add_argument("--ack-dangerous-permissions", action="store_true")
    p.add_argument("--max-cost-usd", type=float)
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--health", action="store_true", help="local-only; never calls a model")
    p.add_argument("--dry-run", action="store_true", help="validate/build command; never calls a model")
    p.add_argument("--refresh-capabilities", action="store_true")
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--pretty", action="store_true")
    return p


def main() -> int:
    p = parser()
    args = p.parse_args()
    if args.self_test:
        payload = self_test()
    else:
        if not args.agent:
            p.error("agent is required unless --self-test is used")
        if args.health:
            payload = health(args)
        else:
            if bool(args.task) == bool(args.task_file):
                p.error("provide exactly one of --task or --task-file")
            if args.result_format == "text" and (args.require_field or args.require_value):
                p.error("--require-field/--require-value require --result-format json")
            try:
                parse_required_values(args.require_value)
            except ValueError as e:
                p.error(str(e))
            payload = invoke(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
