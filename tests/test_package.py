"""Check package completeness and frontmatter without a runtime YAML dependency."""
from pathlib import Path
import importlib.util
import json
import os
import re
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def builder_fixture(self, checkout):
        spec = importlib.util.spec_from_file_location("build_plugin", ROOT / "scripts/build_plugin.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        (checkout / "plugin.json").write_text('{"name":"fixture","version":"0.1.0","license":"MIT"}')
        notice = (ROOT / "LICENSE").read_bytes()
        (checkout / "LICENSE").write_bytes(notice)
        for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md"):
            (checkout / name).write_text("# Fixture\n")
        for name in ("kavazi-method", "kavazi-setup"):
            payload = checkout / "skills" / name
            payload.mkdir(parents=True)
            (payload / "SKILL.md").write_text(f"---\nname: {name}\nlicense: MIT\n---\n# Fixture\n")
            (payload / "LICENSE").write_bytes(notice)
        payload = checkout / "skills/kavazi-method"
        return builder, payload

    def assert_failed_build_preserves_outputs(self, builder, checkout, error):
        existing = checkout / "existing.zip"
        existing.write_bytes(b"Previously accepted archive")
        absent = checkout / "new-output/release.zip"
        for target in (absent, existing):
            with self.subTest(output=target), self.assertRaisesRegex(ValueError, error):
                builder.build(checkout, target)
        self.assertFalse(absent.parent.exists())
        self.assertEqual(existing.read_bytes(), b"Previously accepted archive")
        self.assertFalse(list(checkout.glob(".kavazi-archive-*")))

    def test_plugin_and_onboarding_resolve_inside_bundle(self):
        manifest = json.loads((ROOT / "plugin.json").read_text())
        self.assertEqual(manifest["name"], "kavazi-method")
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual("MIT", manifest["license"])
        self.assertEqual("David Kavazi", manifest["author"]["name"])
        onboarding = manifest["extensions"]["com.openai"]["onboardingSkill"]
        self.assertTrue(onboarding.startswith("./"))
        path = (ROOT / onboarding).resolve()
        path.relative_to(ROOT)
        self.assertTrue(path.is_file())

    def test_release_skills_have_frontmatter_and_resolvable_references(self):
        for skill in (ROOT / "skills").iterdir():
            with self.subTest(skill=skill.name):
                body = (skill / "SKILL.md").read_text()
                parts = body.split("---", 2)
                self.assertEqual(parts[0], "")
                self.assertRegex(parts[1], rf"(?m)^name: {re.escape(skill.name)}\s*$")
                self.assertRegex(parts[1], r"(?m)^description: .+")
                self.assertNotRegex(body, r"(?i)\bTODO\b|\[insert .+\]")
                for link in re.findall(r"\]\(([^)]+)\)", parts[2]):
                    if "://" not in link:
                        path = (skill / link.split("#", 1)[0]).resolve()
                        path.relative_to(ROOT / "skills")
                        self.assertTrue(path.exists(), link)

    def test_main_skill_contains_every_runtime_resource(self):
        main = ROOT / "skills/kavazi-method"
        for name in ("scripts/kavazi.py", "scripts/core.py", "scripts/onboarding.py",
                     "references/core-method.md", "references/adoption.md", "references/records.md",
                     "assets/templates/brief.md", "assets/templates/architecture.md",
                     "assets/templates/methodology.md", "assets/templates/technical-core.md",
                     "assets/templates/master-plan.md", "assets/templates/phase-plan.md",
                     "assets/templates/phase-methodology.md", "assets/templates/phase-evidence.md"):
            self.assertTrue((main / name).is_file(), name)

    def test_repository_carries_the_selected_mit_terms_and_copyright(self):
        expected = '''MIT License
Copyright (c) 2026 David Kavazi
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''
        notice = (ROOT / "LICENSE").read_bytes()
        self.assertEqual(expected.split(), notice.decode("utf-8").split())
        for name in ("kavazi-method", "kavazi-setup"):
            self.assertEqual(notice, (ROOT / "skills" / name / "LICENSE").read_bytes())

    def test_incomplete_release_or_license_mismatch_fails_before_output_writes(self):
        variants = ("missing-root-notice", "different-skill-notice", "empty-notices",
                    "wrong-skill-declaration", "wrong-manifest-license", "missing-manifest-name",
                    "missing-main-skill", "missing-setup-skill", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md")
        for variant in variants:
            with self.subTest(variant=variant), tempfile.TemporaryDirectory(prefix="kavazi-release-contract-") as directory:
                checkout = Path(directory)
                builder, payload = self.builder_fixture(checkout)
                if variant == "missing-root-notice":
                    (checkout / "LICENSE").unlink()
                elif variant == "different-skill-notice":
                    notice = payload / "LICENSE"
                    notice.write_bytes(notice.read_bytes().replace(b"David Kavazi", b"Another Author"))
                elif variant == "empty-notices":
                    for notice in (checkout / "LICENSE", payload / "LICENSE", checkout / "skills/kavazi-setup/LICENSE"):
                        notice.write_bytes(b"")
                elif variant == "wrong-skill-declaration":
                    skill = payload / "SKILL.md"
                    skill.write_text(skill.read_text().replace("license: MIT", "license: Apache-2.0"))
                elif variant in {"wrong-manifest-license", "missing-manifest-name"}:
                    path = checkout / "plugin.json"
                    manifest = json.loads(path.read_text())
                    if variant == "wrong-manifest-license":
                        manifest["license"] = "Apache-2.0"
                    else:
                        del manifest["name"]
                    path.write_text(json.dumps(manifest))
                elif variant in {"missing-main-skill", "missing-setup-skill"}:
                    shutil.rmtree(checkout / "skills" / ("kavazi-method" if variant == "missing-main-skill" else "kavazi-setup"))
                else:
                    (checkout / variant).unlink()
                self.assert_failed_build_preserves_outputs(builder, checkout, ".+")

    def test_reproducible_zip_contains_only_distribution_payload(self):
        spec = importlib.util.spec_from_file_location("build_plugin", ROOT / "scripts/build_plugin.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory(prefix="kavazi-package-") as directory:
            first, second = Path(directory) / "first.zip", Path(directory) / "second.zip"
            builder.build(ROOT, first)
            builder.build(ROOT, second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                names = set(archive.namelist())
                self.assertIn("plugin.json", names)
                for name in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md"):
                    self.assertIn(name, names)
                for name in ("skills/kavazi-method/LICENSE", "skills/kavazi-setup/LICENSE"):
                    self.assertEqual((ROOT / "LICENSE").read_bytes(), archive.read(name))
                self.assertIn("skills/kavazi-method/scripts/kavazi.py", names)
                self.assertIn("skills/kavazi-setup/SKILL.md", names)
                self.assertIn("skills/kavazi-method/assets/templates/brief.md", names)
                self.assertIn("skills/kavazi-method/assets/templates/technical-core.md", names)
                self.assertNotIn(".kavazi/state.json", names)
                self.assertFalse(any("__pycache__" in name or name.startswith("tests/") for name in names))

    def test_extracted_bundle_can_capture_input_and_initialize_full_chain(self):
        spec = importlib.util.spec_from_file_location("build_plugin", ROOT / "scripts/build_plugin.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        with tempfile.TemporaryDirectory(prefix="kavazi-extracted-") as directory:
            fixture = Path(directory)
            archive_path, extracted, project = fixture / "release.zip", fixture / "bundle", fixture / "project"
            project.mkdir()
            builder.build(ROOT, archive_path)
            with zipfile.ZipFile(archive_path) as archive:
                archive.extractall(extracted)
            prompt = "Create a complete local puzzle game.\nKeep costs below $20; preserve this λ input."
            script = extracted / "skills/kavazi-method/scripts/kavazi.py"
            result = subprocess.run(
                [sys.executable, str(script), "init", "--repo", str(project),
                 "--project", "Puzzle fixture", "--prompt", prompt, "--mode", "phase_checkpoint"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            config = json.loads((project / ".kavazi/config.json").read_text())
            self.assertEqual(config["execution"]["mode"], "phase_checkpoint")
            for key in ("brief", "core", "architecture", "methodology", "technical_core", "master_plan"):
                self.assertTrue((project / config["paths"][key]).is_file(), key)
            self.assertIn(prompt, (project / config["paths"]["brief"]).read_text())
            installed = project / ".agents/skills/kavazi-method/scripts/kavazi.py"
            check = subprocess.run(
                [sys.executable, str(installed), "check", "--repo", str(project)],
                capture_output=True, text=True,
            )
            self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
            self.assertEqual((ROOT / "LICENSE").read_bytes(),
                             (project / ".agents/skills/kavazi-method/LICENSE").read_bytes())
            self.assertFalse((project / "LICENSE").exists())

    def test_zip_output_cannot_become_a_skill_payload_resource(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-build-boundary-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            with self.assertRaisesRegex(ValueError, "outside the skills"):
                builder.build(checkout, payload / "release.zip")
            self.assertFalse((payload / "release.zip").exists())
            elsewhere = checkout / "elsewhere"
            elsewhere.mkdir()
            for target in (elsewhere / "../skills/kavazi-method/release.zip", elsewhere / "../plugin.json"):
                before = (checkout / "plugin.json").read_bytes()
                with self.subTest(target=target), self.assertRaises(ValueError):
                    builder.build(checkout, target)
                self.assertFalse((payload / "release.zip").exists())
                self.assertEqual((checkout / "plugin.json").read_bytes(), before)

    def test_nonzip_destination_cannot_overwrite_the_builder_source(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-source-boundary-") as directory:
            checkout = Path(directory)
            builder, _ = self.builder_fixture(checkout)
            source = checkout / "scripts/build_plugin.py"
            source.parent.mkdir()
            source.write_bytes((ROOT / "scripts/build_plugin.py").read_bytes())
            before = {p.relative_to(checkout): p.read_bytes() for p in checkout.rglob("*") if p.is_file()}
            with self.assertRaisesRegex(ValueError, r"\.zip extension"):
                builder.build(checkout, source)
            self.assertEqual(before, {p.relative_to(checkout): p.read_bytes() for p in checkout.rglob("*") if p.is_file()})

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes are unavailable")
    def test_fifo_manifest_fails_before_reading_and_preserves_archive(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-manifest-fifo-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            manifest = checkout / "plugin.json"
            manifest.unlink()
            os.mkfifo(manifest)
            # A regression must fail promptly instead of hanging while opening the FIFO.
            with mock.patch.object(Path, "read_text", side_effect=AssertionError("Manifest opened before regular-file preflight")):
                self.assert_failed_build_preserves_outputs(builder, checkout, "regular distribution file")
            self.assertTrue(stat.S_ISFIFO(manifest.stat().st_mode))
            self.assertTrue((payload / "SKILL.md").read_text().endswith("# Fixture\n"))

    @unittest.skipUnless(hasattr(os, "mkfifo"), "Named pipes are unavailable")
    def test_fifo_payload_file_cannot_be_silently_omitted(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-payload-types-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            pipe = payload / "required-resource"
            os.mkfifo(pipe)
            self.assert_failed_build_preserves_outputs(builder, checkout, "regular distribution file")

    @unittest.skipUnless(hasattr(socket, "AF_UNIX"), "Unix-domain sockets are unavailable")
    def test_socket_payload_file_cannot_be_silently_omitted(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-socket-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stream:
                try:
                    stream.bind(str(payload / "resource.sock"))
                except PermissionError:
                    self.skipTest("Current host permissions prohibit Unix-domain socket creation")
                self.assert_failed_build_preserves_outputs(builder, checkout, "regular distribution file")

    def test_payload_directory_scan_error_preserves_existing_archive(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-scan-error-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            nested = payload / "references/nested"
            nested.mkdir(parents=True)
            resource = nested / "required.md"
            resource.write_text("Required distribution content\n")
            actual_scandir = os.scandir

            def guarded_scandir(path):
                if Path(path) == nested:
                    raise PermissionError(13, "Permission denied", str(path))
                return actual_scandir(path)

            with mock.patch.object(builder.os, "scandir", side_effect=guarded_scandir):
                self.assert_failed_build_preserves_outputs(builder, checkout, "Cannot inspect distribution directory")
            self.assertEqual(resource.read_text(), "Required distribution content\n")

    def test_unreadable_nested_payload_directory_fails_without_archive(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-unreadable-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            nested = payload / "references/private"
            nested.mkdir(parents=True)
            (nested / "required.md").write_text("Required distribution content\n")
            previous_mode = stat.S_IMODE(nested.stat().st_mode)
            try:
                nested.chmod(0)
                try:
                    with os.scandir(nested) as entries:
                        list(entries)
                except PermissionError:
                    pass
                else:
                    self.skipTest("Current permissions allow reading mode-000 directories")
                self.assert_failed_build_preserves_outputs(builder, checkout, "Cannot inspect distribution directory")
            finally:
                nested.chmod(previous_mode)

    def test_source_walk_rejects_symlinks_and_keeps_cache_exclusions(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-source-walk-") as directory:
            checkout = Path(directory)
            builder, payload = self.builder_fixture(checkout)
            cache = payload / "__pycache__"
            cache.mkdir()
            (cache / "ignored.pyc").write_bytes(b"Cached bytecode")
            (payload / "ignored.pyo").write_bytes(b"Cached bytecode")
            output = checkout / "accepted.zip"
            builder.build(checkout, output)
            with zipfile.ZipFile(output) as archive:
                self.assertFalse(any("__pycache__" in name or name.endswith(".pyo") for name in archive.namelist()))
            (payload / "linked-reference").symlink_to(payload / "SKILL.md")
            self.assert_failed_build_preserves_outputs(builder, checkout, "Symlinks are not distributable")


if __name__ == "__main__":
    unittest.main()
