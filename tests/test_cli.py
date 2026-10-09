"""Exercise real source and relocated installed CLI behavior in isolated repositories."""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import stat
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "kavazi.py"


class CliTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="kavazi-cli-")
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name) / "Example project"
        self.repo.mkdir()

    def run_cli(self, command, *flags, installed=False, ok=True):
        script = self.repo / ".agents/skills/kavazi-method/scripts/kavazi.py" if installed else CLI
        result = subprocess.run([sys.executable, str(script), command, "--repo", str(self.repo), *flags],
                                cwd=self.directory.name, text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertNotIn("Traceback", result.stderr)
        return result

    def tree(self):
        return {p.relative_to(self.repo).as_posix(): p.read_bytes() for p in self.repo.rglob("*")
                if p.is_file()}

    def configure_closure(self):
        config_path = self.repo / ".kavazi/config.json"
        config = json.loads(config_path.read_text())
        # A command that would leave a visible marker if read-only tooling executed it.
        config["checks"] = [{"id": "fixture-check", "command": [sys.executable, "-c",
                               "from pathlib import Path; Path('SHOULD_NOT_EXIST').write_text('executed')"]}]
        config_path.write_text(json.dumps(config, indent=2) + "\n")
        state_path = self.repo / ".kavazi/state.json"
        state = json.loads(state_path.read_text())
        phase = state["phases"][0]
        phase["required_checks"] = ["fixture-check"]
        evidence = self.repo / "docs/phases/phase-01/EVIDENCE.md"
        evidence.write_text(evidence.read_text() + "\n## P01-E002\nFixture acceptance and check record.\n"
                            "\n## P01-E003\nFixture full phase review and reconciliation.\n")
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        baseline = self.run_cli("snapshot").stdout.strip()
        phase["closure"] = {
            "baseline": baseline,
            "acceptance": {"evidence": "P01-E002", "summary": "Accepted fixture behavior"},
            "checks": [{"id": "fixture-check", "result": "passed", "evidence": "P01-E002"}],
            "reviews": [{"kind": "phase", "reviewer": "fixture reviewer", "fresh": True,
                         "coverage": ["complete fixture scope and interactions"], "findings": [],
                         "refactoring": "Fixture has no justified refactoring", "evidence": "P01-E003"}],
            "documentation": {"evidence": "P01-E003", "summary": "Fixture documents reconciled"},
        }
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        return state

    def test_dry_run_then_repeatable_init_preserves_content(self):
        original = b"# Existing instructions\r\nKeep product contracts.\r\n"
        (self.repo / "AGENTS.md").write_bytes(original)
        (self.repo / "app.py").write_bytes(b"print('existing')\n")
        before = self.tree()
        self.run_cli("init", "--dry-run")
        self.assertEqual(before, self.tree())
        self.run_cli("init", "--project", "Existing app")
        self.assertTrue((self.repo / "AGENTS.md").read_bytes().startswith(original))
        after = self.tree()
        self.run_cli("init")
        self.assertEqual(after, self.tree())
        self.run_cli("check", installed=True)
        result = self.run_cli("status", installed=True)
        self.assertIn("Phase 01", result.stdout)
        self.assertIn("in_progress", result.stdout)
        self.assertEqual([p.name for p in (self.repo / "docs/phases").iterdir()], ["phase-01"])

    def test_install_only_is_self_contained_and_does_not_adopt(self):
        self.run_cli("install", "--dry-run")
        self.assertEqual(self.tree(), {})
        self.run_cli("install")
        self.assertFalse((self.repo / ".kavazi").exists())
        self.run_cli("init", installed=True)
        self.run_cli("check", installed=True)
        self.run_cli("doctor", installed=True)

    def test_init_captures_request_and_new_canonical_documents(self):
        raw = "Build a useful service\n```\n[Unresolved example](not-created.md)\n```\n$keep"
        self.run_cli("init", "--prompt", raw, "--brief", "context/REQUEST.md",
                     "--technical-core", "context/TECHNICAL.md", "--mode", "phase_checkpoint")
        self.assertIn(raw.encode(), (self.repo / "context/REQUEST.md").read_bytes())
        self.assertTrue((self.repo / "context/TECHNICAL.md").is_file())
        config = json.loads((self.repo / ".kavazi/config.json").read_text())
        self.assertEqual("phase_checkpoint", config["execution"]["mode"])
        self.run_cli("check", installed=True)
        self.assertIn("phase_checkpoint", self.run_cli("status").stdout)
        before = self.tree()
        self.run_cli("init")
        self.assertEqual(before, self.tree())

    def test_supplied_display_text_cannot_inject_document_structure_or_links(self):
        project = 'My [sample](missing.md) <pre> ```'
        source = Path(self.directory.name) / 'request [sample](missing.md) `<!--.txt'
        raw = 'Build this small project.\nKeep [this original input](uncreated.md).'
        source.write_text(raw)
        self.run_cli("init", "--project", project, "--brief-file", str(source))
        self.run_cli("check", installed=True)
        config = json.loads((self.repo / ".kavazi/config.json").read_text())
        self.assertEqual(project, config["project"])
        brief = (self.repo / config["paths"]["brief"]).read_text()
        self.assertIn(raw, brief)
        self.assertIn(project, html.unescape(brief))
        self.assertIn(str(source), html.unescape(brief))
        before = self.tree()
        self.run_cli("init", "--project", project, "--brief-file", str(source))
        self.assertEqual(before, self.tree())

    def test_next_title_and_outcome_are_literal_display_with_original_state(self):
        self.run_cli("init")
        self.configure_closure()
        self.run_cli("close")
        title = "Next [sample](missing.md)\n```md"
        outcome = "A literal <!-- example and [text](missing.md).\n```\n# New heading"
        self.run_cli("next", "--title", title, "--outcome", outcome)
        self.run_cli("check", installed=True)
        state = json.loads((self.repo / ".kavazi/state.json").read_text())
        self.assertEqual(title, state["phases"][1]["title"])
        plan = (self.repo / "docs/phases/phase-02/IMPLEMENTATION_PLAN.md").read_text()
        self.assertIn(title, html.unescape(plan))
        self.assertIn(outcome, html.unescape(plan))

    def test_init_file_input_is_verbatim_and_source_flags_exclusive(self):
        raw = b"A real request\r\nWith preserved newlines.\r\n"
        source = Path(self.directory.name) / "request.txt"
        source.write_bytes(raw)
        self.run_cli("init", "--brief-file", str(source), "--prompt", "Ambiguous", ok=False)
        self.assertEqual({}, self.tree())
        self.run_cli("init", "--brief-file", str(source))
        self.assertIn(raw, (self.repo / "docs/PROJECT_BRIEF.md").read_bytes())
        self.assertIn("autonomous", self.run_cli("status").stdout)

    def test_installed_dry_run_and_read_only_commands_write_no_caches(self):
        self.run_cli("install")
        before = self.tree()
        self.run_cli("init", "--dry-run", installed=True)
        self.assertEqual(before, self.tree())
        self.run_cli("init", installed=True)
        before = self.tree()
        for command in ("status", "check", "doctor", "snapshot"):
            self.run_cli(command, installed=True)
            self.assertEqual(before, self.tree(), command)
        self.assertFalse(any("__pycache__" in name for name in self.tree()))

    def test_next_refuses_unfinished_and_invalid_closure(self):
        self.run_cli("init")
        before = self.tree()
        self.run_cli("next", "--title", "Future", "--outcome", "A future outcome", ok=False)
        self.run_cli("close", ok=False)
        self.assertEqual(before, self.tree())
        self.assertFalse((self.repo / "docs/phases/phase-02").exists())

    def test_supported_closure_then_only_immediate_next_package(self):
        self.run_cli("init")
        self.configure_closure()
        self.run_cli("check", "--closure")
        self.run_cli("doctor")
        self.assertFalse((Path(self.directory.name) / "SHOULD_NOT_EXIST").exists())
        self.assertFalse((self.repo / "SHOULD_NOT_EXIST").exists())
        before = self.tree()
        self.run_cli("close", "--dry-run")
        self.assertEqual(before, self.tree())
        self.run_cli("close")
        self.assertIn("complete", self.run_cli("status").stdout)
        before = self.tree()
        self.run_cli("next", "--title", "Second", "--outcome", "Build the next bounded outcome", "--dry-run", installed=True)
        self.assertEqual(before, self.tree())
        self.run_cli("next", "--title", "Second", "--outcome", "Build the next bounded outcome", installed=True)
        self.run_cli("check")
        self.assertEqual(sorted(p.name for p in (self.repo / "docs/phases").iterdir()), ["phase-01", "phase-02"])
        self.run_cli("next", "--title", "Third", "--outcome", "Must wait", ok=False)

    def test_checkout_next_uses_its_own_templates_without_an_installed_skill(self):
        self.run_cli("init")
        shutil.rmtree(self.repo / ".agents")
        self.configure_closure()
        self.run_cli("close")
        before = self.tree()
        flags = ("--title", "Second", "--outcome", "Advance from the source checkout")
        self.run_cli("next", *flags, "--dry-run")
        self.assertEqual(before, self.tree())
        self.assertFalse((self.repo / ".agents").exists())
        self.run_cli("next", *flags)
        self.run_cli("check")
        package = self.repo / "docs/phases/phase-02"
        self.assertEqual({"IMPLEMENTATION_PLAN.md", "METHODOLOGY.md", "EVIDENCE.md"},
                         {path.name for path in package.iterdir()})
        self.assertFalse((self.repo / ".agents").exists())
        self.assertFalse((self.repo / "docs/phases/phase-03").exists())

    def test_generated_sync_command_runs_from_internal_and_external_source_paths(self):
        source_name = "-tool with spaces 'quotes' ```` [link](missing.md)\n$(touch KAVAZI_INJECTED)"
        for location in ("internal", "external"):
            with self.subTest(location=location):
                self.repo = Path(self.directory.name) / f"Target {location}"
                self.repo.mkdir()
                self.run_cli("init")
                shutil.rmtree(self.repo / ".agents")
                source = (self.repo if location == "internal" else Path(self.directory.name)) / source_name
                shutil.copytree(ROOT / "skills/kavazi-method", source,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
                script = source / "scripts/kavazi.py"
                self.configure_closure()
                self.run_cli("close")
                flags = [sys.executable, str(script), "next", "--repo", str(self.repo),
                         "--title", "Second", "--outcome", "A usable generated command"]
                before = self.tree()
                preview = subprocess.run([*flags, "--dry-run"], capture_output=True, text=True)
                self.assertEqual(0, preview.returncode, preview.stderr)
                self.assertEqual(before, self.tree())
                created = subprocess.run(flags, capture_output=True, text=True)
                self.assertEqual(0, created.returncode, created.stderr)
                self.run_cli("check")
                plan = (self.repo / "docs/phases/phase-02/IMPLEMENTATION_PLAN.md").read_text()
                block = re.search(r"^(`{3,})sh\n(.*?)\n\1$", plan, re.MULTILINE | re.DOTALL)
                self.assertIsNotNone(block, plan)
                command = block[2]
                expected_path = "./" + script.relative_to(self.repo).as_posix() if location == "internal" else str(script)
                self.assertEqual(["python3", expected_path, "sync", "--repo", "."], shlex.split(command))
                self.assertEqual(location == "external", "external Kavazi directory" in plan)
                synced = subprocess.run(command, shell=True, cwd=self.repo, capture_output=True, text=True)
                self.assertEqual(0, synced.returncode, synced.stderr)
                self.assertFalse((self.repo / "KAVAZI_INJECTED").exists())
                self.assertFalse((self.repo / ".agents").exists())
                self.run_cli("check")

    def test_next_rejects_carriage_return_tool_path_before_writes(self):
        self.run_cli("init")
        shutil.rmtree(self.repo / ".agents")
        source = Path(self.directory.name) / "tool with\rcarriage return"
        shutil.copytree(ROOT / "skills/kavazi-method", source,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        self.configure_closure()
        self.run_cli("close")
        before = self.tree()
        for dry_run in (True, False):
            flags = [sys.executable, str(source / "scripts/kavazi.py"), "next", "--repo", str(self.repo),
                     "--title", "Second", "--outcome", "A command whose path must round-trip"]
            result = subprocess.run([*flags, *(["--dry-run"] if dry_run else [])], capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("Markdown rendering changes it", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(before, self.tree())
            self.assertFalse((self.repo / "docs/phases/phase-02").exists())

    def test_checkpoint_closure_waits_until_explicit_approval_record(self):
        self.run_cli("init", "--mode", "phase_checkpoint")
        self.configure_closure()
        self.run_cli("close")
        status = self.run_cli("status").stdout
        self.assertIn("Waiting for explicit human approval", status)
        before = self.tree()
        result = self.run_cli("next", "--title", "Second", "--outcome", "Needs checkpoint", ok=False)
        self.assertIn("waiting for explicit human approval", result.stderr)
        self.assertEqual(before, self.tree())
        evidence = self.repo / "docs/phases/phase-01/EVIDENCE.md"
        evidence.write_text(evidence.read_text() + "\n## P01-E004\nAda explicitly approved advancing after reviewing the phase results.\n")
        before = self.tree()
        flags = ("--evidence", "P01-E004", "--summary", "Proceed to the next phase", "--by", "Ada Developer")
        self.run_cli("approve", *flags, "--dry-run")
        self.assertEqual(before, self.tree())
        self.run_cli("approve", *flags, installed=True)
        state = json.loads((self.repo / ".kavazi/state.json").read_text())
        self.assertEqual({"evidence": "P01-E004", "summary": "Proceed to the next phase", "granted_by": "Ada Developer"},
                         state["phases"][0]["closure"]["human_approval"])
        before = self.tree()
        self.run_cli("approve", *flags)
        self.assertEqual(before, self.tree())
        self.assertIn("approval recorded from Ada Developer", self.run_cli("status").stdout)
        self.run_cli("next", "--title", "Second", "--outcome", "Accepted successor")
        self.run_cli("check")
        self.assertFalse((self.repo / "docs/phases/phase-03").exists())
        # Historical approval remains required after the next package exists;
        # deleting the ledger attestation cannot silently bypass the checkpoint.
        state_path = self.repo / ".kavazi/state.json"
        state = json.loads(state_path.read_text())
        del state["phases"][0]["closure"]["human_approval"]
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        before = self.tree()
        self.run_cli("check", ok=False)
        self.run_cli("status", ok=False)
        self.assertEqual(before, self.tree())

    def test_approval_requires_completed_checkpoint_phase_and_real_evidence(self):
        flags = ("--evidence", "P01-E004", "--summary", "Proceed", "--by", "Ada Developer")
        self.run_cli("init")
        before = self.tree()
        self.run_cli("approve", *flags, ok=False)
        self.assertEqual(before, self.tree())

        config_path = self.repo / ".kavazi/config.json"
        config = json.loads(config_path.read_text())
        config["execution"]["mode"] = "phase_checkpoint"
        config_path.write_text(json.dumps(config, indent=2) + "\n")
        before = self.tree()
        self.run_cli("approve", *flags, ok=False)
        self.assertEqual(before, self.tree())
        self.configure_closure()
        self.run_cli("close")
        before = self.tree()
        self.run_cli("approve", *flags, ok=False)
        self.assertEqual(before, self.tree())
        evidence = self.repo / "docs/phases/phase-01/EVIDENCE.md"
        evidence.write_text(evidence.read_text() + "\n```md\n## P01-E004\nUnexecuted approval example\n```\n")
        before = self.tree()
        self.run_cli("approve", *flags, ok=False)
        self.assertEqual(before, self.tree())

    def test_malformed_approval_is_rejected_before_read_or_write_actions(self):
        self.run_cli("init", "--mode", "phase_checkpoint")
        self.configure_closure()
        self.run_cli("close")
        state_path = self.repo / ".kavazi/state.json"
        state = json.loads(state_path.read_text())
        state["phases"][0]["closure"]["human_approval"] = "invented"
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        before = self.tree()
        self.run_cli("status", ok=False)
        self.run_cli("approve", "--evidence", "P01-E003", "--summary", "Proceed", "--by", "Ada", ok=False)
        self.run_cli("next", "--title", "Second", "--outcome", "Must wait", ok=False)
        self.assertEqual(before, self.tree())

    def test_stale_baseline_prevents_approval_before_any_write(self):
        self.run_cli("init", "--mode", "phase_checkpoint")
        self.configure_closure()
        self.run_cli("close")
        evidence = self.repo / "docs/phases/phase-01/EVIDENCE.md"
        evidence.write_text(evidence.read_text() + "\n## P01-E004\nExplicit human approval observation.\n")
        (self.repo / "app.py").write_text("# Changed after closure\n")
        before = self.tree()
        self.run_cli("approve", "--evidence", "P01-E004", "--summary", "Proceed", "--by", "Ada", ok=False)
        self.assertEqual(before, self.tree())

    def test_substantive_change_invalidates_closure(self):
        self.run_cli("init")
        self.configure_closure()
        (self.repo / "app.py").write_text("# later implementation change\n")
        self.run_cli("check", "--closure", ok=False)
        self.run_cli("close", ok=False)

    def test_malformed_state_reports_error_without_traceback(self):
        self.run_cli("init")
        (self.repo / ".kavazi/state.json").write_text('{"schema_version":1,"phases":[null]}')
        self.run_cli("check", ok=False)
        self.run_cli("status", ok=False)
        self.run_cli("sync", ok=False)

    def test_sync_repairs_only_register_drift(self):
        self.run_cli("init")
        state_path = self.repo / ".kavazi/state.json"
        state = json.loads(state_path.read_text())
        state["phases"][0]["next_action"] = "Inspect the actual baseline"
        state_path.write_text(json.dumps(state) + "\n")
        self.run_cli("check", ok=False)
        self.run_cli("sync")
        self.run_cli("check")
        state["phases"][0]["status"] = "anything"
        state_path.write_text(json.dumps(state) + "\n")
        before = self.tree()
        self.run_cli("sync", ok=False)
        self.assertEqual(before, self.tree())

    def test_atomic_cli_updates_preserve_existing_file_permissions(self):
        self.run_cli("init")
        state_path = self.repo / ".kavazi/state.json"
        master = self.repo / "docs/MASTER_IMPLEMENTATION_PLAN.md"
        state = json.loads(state_path.read_text())
        state["phases"][0]["next_action"] = "Observe permissions preservation"
        state_path.write_text(json.dumps(state) + "\n")
        master.chmod(0o664)
        self.run_cli("sync")
        self.assertEqual(stat.S_IMODE(master.stat().st_mode), 0o664)
        self.configure_closure()
        state_path.chmod(0o664)
        self.run_cli("close")
        self.assertEqual(stat.S_IMODE(state_path.stat().st_mode), 0o664)
        self.assertEqual(stat.S_IMODE(master.stat().st_mode), 0o664)

    def test_symlinked_target_is_rejected(self):
        alias = Path(self.directory.name) / "alias"
        try:
            alias.symlink_to(self.repo, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        result = subprocess.run([sys.executable, str(CLI), "init", "--repo", str(alias)],
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tree(), {})


if __name__ == "__main__":
    unittest.main()
