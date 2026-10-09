"""Behavioral regressions for preservation and complete write preflight."""

import html
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/kavazi-method/scripts"))
import core
import onboarding


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.source = self.base / "source"
        self.repo.mkdir()
        (self.source / "assets/templates").mkdir(parents=True)
        (self.source / "references").mkdir()
        (self.source / "scripts").mkdir()
        (self.source / "SKILL.md").write_text("---\nname: fixture\nlicense: MIT\n---\n# Portable skill\n", encoding="utf-8")
        (self.source / "LICENSE").write_bytes((Path(__file__).resolve().parents[1] / "LICENSE").read_bytes())
        (self.source / "scripts/kavazi.py").write_text("# Tool fixture\n", encoding="utf-8")
        (self.source / "references/core-method.md").write_text("## Rules\nOne active phase.\n", encoding="utf-8")
        templates = {
            "brief.md": "# $project Brief\nSource: $brief_source\nMode: $execution_mode\n$brief\n[Architecture]($architecture_link)\n",
            "architecture.md": "# $project Architecture\n[Core]($core_link)\n",
            "methodology.md": "# $project Methodology\n[Architecture]($architecture_link)\n",
            "technical-core.md": "# $project Technical Core\n[Brief]($brief_link)\n[Methods]($methodology_link)\n",
            "master-plan.md": "# $project Master Plan\n$register\n[Phase]($current_phase_link)\n",
            "phase-plan.md": "# $phase_id $title\n$outcome\n[State]($state_link)\n",
            "phase-methodology.md": "# $phase_id Methodology\n[Core]($core_link)\n",
            "phase-evidence.md": "# Evidence\n## $phase_id-E001 Adoption\n$date\nNo runtime checks performed.\n",
        }
        for name, text in templates.items():
            (self.source / "assets/templates" / name).write_text(text, encoding="utf-8")

    def contents(self):
        return {path.relative_to(self.repo).as_posix(): path.read_bytes() for path in self.repo.rglob("*") if path.is_file()}

    def test_dry_run_has_zero_writes_and_same_proposal(self):
        (self.repo / "user.txt").write_bytes(b"Keep this\x00")
        before = self.contents()
        proposed = onboarding.init_project(self.repo, self.source, dry_run=True)
        self.assertEqual(before, self.contents())
        self.assertFalse((self.repo / ".kavazi").exists())
        self.assertFalse((self.repo / ".agents").exists())
        self.assertEqual(proposed, onboarding.init_project(self.repo, self.source))
        self.assertEqual([], core.validate(self.repo))

    def test_repeated_adoption_is_noop_and_keeps_evidence_unverified(self):
        onboarding.init_project(self.repo, self.source)
        before = self.contents()
        self.assertEqual([], onboarding.init_project(self.repo, self.source))
        self.assertEqual(before, self.contents())
        _, state = core.load_project(self.repo)
        phase = state["phases"][0]
        self.assertEqual("in_progress", phase["status"])
        self.assertIsNone(phase["closure"])
        self.assertEqual([], phase["required_checks"])
        self.assertTrue(core.validate(self.repo, closure=True))
        self.assertFalse((self.repo / "docs/phases/phase-02").exists())
        config, _ = core.load_project(self.repo)
        self.assertEqual({"mode": "autonomous"}, config["execution"])
        self.assertTrue((self.repo / "docs/PROJECT_BRIEF.md").is_file())
        self.assertTrue((self.repo / "docs/MASTER_TECHNICAL_CORE.md").is_file())

    def test_skill_notice_is_copied_without_relicensing_the_project(self):
        project_notice = b"Copyright Example Company\r\nProject-specific terms remain in force.\r\n"
        (self.repo / "LICENSE").write_bytes(project_notice)
        onboarding.install_skill(self.repo, self.source)
        installed_notice = self.repo / onboarding.INSTALL_PATH / "LICENSE"
        self.assertEqual((self.source / "LICENSE").read_bytes(), installed_notice.read_bytes())
        onboarding.init_project(self.repo, self.source)
        self.assertEqual(project_notice, (self.repo / "LICENSE").read_bytes())
        self.assertEqual((self.source / "LICENSE").read_bytes(), installed_notice.read_bytes())

    def test_missing_or_invalid_skill_license_aborts_all_install_and_init_writes(self):
        notice = self.source / "LICENSE"
        original = notice.read_bytes()
        skill = self.source / "SKILL.md"
        original_skill = skill.read_text()
        variants = ("missing", "empty", "truncated", "undeclared", "different")
        for variant in variants:
            notice.write_bytes(original)
            skill.write_text(original_skill)
            if variant == "missing":
                notice.unlink()
            elif variant == "empty":
                notice.write_bytes(b"")
            elif variant == "truncated":
                notice.write_text("MIT License\nCopyright (c) 2026 Example\n")
            elif variant == "undeclared":
                skill.write_text(original_skill.replace("license: MIT\n", ""))
            else:
                skill.write_text(original_skill.replace("license: MIT", "license: Apache-2.0"))
            before = self.contents()
            for action in (onboarding.install_skill, onboarding.init_project):
                for dry_run in (True, False):
                    with self.subTest(variant=variant, action=action.__name__, dry_run=dry_run):
                        with self.assertRaises(core.KavaziError):
                            action(self.repo, self.source, dry_run=dry_run)
                        self.assertEqual(before, self.contents())
                        self.assertFalse((self.repo / ".agents").exists())
                        self.assertFalse((self.repo / ".kavazi").exists())

    def test_agent_prefix_preserved_byte_for_byte(self):
        original = b"# User rules\r\nPreserve unusual bytes: \xff"
        (self.repo / "AGENTS.md").write_bytes(original)
        onboarding.init_project(self.repo, self.source)
        resulting = (self.repo / "AGENTS.md").read_bytes()
        self.assertTrue(resulting.startswith(original))
        self.assertEqual(1, resulting.count(onboarding.INSTRUCTIONS_START))
        onboarding.init_project(self.repo, self.source)
        self.assertEqual(resulting, (self.repo / "AGENTS.md").read_bytes())

    def test_hidden_agent_entry_is_rejected_before_any_adoption_writes(self):
        for prefix in (b"# Rules\n\n```text\nUnfinished example\n",
                       b"# Rules\n\n<!--\nUnfinished comment\n",
                       b"# Rules\n\n<pre>\nUnfinished raw block\n"):
            (self.repo / "AGENTS.md").write_bytes(prefix)
            before = self.contents()
            for dry_run in (True, False):
                with self.subTest(prefix=prefix, dry_run=dry_run), self.assertRaisesRegex(core.KavaziError, "visible Markdown"):
                    onboarding.init_project(self.repo, self.source, prompt="Build a project", dry_run=dry_run)
                self.assertEqual(before, self.contents())
                self.assertFalse((self.repo / ".agents").exists())

    def test_existing_managed_block_in_fenced_example_cannot_count_as_arrival(self):
        onboarding.init_project(self.repo, self.source)
        agents = self.repo / "AGENTS.md"
        agents.write_bytes(b"```text\n" + agents.read_bytes() + b"```\n")
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "visible Markdown"):
            onboarding.init_project(self.repo, self.source)
        self.assertEqual(before, self.contents())

    def test_default_master_conflict_aborts_all_writes(self):
        (self.repo / "CORE_KAVAZI_METHOD.md").write_bytes(b"Existing core\n")
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "explicit path mapping"):
            onboarding.init_project(self.repo, self.source)
        self.assertEqual(before, self.contents())
        self.assertFalse((self.repo / ".agents").exists())

    def test_explicit_existing_masters_preserved_and_register_appended(self):
        (self.repo / "design").mkdir()
        mappings = {
            "core": "design/CORE.md", "brief": "design/INPUT.md", "architecture": "design/ARCH.md",
            "methodology": "design/METHOD.md", "technical_core": "design/TECH.md", "master_plan": "design/PLAN.md",
            "phases": "work/phases",
        }
        original = {}
        for key, path in mappings.items():
            if key != "phases":
                data = f"# Existing {key}\nKeep accepted requirements.\n".encode()
                (self.repo / path).write_bytes(data)
                original[path] = data
        onboarding.init_project(self.repo, self.source, paths=mappings)
        for key in ("core", "brief", "architecture", "methodology", "technical_core"):
            self.assertEqual(original[mappings[key]], (self.repo / mappings[key]).read_bytes())
        self.assertTrue((self.repo / mappings["master_plan"]).read_bytes().startswith(original[mappings["master_plan"]]))
        self.assertEqual([], core.validate(self.repo))
        self.assertEqual([], onboarding.init_project(self.repo, self.source, paths=mappings))

    def test_inherited_phase_history_blocks_even_with_new_mapping(self):
        inherited = self.repo / "docs/phases/phase-03"
        inherited.mkdir(parents=True)
        (inherited / "EVIDENCE.md").write_text("Historical work\n")
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "existing phase history"):
            onboarding.init_project(self.repo, self.source, paths={"phases": "new/phases"})
        self.assertEqual(before, self.contents())

    def test_raw_prompt_capture_uses_adaptive_fence_and_preserves_input(self):
        raw = "Develop this service\r\n```md\n[Unknown link](missing.md)\n``````\n$literal ${title}\r\n"
        onboarding.init_project(self.repo, self.source, prompt=raw, mode="phase_checkpoint")
        brief = (self.repo / "docs/PROJECT_BRIEF.md").read_bytes()
        self.assertIn(raw.encode("utf-8"), brief)
        self.assertIn(b"```````text", brief)
        self.assertIn(b"--prompt", brief)
        self.assertIn(b"phase_checkpoint", brief)
        self.assertEqual([], core.validate(self.repo))
        before = self.contents()
        self.assertEqual([], onboarding.init_project(self.repo, self.source, prompt=raw))
        self.assertEqual(before, self.contents())
        with self.assertRaisesRegex(core.KavaziError, "Incoming user input differs"):
            onboarding.init_project(self.repo, self.source, prompt="Changed scope")
        self.assertEqual(before, self.contents())

    def test_file_brief_capture_preserves_crlf_and_checks_sources(self):
        source = self.base / "initial request.txt"
        raw = b"User request\r\nKeep this exact text.\r\n"
        source.write_bytes(raw)
        before = self.contents()
        onboarding.init_project(self.repo, self.source, brief_file=source, dry_run=True)
        self.assertEqual(before, self.contents())
        onboarding.init_project(self.repo, self.source, brief_file=source)
        brief = (self.repo / "docs/PROJECT_BRIEF.md").read_bytes()
        self.assertIn(raw, brief)
        self.assertIn(str(source), html.unescape(brief.decode("utf-8")))
        self.assertEqual([], onboarding.init_project(self.repo, self.source, brief_file=source))
        before = self.contents()
        source.write_bytes(raw.rstrip(b"\r\n"))
        with self.assertRaisesRegex(core.KavaziError, "Incoming user input differs"):
            onboarding.init_project(self.repo, self.source, brief_file=source)
        self.assertEqual(before, self.contents())

    def test_changed_prompt_terminal_newline_is_not_silently_discarded(self):
        onboarding.init_project(self.repo, self.source, prompt="Exact input")
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "Incoming user input differs"):
            onboarding.init_project(self.repo, self.source, prompt="Exact input\n")
        self.assertEqual(before, self.contents())

    def test_user_capture_examples_cannot_spoof_existing_input_provenance(self):
        candidate = "Different user scope"
        fenced, metadata = onboarding._capture_brief(candidate, None)
        original = f"Document this capture example:\n{metadata}\n{fenced}\nKeep the original requirement."
        onboarding.init_project(self.repo, self.source, prompt=original)
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "Incoming user input differs"):
            onboarding.init_project(self.repo, self.source, prompt=candidate)
        self.assertEqual(before, self.contents())

    def test_equivalent_literal_provenance_formats_preserve_the_same_input(self):
        raw = "Keep this exact request."
        onboarding.init_project(self.repo, self.source, prompt=raw)
        path = self.repo / "docs/PROJECT_BRIEF.md"
        body = path.read_text()
        fenced, metadata = onboarding._capture_brief(raw, None)
        self.assertIn(fenced, body)
        path.write_text(body.replace(metadata, html.unescape(metadata)))
        before = self.contents()
        self.assertEqual([], onboarding.init_project(self.repo, self.source, prompt=raw))
        self.assertEqual(before, self.contents())
        with self.assertRaisesRegex(core.KavaziError, "Incoming user input differs"):
            onboarding.init_project(self.repo, self.source, prompt=raw + "\n")
        self.assertEqual(before, self.contents())

    def test_unreadable_payload_directory_fails_before_any_target_writes(self):
        hidden = self.source / "hidden"
        hidden.mkdir()
        (hidden / "needed.txt").write_text("Required payload data.")
        hidden.chmod(0)
        try:
            if os.access(hidden, os.R_OK | os.X_OK):
                self.skipTest("User can traverse permission-restricted directories")
            for dry_run in (True, False):
                with self.subTest(dry_run=dry_run), self.assertRaisesRegex(core.KavaziError, "Cannot inspect skill payload"):
                    onboarding.install_skill(self.repo, self.source, dry_run=dry_run)
                self.assertEqual({}, self.contents())
                self.assertFalse((self.repo / ".agents").exists())
        finally:
            hidden.chmod(0o755)

    def test_invalid_or_ambiguous_brief_sources_leave_repository_untouched(self):
        source = self.base / "bad.txt"
        source.write_bytes(b"Invalid UTF-8: \xff")
        cases = (
            {"brief_file": source}, {"brief_file": self.base},
            {"brief_file": self.base / "missing.txt"},
            {"prompt": "one", "brief_file": source},
            {"prompt": ""}, {"prompt": "  \r\n"},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(core.KavaziError):
                onboarding.init_project(self.repo, self.source, **kwargs)
            self.assertEqual({}, self.contents())

    def test_existing_mapped_brief_and_new_prompt_require_reconciliation(self):
        (self.repo / "INPUT.md").write_bytes(b"Existing accepted user requirements.\n")
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "mapped brief already exists"):
            onboarding.init_project(self.repo, self.source, paths={"brief": "INPUT.md"}, prompt="new input")
        self.assertEqual(before, self.contents())

    def test_omitted_mode_preserves_checkpoint_and_conflict_refuses(self):
        onboarding.init_project(self.repo, self.source, mode="phase_checkpoint")
        before = self.contents()
        self.assertEqual([], onboarding.init_project(self.repo, self.source))
        self.assertEqual("phase_checkpoint", core.load_project(self.repo)[0]["execution"]["mode"])
        with self.assertRaisesRegex(core.KavaziError, "different execution mode"):
            onboarding.init_project(self.repo, self.source, mode="autonomous")
        self.assertEqual(before, self.contents())

    def test_existing_unclosed_fence_blocks_register_append_before_any_writes(self):
        original = b"# Original roadmap\n\n```text\nExisting planned sample\n"
        (self.repo / "roadmap.md").write_bytes(original)
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "unfenced"):
            onboarding.init_project(self.repo, self.source, paths={"master_plan": "roadmap.md"})
        self.assertEqual(before, self.contents())
        self.assertFalse((self.repo / ".agents").exists())

    def test_excluded_canonical_path_blocks_both_preview_and_apply_before_writes(self):
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run), self.assertRaisesRegex(core.KavaziError, "snapshot-excluded"):
                onboarding.init_project(self.repo, self.source, paths={"core": "dist/CORE.md"}, dry_run=dry_run)
            self.assertEqual({}, self.contents())
            self.assertFalse((self.repo / ".agents").exists())

    def test_unsupported_canonical_encoding_is_preserved_and_blocks_adoption(self):
        original = b"# Existing architecture\n\xff\n"
        (self.repo / "architecture.md").write_bytes(original)
        before = self.contents()
        for dry_run in (True, False):
            with self.subTest(dry_run=dry_run), self.assertRaisesRegex(core.KavaziError, "must be UTF-8"):
                onboarding.init_project(self.repo, self.source,
                                        paths={"architecture": "architecture.md"}, dry_run=dry_run)
            self.assertEqual(before, self.contents())
            self.assertFalse((self.repo / ".agents").exists())

    def test_mapped_document_links_support_spaces_and_url_punctuation(self):
        mappings = {
            "core": "project notes/CORE #1.md", "architecture": "project notes/ARCH & design.md",
            "methodology": "project notes/METHOD ?.md", "master_plan": "project notes/PLAN.md",
            "phases": "project notes/phases",
        }
        onboarding.init_project(self.repo, self.source, paths=mappings)
        self.assertEqual([], core.validate(self.repo))
        agents = (self.repo / "AGENTS.md").read_text()
        self.assertIn("CORE%20%231.md", agents)

    def test_late_agent_conflict_blocks_payload_and_documents(self):
        (self.repo / "AGENTS.md").write_bytes(onboarding.INSTRUCTIONS_START + b"\nMalformed\n")
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "malformed"):
            onboarding.init_project(self.repo, self.source)
        self.assertEqual(before, self.contents())
        self.assertFalse((self.repo / "docs").exists())

    def test_differing_payload_never_overwrites_or_partially_installs(self):
        onboarding.install_skill(self.repo, self.source)
        original = self.contents()
        (self.source / "SKILL.md").write_text("---\nname: fixture\nlicense: MIT\n---\nChanged package\n")
        (self.source / "references/new.md").write_text("New file\n")
        with self.assertRaisesRegex(core.KavaziError, "conflicting existing file"):
            onboarding.install_skill(self.repo, self.source)
        self.assertEqual(original, self.contents())

    def test_source_destination_identity_is_noop_including_dry_run(self):
        onboarding.install_skill(self.repo, self.source)
        installed = self.repo / onboarding.INSTALL_PATH
        before = self.contents()
        self.assertEqual([], onboarding.install_skill(self.repo, installed, dry_run=True))
        self.assertEqual([], onboarding.install_skill(self.repo, installed))
        self.assertEqual(before, self.contents())

    def test_symlink_destination_and_source_are_rejected_without_writes(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.repo / ".agents").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        with self.assertRaisesRegex(core.KavaziError, "Symlink"):
            onboarding.init_project(self.repo, self.source)
        self.assertEqual([], list(outside.iterdir()))
        (self.repo / ".agents").unlink()
        (self.source / "references/linked.md").symlink_to(self.source / "SKILL.md")
        with self.assertRaisesRegex(core.KavaziError, "symlink"):
            onboarding.install_skill(self.repo, self.source, dry_run=True)
        self.assertEqual({}, self.contents())

    def test_path_and_output_collisions_fail_before_writes(self):
        for paths in ({"core": "../outside.md"}, {"core": ".kavazi/state.json"}, {"architecture": "docs/phases/ARCH.md"}, {"core": "AGENTS.md"}):
            with self.subTest(paths=paths), self.assertRaises(core.KavaziError):
                onboarding.init_project(self.repo, self.source, paths=paths)
            self.assertEqual({}, self.contents())

    def test_existing_state_and_changed_configuration_require_reconciliation(self):
        onboarding.init_project(self.repo, self.source)
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "different project name"):
            onboarding.init_project(self.repo, self.source, project="other")
        self.assertEqual(before, self.contents())
        config_path = self.repo / ".kavazi/config.json"
        config_path.unlink()
        before = self.contents()
        with self.assertRaisesRegex(core.KavaziError, "state without configuration"):
            onboarding.init_project(self.repo, self.source)
        self.assertEqual(before, self.contents())

    def test_required_commands_are_never_executed_by_repeated_init(self):
        onboarding.init_project(self.repo, self.source)
        config_path = self.repo / ".kavazi/config.json"
        config = json.loads(config_path.read_text())
        sentinel = self.repo / "executed"
        config["checks"] = [{"id": "sentinel", "command": [sys.executable, "-c", f"open({str(sentinel)!r}, 'w').write('bad')"]}]
        config_path.write_text(json.dumps(config))
        self.assertEqual([], onboarding.init_project(self.repo, self.source))
        self.assertFalse(sentinel.exists())

    def test_new_phase_writes_use_installed_self_contained_templates(self):
        onboarding.init_project(self.repo, self.source)
        config, state = core.load_project(self.repo)
        before = self.contents()
        proposed = onboarding.create_phase_files(self.repo, config, 2, "Useful work", "Observed outcome", dry_run=True)
        self.assertEqual(3, len(proposed))
        self.assertEqual(before, self.contents())
        onboarding.create_phase_files(self.repo, config, 2, "Useful work", "Observed outcome")
        self.assertEqual(state, core.load_project(self.repo)[1])
        with self.assertRaisesRegex(core.KavaziError, "already exists"):
            onboarding.create_phase_files(self.repo, config, 2, "Useful work", "Observed outcome")

    def test_mid_write_io_failure_reports_partial_result(self):
        real_replace = onboarding.os.replace
        count = 0

        def fail_second(source, destination):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated storage failure")
            return real_replace(source, destination)

        with patch.object(onboarding.os, "replace", side_effect=fail_second):
            with self.assertRaisesRegex(core.KavaziError, "Files already written:") as caught:
                onboarding.install_skill(self.repo, self.source)
        self.assertEqual(1, len(self.contents()))
        for path in self.contents():
            self.assertIn(path, str(caught.exception))
        self.assertFalse(any(self.repo.rglob(".kavazi-write-*")))


if __name__ == "__main__":
    unittest.main()
