#!/usr/bin/env python3
"""Small, standard-library integration phase runner. See references/runner.md."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid

PHASES = ('preflight', 'setup', 'ready', 'seed', 'collect', 'cleanup')


def validate(config):
    def steps(items):
        if not isinstance(items, list):
            raise ValueError('steps must be a list')
        names = set()
        for step in items:
            if not isinstance(step, dict):
                raise ValueError('step must be an object')
            name = step.get('id', '')
            if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', name) or name in names:
                raise ValueError('step IDs must be unique safe names within each phase/case')
            names.add(name)
            cmd = step.get('cmd')
            if not isinstance(cmd, list) or not cmd or not all(isinstance(v, str) and v for v in cmd):
                raise ValueError('cmd must be a nonempty string argv array')
            timeout = step.get('timeout', 120)
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
                raise ValueError('timeout must be finite and positive')
    if not isinstance(config, dict):
        raise ValueError('suite must be an object')
    unknown = set(config) - set(PHASES) - {'cases', 'redact_env'}
    if unknown:
        raise ValueError('unknown suite fields: ' + ', '.join(sorted(unknown)))
    for phase in PHASES:
        steps(config.get(phase, []))
    cases = config.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('suite requires at least one case')
    names = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('case must be an object')
        name = case.get('id', '')
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', name) or name in names:
            raise ValueError('case IDs must be unique safe names')
        names.add(name)
        if not case.get('steps'):
            raise ValueError('each case requires executable steps/assertions')
        steps(case['steps'])
    secrets = config.get('redact_env', [])
    if not isinstance(secrets, list) or not all(isinstance(v, str) for v in secrets):
        raise ValueError('redact_env must be an array of environment variable names')


def redact(text, values):
    for value in sorted(values, key=len, reverse=True):
        text = text.replace(value, '[REDACTED]')
    text = re.sub(r'(?i)(authorization|cookie|set-cookie)\s*[:=][^\r\n]*', r'\1: [REDACTED]', text)
    text = re.sub(r'''(?ix)(["']?(?:password|passwd|token|secret|api[_-]?key)["']?\s*[:=]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;]+)''', r'\1[REDACTED]', text)
    return re.sub(r'(://[^\s/:@]+:)[^\s@]+@', r'\1[REDACTED]@', text)


def excerpt(path, values):
    # Only seek a bounded tail, even for very large binary/no-newline logs.
    with path.open('rb') as stream:
        stream.seek(0, 2)
        stream.seek(max(0, stream.tell() - 8192))
        data = stream.read().decode('utf-8', errors='replace')
    return redact('\n'.join(data.splitlines()[-20:]), values)[-4000:]


def terminate(proc):
    if os.name == 'nt':
        # taskkill /T includes children; direct terminate is the fallback.
        try:
            result = subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
            if result.returncode and proc.poll() is None:
                proc.kill()
        except (OSError, subprocess.TimeoutExpired):
            proc.kill()
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=10)


def run(config, root, output, chosen):
    run_id = 'it-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
    dest = output / run_id
    dest.mkdir(parents=True, mode=0o700)
    env = dict(os.environ, IT_RUN_ID=run_id, IT_ARTIFACT_DIR=str(dest), IT_PROJECT_ROOT=str(root))
    values = [env[k] for k in config.get('redact_env', []) if env.get(k)]
    selected = [c for c in config['cases'] if not chosen or c['id'] in chosen]
    report = {'run_id': run_id, 'root': str(root), 'started_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'steps': [], 'cases': [], 'interrupted': False}

    def execute(phase, step, case_id=''):
        log = dest / f'{len(report["steps"]):03d}-{phase}-{case_id or "env"}-{step["id"]}.log'
        row = {'phase': phase, 'case_id': case_id, 'id': step['id'], 'log': str(log)}
        started = time.monotonic()
        proc = None
        try:
            with log.open('wb') as stream:
                proc = subprocess.Popen(step['cmd'], cwd=root, env=dict(env, IT_CASE_ID=case_id),
                                        stdout=stream, stderr=subprocess.STDOUT,
                                        start_new_session=os.name != 'nt')
                row['exit_code'] = proc.wait(timeout=step.get('timeout', 120))
                row['status'] = 'PASS' if row['exit_code'] == 0 else 'FAIL'
        except subprocess.TimeoutExpired:
            terminate(proc)
            row.update(status='TIMEOUT', exit_code=124)
        except KeyboardInterrupt:
            if proc is not None:
                terminate(proc)
            row.update(status='INTERRUPTED', exit_code=130)
            raise
        except OSError as error:
            row.update(status='ERROR', exit_code=127, error=redact(str(error), values))
        finally:
            row['seconds'] = round(time.monotonic() - started, 3)
            if row.get('status') != 'PASS' and log.exists():
                row['excerpt'] = excerpt(log, values)
            report['steps'].append(row)
        return row['status'] == 'PASS'

    def phase(name, always=False):
        ok = True
        for step in config.get(name, []):
            passed = execute(name, step)
            ok = ok and passed
            if not passed and not always:
                break
        return ok

    try:
        ready = True
        for name in ('preflight', 'setup', 'ready', 'seed'):
            if not phase(name):
                ready = False
                break
        for case in selected:
            row = {'id': case['id'], 'status': 'BLOCKED'}
            report['cases'].append(row)
            if ready:
                row['status'] = 'PASS'
                for step in case['steps']:
                    row['status'] = 'BLOCKED'  # interrupted execution must not look passed
                    if not execute('case', step, case['id']):
                        row['status'] = 'FAIL'
                        break
                    row['status'] = 'PASS'
    except KeyboardInterrupt:
        report['interrupted'] = True
    finally:
        # Finish collection/cleanup on first Ctrl-C or TERM; a hard kill cannot be recovered here.
        previous = {s: signal.signal(s, signal.SIG_IGN) for s in (signal.SIGINT, signal.SIGTERM)}
        try:
            try:
                phase('collect', always=True)
            finally:
                phase('cleanup', always=True)
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        recorded = {c['id'] for c in report['cases']}
        report['cases'].extend({'id': c['id'], 'status': 'BLOCKED'} for c in selected if c['id'] not in recorded)
        counts = {s: sum(c['status'] == s for c in report['cases']) for s in ('PASS', 'FAIL', 'BLOCKED')}
        infra = any(s['phase'] != 'case' and s['status'] != 'PASS' for s in report['steps'])
        code = 130 if report['interrupted'] else 2 if infra or counts['BLOCKED'] else 1 if counts['FAIL'] else 0
        report.update(counts=counts, exit_code=code)
        (dest / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        summary = f'{run_id} PASS={counts["PASS"]} FAIL={counts["FAIL"]} BLOCKED={counts["BLOCKED"]} exit={code}'
        details = [summary, f'Results: {dest / "results.json"}']
        budget = 12000
        for step in report['steps']:
            if step['status'] != 'PASS':
                details.append(f'{step["phase"]}/{step["case_id"]}/{step["id"]}: {step["status"]}; {step["log"]}')
                snippet = step.get('excerpt', '')[:budget]
                details.append(snippet)
                budget -= len(snippet)
        (dest / 'summary.txt').write_text('\n'.join(details) + '\n', encoding='utf-8')
        print(summary)
        print(f'Summary: {dest / "summary.txt"}')
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('suite', type=Path)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='project cwd for every command')
    parser.add_argument('--output', type=Path, default=Path('.integration-artifacts'))
    parser.add_argument('--case', action='append', default=[], help='repeat to select multiple case IDs')
    args = parser.parse_args()
    try:
        config = json.loads(args.suite.read_text(encoding='utf-8'))
        validate(config)
        unknown = set(args.case) - {c['id'] for c in config['cases']}
        if unknown:
            raise ValueError('unknown case ID: ' + ', '.join(sorted(unknown)))
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('--root must be a directory')
        output = args.output if args.output.is_absolute() else root / args.output
    except (ValueError, OSError) as error:
        print(f'Invalid suite: {error}', file=sys.stderr)
        return 2
    def interrupted(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupted)
    return run(config, root, output.resolve(), set(args.case))


if __name__ == '__main__':
    sys.exit(main())
