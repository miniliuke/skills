"""Regression checks for the optional runner; Python standard library only."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'skills/backend-integration-testing/scripts/run_suite.py'
spec = importlib.util.spec_from_file_location('runner', RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def step(self, name, code, **kw):
        return {'id': name, 'cmd': [sys.executable, '-c', code], **kw}

    def config(self, steps=None):
        return {'cases': [{'id': 'IT-001', 'steps': steps or [self.step('ok', 'print("ok")')]}],
                'cleanup': [self.step('clean', 'from pathlib import Path; Path("cleaned").touch()')]}

    def write(self, config):
        path = self.root / 'suite.json'
        path.write_text(json.dumps(config), encoding='utf-8')
        return [sys.executable, str(RUNNER), str(path), '--root', str(self.root)]

    def run_suite(self, config, *args, env=None):
        result = subprocess.run(self.write(config) + list(args), capture_output=True, text=True, env=env, timeout=15)
        paths = sorted((self.root / '.integration-artifacts').glob('*/results.json'), key=lambda p: p.stat().st_mtime_ns)
        report = json.loads(paths[-1].read_text()) if paths else None
        return result, report

    def test_repeatable_sqlite_flow(self):
        setup = 'import sqlite3; c=sqlite3.connect("test.db"); c.execute("create table items(id integer primary key, value text)"); c.commit()'
        insert = 'import sqlite3; c=sqlite3.connect("test.db"); c.execute("insert into items values(1, ?)", ("hello",)); c.commit()'
        check = 'import sqlite3; c=sqlite3.connect("test.db"); assert c.execute("select * from items").fetchall() == [(1,"hello")]'
        config = self.config([self.step('insert', insert), self.step('assert', check)])
        config['setup'] = [self.step('db', setup)]
        config['cleanup'] = [self.step('db', 'from pathlib import Path; Path("test.db").unlink(missing_ok=True)')]
        runs = []
        for _ in range(2):
            result, report = self.run_suite(config)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(report['counts'], {'PASS': 1, 'FAIL': 0, 'BLOCKED': 0})
            self.assertFalse((self.root / 'test.db').exists())
            runs.append(report['run_id'])
        self.assertNotEqual(*runs)

    def test_failure_stops_dependent_steps_collects_and_continues_independent_case(self):
        config = self.config([self.step('fail', 'raise AssertionError("expected=1 actual=2")'),
                              self.step('forbidden', 'raise Exception("must not run")')])
        config['cases'].append({'id': 'IT-002', 'steps': [self.step('ok', 'pass')]})
        config['collect'] = [self.step('collect', 'from pathlib import Path; Path("evidence").write_text("saved")')]
        result, report = self.run_suite(config)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['counts']['PASS'], 1)
        self.assertEqual(report['counts']['FAIL'], 1)
        self.assertNotIn('forbidden', [s['id'] for s in report['steps']])
        self.assertTrue((self.root / 'evidence').exists())
        self.assertTrue((self.root / 'cleaned').exists())

    def test_setup_failure_is_blocked_and_cleans_partial_environment(self):
        config = self.config()
        config['setup'] = [self.step('bad', 'raise SystemExit(8)')]
        result, report = self.run_suite(config)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report['cases'][0]['status'], 'BLOCKED')
        self.assertTrue((self.root / 'cleaned').exists())

    def test_collect_and_cleanup_failure_preserve_business_failure(self):
        config = self.config([self.step('failed-case', 'raise SystemExit(5)')])
        config['collect'] = [self.step('bad-collect', 'raise SystemExit(6)')]
        config['cleanup'].insert(0, self.step('bad-clean', 'raise SystemExit(7)'))
        result, report = self.run_suite(config)
        self.assertEqual(result.returncode, 2)
        self.assertEqual([s['exit_code'] for s in report['steps']], [5, 6, 7, 0])
        self.assertEqual(report['cases'][0]['status'], 'FAIL')
        self.assertTrue((self.root / 'cleaned').exists())

    def test_timeout_and_missing_executable(self):
        config = self.config([self.step('slow', 'import time; time.sleep(30)', timeout=0.1)])
        result, report = self.run_suite(config)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['steps'][0]['status'], 'TIMEOUT')
        self.assertTrue((self.root / 'cleaned').exists())
        config['cases'][0]['steps'] = [{'id': 'missing', 'cmd': ['nonexistent-integration-test-command']}]
        result, report = self.run_suite(config)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report['steps'][0]['exit_code'], 127)

    def test_selection_and_invalid_config_do_not_mutate(self):
        config = self.config()
        config['cases'].append({'id': 'IT-002', 'steps': [self.step('ok', 'pass')]})
        result, report = self.run_suite(config, '--case', 'IT-002')
        self.assertEqual(result.returncode, 0)
        self.assertEqual([c['id'] for c in report['cases']], ['IT-002'])
        (self.root / 'cleaned').unlink()
        result, _ = self.run_suite(config, '--case', 'unknown')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'cleaned').exists())
        config['cases'] = []
        result, _ = self.run_suite(config)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'cleaned').exists())

    def test_bounded_secret_redaction(self):
        secret = 'sensitive-test-value-12345'
        code = 'import os; print("x"*100000); print(os.environ["PRIVATE_VALUE"]); print("Authorization: Bearer abc123"); print("password=hunter2"); print("postgres://user:dbpass@host/db"); raise SystemExit(1)'
        config = self.config([self.step('secrets', code)])
        config['redact_env'] = ['PRIVATE_VALUE']
        result, report = self.run_suite(config, env=dict(os.environ, PRIVATE_VALUE=secret))
        self.assertEqual(result.returncode, 1)
        rendered = json.dumps(report)
        for value in (secret, 'abc123', 'hunter2', 'dbpass'):
            self.assertNotIn(value, rendered)
        self.assertLessEqual(len(report['steps'][0]['excerpt']), 4000)
        self.assertIn('[REDACTED]', report['steps'][0]['excerpt'])
        self.assertIn('Authorization:', report['steps'][0]['excerpt'])
        self.assertNotIn(secret, result.stdout)

    @unittest.skipIf(os.name == 'nt', 'POSIX process-group and signal check')
    def test_term_collects_and_cleans(self):
        config = self.config([self.step('wait', 'from pathlib import Path; import time; Path("started").touch(); time.sleep(30)')])
        process = subprocess.Popen(self.write(config), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5
            while not (self.root / 'started').exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue((self.root / 'started').exists())
            process.send_signal(signal.SIGTERM)
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 130, out + err)
            self.assertTrue((self.root / 'cleaned').exists())
            report = json.loads(next((self.root / '.integration-artifacts').glob('*/results.json')).read_text())
            self.assertTrue(report['interrupted'])
            self.assertEqual(report['cases'][0]['status'], 'BLOCKED')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    def test_reject_invalid_timeouts_and_duplicate_ids(self):
        for timeout in (0, -1, float('nan'), float('inf'), True):
            with self.assertRaises(ValueError):
                runner.validate(self.config([self.step('bad', 'pass', timeout=timeout)]))
        config = self.config()
        config['clean-up'] = []
        with self.assertRaises(ValueError):
            runner.validate(config)
        config = self.config()
        config['cases'].append(config['cases'][0])
        with self.assertRaises(ValueError):
            runner.validate(config)


if __name__ == '__main__':
    unittest.main()
