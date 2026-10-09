"""Behavioral regression coverage for the read-only protocol and closure gates."""

import copy
import html
import importlib.util
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/kavazi-method/scripts/core.py"
SPEC = importlib.util.spec_from_file_location("kavazi_core_test", SCRIPT)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config = {
            "schema_version": 1, "method_version": "0.1.0", "project": "Fixture",
            "paths": {"core": "CORE_KAVAZI_METHOD.md", "architecture": "docs/MASTER_ARCHITECTURE.md",
                      "brief": "docs/PROJECT_BRIEF.md", "technical_core": "docs/MASTER_TECHNICAL_CORE.md",
                      "methodology": "docs/MASTER_METHODOLOGY.md", "master_plan": "docs/MASTER_IMPLEMENTATION_PLAN.md",
                      "phases": "docs/phases"},
            "execution": {"mode": "autonomous"},
            "checks": [{"id": "tests", "command": ["python3", "-m", "unittest"]}],
        }
        self.state = {"schema_version": 1, "phases": [self.phase(1)]}
        for key, relative in self.config["paths"].items():
            if key != "phases":
                self.write(relative, "# " + key + "\n")
        self.write(self.config["paths"]["master_plan"], "# Plan\n\n" + core.render_register(self.state) + "\n\nPreserve this footer.\n")
        self.package(1)
        self.save()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def save(self, sync=True):
        self.write(".kavazi/config.json", json.dumps(self.config))
        self.write(".kavazi/state.json", json.dumps(self.state))
        if sync and isinstance(self.state, dict) and isinstance(self.state.get("phases"), list):
            self.write(self.config["paths"]["master_plan"], core.sync_register(self.root, self.config, self.state))

    @staticmethod
    def phase(number, status="in_progress"):
        return {"number": number, "title": f"Phase {number}", "status": status,
                "next_action": "Observe acceptance", "required_checks": ["tests"], "closure": None}

    def package(self, number):
        relative = f"docs/phases/phase-{number:02d}"
        self.write(relative + "/IMPLEMENTATION_PLAN.md", "# Plan\n\n[Methods](METHODOLOGY.md) · [Evidence](EVIDENCE.md)\n")
        self.write(relative + "/METHODOLOGY.md", "# Methods\n")
        self.write(relative + "/EVIDENCE.md", "# Evidence\n\n" + "\n".join(f"## P{number:02d}-E{i:03d} — observed results\n\nObserved actual check.\n" for i in range(1, 5)))

    def record(self, number=1):
        evidence = f"P{number:02d}-E001"
        review = {"kind": "phase", "reviewer": "Observed reviewer", "fresh": True,
                  "coverage": ["Entire phase scope and interactions"], "findings": [],
                  "refactoring": "No refactor warranted after inspection", "evidence": evidence}
        return {"baseline": core.snapshot(self.root, self.config),
                "acceptance": {"evidence": evidence, "summary": "Observed intended behavior"},
                "checks": [{"id": "tests", "result": "passed", "evidence": evidence}],
                "reviews": [review], "documentation": {"evidence": evidence, "summary": "Documents reconciled"}}

    def assert_error(self, needle, closure=False):
        errors = core.validate(self.root, closure=closure)
        self.assertTrue(any(needle.lower() in error.lower() for error in errors), errors)

    def test_valid_structure_is_read_only_and_load_permits_malformed_state(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(core.validate(self.root), [])
        self.assertEqual(core.load_project(self.root), (self.config, self.state))
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.write(".kavazi/state.json", "[]")
        self.assertEqual(core.load_project(self.root)[1], [])
        self.assert_error("State must be an object")

    def test_safe_path_rejects_traversal_absolute_and_symlinks(self):
        for value in ("../escape", "/tmp/escape", "a/../b", "C:\\escape", "C:escape", "a\\b", "", "a//b", "."):
            with self.subTest(path=value), self.assertRaises(core.KavaziError):
                core.safe_path(self.root, value)
        self.assertEqual(core.safe_path(self.root, "new/deep/file.md"), self.root / "new/deep/file.md")
        (self.root / "link").symlink_to(self.root / "docs", target_is_directory=True)
        with self.assertRaises(core.KavaziError):
            core.safe_path(self.root, "link/no-file.md")
        with self.assertRaises(core.KavaziError):
            core.safe_path(self.root / "link", "no-file.md")

    def test_invalid_configuration_reports_diagnostic(self):
        mutations = [lambda c: c.update(schema_version=True), lambda c: c.update(project=" "),
                     lambda c: c["paths"].update(core="../bad"), lambda c: c["paths"].update(core=".kavazi/x"),
                     lambda c: c["paths"].update(core="build/CORE.md"),
                     lambda c: c["checks"].append(copy.deepcopy(c["checks"][0])),
                     lambda c: c["checks"][0].update(command="echo pass"), lambda c: c.update(paths=[])]
        original = copy.deepcopy(self.config)
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                self.config = copy.deepcopy(original)
                mutate(self.config)
                self.write(".kavazi/config.json", json.dumps(self.config))
                with self.assertRaises(core.KavaziError):
                    core.load_project(self.root)
                self.assert_error("configuration")

    def test_duplicate_json_keys_fail_without_silently_overwriting_authority(self):
        self.write(".kavazi/state.json", '{"schema_version":1,"phases":[],"phases":[]}')
        self.assert_error("Duplicate JSON key")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named pipes unavailable")
    def test_nonregular_record_and_canonical_files_are_rejected_before_open(self):
        for relative in (".kavazi/config.json", "CORE_KAVAZI_METHOD.md"):
            path = self.root / relative
            original = path.read_bytes()
            path.unlink()
            os.mkfifo(path)
            try:
                original_open = Path.open
                def guarded_open(candidate, *args, **kwargs):
                    if candidate == path:
                        raise AssertionError("Reader attempted to open a named pipe")
                    return original_open(candidate, *args, **kwargs)
                with patch.object(Path, "open", guarded_open):
                    self.assert_error("expected a regular file")
            finally:
                path.unlink()
                path.write_bytes(original)

    def test_malformed_states_report_without_tracebacks(self):
        values = [None, [], "text", {}, {"schema_version": True, "phases": []},
                  {"schema_version": 1, "phases": [None]}, {"schema_version": 1, "phases": [{"number": True}]},
                  {"schema_version": 1, "phases": [dict(self.phase(1), status=[])]},
                  {"schema_version": 1, "phases": [dict(self.phase(1), required_checks=[{}])] }]
        for state in values:
            with self.subTest(state=state):
                self.write(".kavazi/state.json", json.dumps(state))
                self.assertTrue(core.validate(self.root))

    def test_register_sync_preserves_surrounding_bytes_and_requires_one_pair(self):
        self.state["phases"][0]["title"] = "New | title\nnext"
        self.save(sync=False)
        self.assert_error("register is stale")
        before = (self.root / self.config["paths"]["master_plan"]).read_text()
        after = core.sync_register(self.root, self.config, self.state)
        self.assertTrue(after.startswith(before.split(core.REGISTER_START)[0]))
        self.assertTrue(after.endswith(before.split(core.REGISTER_END)[1]))
        self.assertIn("New | title next", html.unescape(after))
        self.assertEqual((self.root / self.config["paths"]["master_plan"]).read_text(), before)
        for body in ("No markers", core.REGISTER_END + core.REGISTER_START,
                     core.REGISTER_START + core.REGISTER_START + core.REGISTER_END):
            self.write(self.config["paths"]["master_plan"], body)
            with self.assertRaises(core.KavaziError):
                core.sync_register(self.root, self.config, self.state)

    def test_register_sync_preserves_crlf_outside_block_and_rejects_fenced_markers(self):
        path = self.root / self.config["paths"]["master_plan"]
        prefix, suffix = "# Plan\r\n\r\n", "\r\n\r\nUser footer\r\n"
        path.write_bytes((prefix + core.render_register(self.state).replace("\n", "\r\n") + suffix).encode())
        result = core.sync_register(self.root, self.config, self.state)
        self.assertTrue(result.startswith(prefix))
        self.assertTrue(result.endswith(suffix))
        self.write(self.config["paths"]["master_plan"], "```md\n" + core.render_register(self.state) + "\n```\n")
        with self.assertRaisesRegex(core.KavaziError, "unfenced"):
            core.sync_register(self.root, self.config, self.state)

    def test_links_validate_real_anchors_ignore_fences_and_support_duplicate_slugs(self):
        self.write("docs/target.md", "# API, Results!\n# API, Results!\n```md\n# Imaginary\n```\nTitle Underlined\n---\n")
        self.write("CORE_KAVAZI_METHOD.md", "# Core\n[a](docs/target.md#api-results)\n[b](docs/target.md#api-results-1)\n[c](docs/target.md#title-underlined)\n```md\n[bad](missing.md)\n~~~\n```\n")
        self.assertEqual(core.validate(self.root), [])
        self.write("CORE_KAVAZI_METHOD.md", "# Core\n[bad](docs/target.md#imaginary)\n[missing](missing.md)\n[escape](../outside.md)\n")
        self.assert_error("missing heading anchor")
        self.assert_error("missing local link target")
        self.assert_error("escapes repository")

    def test_reference_links_and_malformed_url(self):
        self.write("CORE_KAVAZI_METHOD.md", "# Core\n[docs][known]\n[known]: docs/MASTER_ARCHITECTURE.md\n")
        self.assertEqual(core.validate(self.root), [])
        self.write("CORE_KAVAZI_METHOD.md", "# Core\n[bad][unknown]\n[broken](http://[broken)\n")
        self.assert_error("missing Markdown link definition")
        self.assert_error("malformed link")

    def test_link_heading_labels_and_explicit_anchors(self):
        self.write("docs/target.md", '# [Reference](MASTER_ARCHITECTURE.md)\n<a id="custom-anchor"></a>\n')
        self.write("CORE_KAVAZI_METHOD.md", "# Core\n[a](docs/target.md#reference)\n[b](docs/target.md#custom-anchor)\n")
        self.assertEqual(core.validate(self.root), [])

    def test_mixed_fence_closer_cannot_create_live_evidence_heading(self):
        self.state["phases"][0]["closure"] = self.record()
        self.state["phases"][0]["closure"]["acceptance"]["evidence"] = "P01-E999"
        path = "docs/phases/phase-01/EVIDENCE.md"
        self.write(path, (self.root / path).read_text() + "\n```md\n```~~~\n## P01-E999\n```\n")
        self.save()
        self.assert_error("unfenced heading ID", closure=True)

    def test_hidden_html_cannot_supply_closure_evidence(self):
        path = "docs/phases/phase-01/EVIDENCE.md"
        for hidden in ("<!--\n## P01-E001\n-->", "<!--\n## P01-E001",
                       "<pre>\n## P01-E001\n</pre>", "<script>\n## P01-E001\n</script>",
                       "<pre>\n</pre >\n## P01-E001",
                       "<div>\n## P01-E001\n</div>", "<?test\n## P01-E001\n?>",
                       "<!doctype\n## P01-E001\n>",
                       "<![CDATA[\n## P01-E001\n]]>"):
            with self.subTest(hidden=hidden):
                self.write(path, "# Evidence\n" + hidden + "\n")
                self.state["phases"][0]["closure"] = self.record()
                self.save()
                self.assert_error("unfenced heading ID", closure=True)

    def test_html_and_fence_boundaries_preserve_live_evidence(self):
        path = "docs/phases/phase-01/EVIDENCE.md"
        for prefix in ("<!--\n```md\n-->\n", "```md\n<!--\n```\n",
                       "Literal `<!--` example.\n", "<div>\nLiteral HTML.\n</div>\n\n",
                       "<pre>\n</script>\n"):
            with self.subTest(prefix=prefix):
                self.write(path, "# Evidence\n" + prefix + "## P01-E001 Observation\nActual result.\n")
                self.state["phases"][0]["closure"] = self.record()
                self.save()
                self.assertEqual([], core.validate(self.root, closure=True))

    def test_commented_links_and_html_anchors_are_inert(self):
        self.write("docs/target.md", '# Target\n<!--\n<a id="hidden"></a>\n-->\n'
                   '<pre>\n<a id="raw"></a>\n</pre>\n\n<a id="live"></a>\n')
        self.write("CORE_KAVAZI_METHOD.md", "# Core\n<!-- [bad](missing.md) -->\n[good](docs/target.md#live)\n")
        self.assertEqual([], core.validate(self.root))
        for anchor in ("hidden", "raw"):
            with self.subTest(anchor=anchor):
                self.write("CORE_KAVAZI_METHOD.md", f"# Core\n[bad](docs/target.md#{anchor})\n")
                self.assert_error("missing heading anchor")

    def test_register_markers_inside_html_are_rejected(self):
        path = self.config["paths"]["master_plan"]
        for opening, ending in (("<!--", "-->"), ("<div>", "</div>")):
            self.write(path, opening + "\n" + core.render_register(self.state) + "\n" + ending + "\n")
            with self.subTest(opening=opening), self.assertRaisesRegex(core.KavaziError, "unfenced"):
                core.sync_register(self.root, self.config, self.state)

    def test_execution_mode_and_technical_core_are_validated_and_snapshotted(self):
        original = core.snapshot(self.root, self.config)
        self.write(self.config["paths"]["technical_core"], "# Technical Core\nChanged mechanism.\n")
        self.assertNotEqual(original, core.snapshot(self.root, self.config))
        self.config["execution"]["mode"] = "unknown"
        self.save(sync=False)
        self.assert_error("execution.mode")
        self.config["execution"] = {"mode": "autonomous"}
        del self.config["paths"]["technical_core"]
        self.save(sync=False)
        self.assert_error("technical_core")

    def test_checkpoint_approval_is_required_only_for_advancement(self):
        self.config["execution"]["mode"] = "phase_checkpoint"
        self.save()
        phase = self.state["phases"][0]
        phase["closure"] = self.record()
        phase["status"] = "complete"
        self.save()
        self.assertEqual([], core.validate(self.root, closure=True))
        self.package(2)
        self.state["phases"].append(self.phase(2))
        self.save()
        self.assert_error("human approval")
        phase["closure"]["human_approval"] = {"evidence": "P01-E004", "summary": "User approved Phase 02", "granted_by": "User"}
        self.save()
        self.assertEqual([], core.validate(self.root))
        phase["closure"]["human_approval"]["evidence"] = "P02-E001"
        self.save()
        self.assert_error("unfenced heading ID")

    def test_approval_requires_completed_phase_and_actual_evidence(self):
        approval = {"evidence": "P01-E001", "summary": "Continue", "granted_by": "User"}
        phase = self.state["phases"][0]
        with self.assertRaisesRegex(core.KavaziError, "after the phase is complete"):
            core.validate_human_approval(self.root, self.config, phase, approval)
        phase["status"] = "complete"
        core.validate_human_approval(self.root, self.config, phase, approval)
        for key in approval:
            invalid = {**approval, key: ""}
            with self.subTest(key=key), self.assertRaises(core.KavaziError):
                core.validate_human_approval(self.root, self.config, phase, invalid)

    def test_phase_prefix_folders_and_numbering_are_enforced(self):
        self.state["phases"].append(self.phase(2, "not_planned"))
        self.save()
        self.assertEqual(core.validate(self.root), [])
        self.package(2)
        self.assert_error("future not_planned phase")
        self.state["phases"][1]["status"] = "in_progress"
        self.save()
        self.assert_error("predecessor must fully close")
        self.write("docs/phases/phase-03/IMPLEMENTATION_PLAN.md", "# Premature\n")
        self.assert_error("Unregistered")
        self.state["phases"][1]["number"] = 3
        self.save()
        self.assert_error("contiguous positive integers")

    def test_malformed_future_package_names_cannot_hide_in_phase_directory(self):
        self.write("docs/phases/phase-02-draft/IMPLEMENTATION_PLAN.md", "# Premature detailed draft\n")
        self.assert_error("noncanonical phase package")

    def test_closure_requires_supported_observed_records_and_current_baseline(self):
        self.assert_error("must be a recorded object", closure=True)
        self.state["phases"][0]["closure"] = self.record()
        self.save()
        self.assertEqual(core.validate(self.root, closure=True), [])
        self.state["phases"][0]["status"] = "complete"
        self.save()
        self.assertEqual(core.validate(self.root), [])
        self.write("source.py", "changed = True\n")
        self.assert_error("baseline differs")

    def test_closure_requires_at_least_one_required_check_and_no_unavailable_check(self):
        self.state["phases"][0]["closure"] = self.record()
        self.state["phases"][0]["required_checks"] = []
        self.save()
        self.assert_error("at least one", closure=True)
        self.state["phases"][0]["required_checks"] = ["tests"]
        self.state["phases"][0]["closure"]["checks"][0]["result"] = "unavailable"
        self.save()
        self.assert_error("observed passed result", closure=True)

    def test_evidence_references_cannot_use_fenced_heading_or_other_phase(self):
        self.state["phases"][0]["closure"] = self.record()
        self.state["phases"][0]["closure"]["acceptance"]["evidence"] = "P01-E999"
        path = "docs/phases/phase-01/EVIDENCE.md"
        self.write(path, (self.root / path).read_text() + "\n```md\n## P01-E999\n```\n")
        self.save()
        self.assert_error("unfenced heading ID", closure=True)
        self.state["phases"][0]["closure"]["acceptance"]["evidence"] = "P02-E001"
        self.save()
        self.assert_error("unfenced heading ID", closure=True)

    def test_review_rounds_preserve_unresolved_findings_and_require_fresh_final_round(self):
        record = self.record()
        record["reviews"][0]["fresh"] = False
        record["reviews"][0]["findings"] = [{"id": "F001", "status": "open", "evidence": "P01-E002"}]
        final = copy.deepcopy(record["reviews"][0])
        final.update(fresh=True, findings=[])
        record["reviews"].append(final)
        self.state["phases"][0]["closure"] = record
        self.save()
        self.assert_error("unresolved earlier finding F001", closure=True)
        final["findings"] = [{"id": "F001", "status": "resolved", "evidence": "P01-E003"}]
        self.save()
        self.assertEqual(core.validate(self.root, closure=True), [])
        final["fresh"] = False
        self.save()
        self.assert_error("last phase review must be fresh", closure=True)

    def test_historical_baselines_are_not_compared_to_current_active_successor(self):
        self.state["phases"][0].update(status="complete", closure=self.record())
        self.state["phases"].append(self.phase(2))
        self.package(2)
        self.write("new_product.py", "new = True\n")
        self.save()
        self.assertEqual(core.validate(self.root), [])
        self.state["phases"][0]["closure"]["acceptance"]["evidence"] = "nonexistent"
        self.save()
        self.assert_error("unfenced heading ID")

    def test_fifth_phase_needs_phase_and_whole_repository_fresh_reviews(self):
        self.state["phases"] = []
        for number in range(1, 6):
            self.package(number)
            phase = self.phase(number, "complete" if number < 5 else "in_progress")
            phase["closure"] = self.record(number)
            self.state["phases"].append(phase)
        self.save()
        self.state["phases"][-1]["closure"]["baseline"] = core.snapshot(self.root, self.config)
        self.save()
        self.assert_error("last whole_repository review must be fresh", closure=True)
        whole = copy.deepcopy(self.state["phases"][-1]["closure"]["reviews"][0])
        whole["kind"] = "whole_repository"
        self.state["phases"][-1]["closure"]["reviews"].append(whole)
        self.save()
        self.assertEqual(core.validate(self.root, closure=True), [])

    def test_snapshot_excludes_ledger_evidence_dependencies_and_generated_register(self):
        before = core.snapshot(self.root, self.config)
        self.write(".kavazi/state.json", "unparseable excluded ledger")
        self.write("docs/phases/phase-01/EVIDENCE.md", "new observation")
        for name in (".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", "build", "dist"):
            self.write(f"{name}/ignored.bin", "new excluded bytes")
        master = self.root / self.config["paths"]["master_plan"]
        master.write_text(master.read_text().replace("Observe acceptance", "Changed register text"))
        self.assertEqual(core.snapshot(self.root, self.config), before)
        self.write("docs/phases/phase-01/IMPLEMENTATION_PLAN.md", "Substantive edit\n")
        self.assertNotEqual(core.snapshot(self.root, self.config), before)

    def test_snapshot_covers_paths_config_assets_and_nonphase_evidence(self):
        before = core.snapshot(self.root, self.config)
        self.write("assets/shape.bin", "asset")
        asset = core.snapshot(self.root, self.config)
        self.assertNotEqual(asset, before)
        (self.root / "assets/shape.bin").rename(self.root / "assets/renamed.bin")
        self.assertNotEqual(core.snapshot(self.root, self.config), asset)
        previous = core.snapshot(self.root, self.config)
        self.write("docs/EVIDENCE.md", "This is not a phase log")
        self.assertNotEqual(core.snapshot(self.root, self.config), previous)

    def test_snapshot_rejects_scoped_symlink_and_invalid_configuration(self):
        (self.root / "unsafe.py").symlink_to(self.root / "CORE_KAVAZI_METHOD.md")
        with self.assertRaisesRegex(core.KavaziError, "Symlink"):
            core.snapshot(self.root, self.config)
        invalid = copy.deepcopy(self.config)
        invalid["paths"]["master_plan"] = "../outside.md"
        with self.assertRaisesRegex(core.KavaziError, "configuration"):
            core.snapshot(self.root, invalid)


if __name__ == "__main__":
    unittest.main()
