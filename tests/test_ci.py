"""Exercise the exact trusted route and CI aggregate code stored in workflows."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = {"id": 123456789, "full_name": "Cyber-preacher/kavazi-method"}
FORK = {"id": 987654321, "full_name": "contributor/kavazi-method"}


def workflow_python(filename):
    """Read the single Python step without adding a YAML runtime dependency."""
    body = (ROOT / ".github/workflows" / filename).read_text(encoding="utf-8")
    marker = "        shell: python\n        run: |\n"
    if body.count(marker) != 1:
        raise AssertionError(f"Expected one inline Python step in {filename}")
    lines = []
    for line in body.split(marker, 1)[1].splitlines():
        if line and not line.startswith("          "):
            break
        lines.append(line)
    return textwrap.dedent("\n".join(lines)) + "\n"


def pull_event(head="feature/puzzle", base="dev", fork=False):
    return {
        "action": "opened",
        "repository": deepcopy(REPOSITORY),
        "pull_request": {
            "head": {"ref": head, "sha": "a" * 40, "repo": deepcopy(FORK if fork else REPOSITORY)},
            "base": {"ref": base, "sha": "b" * 40, "repo": deepcopy(REPOSITORY)},
        },
    }


class PullRequestRouteTests(unittest.TestCase):
    def run_route(self, event, extra_env=None, raw=None):
        with tempfile.TemporaryDirectory(prefix="kavazi-ci-route-") as directory:
            event_path = Path(directory) / "event.json"
            event_path.write_text(json.dumps(event) if raw is None else raw, encoding="utf-8")
            env = {
                **os.environ,
                "GITHUB_EVENT_NAME": "pull_request_target",
                "GITHUB_EVENT_PATH": str(event_path),
                "GITHUB_REPOSITORY_ID": str(REPOSITORY["id"]),
                "GITHUB_REPOSITORY": REPOSITORY["full_name"],
            }
            env.update(extra_env or {})
            return subprocess.run(
                [sys.executable, "-c", workflow_python("pr-route.yml")],
                cwd=directory, env=env, capture_output=True, text=True, timeout=5,
            )

    def test_contributor_branches_and_forks_can_target_dev(self):
        for fork in (False, True):
            for head in ("feature/puzzle", "fix/phase-check", "dev"):
                with self.subTest(fork=fork, head=head):
                    result = self.run_route(pull_event(head=head, fork=fork))
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_master_accepts_only_same_repository_dev(self):
        for head, fork, accepted in (
            ("dev", False, True),
            ("dev", True, False),
            ("feature/puzzle", False, False),
            ("feature/puzzle", True, False),
            ("master", False, False),
        ):
            with self.subTest(head=head, fork=fork):
                result = self.run_route(pull_event(head=head, base="master", fork=fork))
                self.assertEqual(accepted, result.returncode == 0, result.stdout + result.stderr)

    def test_other_destinations_and_untrusted_event_types_fail(self):
        for base in ("main", "release", "MASTER", ""):
            with self.subTest(base=base):
                self.assertNotEqual(0, self.run_route(pull_event(base=base)).returncode)
        self.assertNotEqual(0, self.run_route(pull_event(), {"GITHUB_EVENT_NAME": "pull_request"}).returncode)

    def test_retargeting_rechecks_the_destination(self):
        event = pull_event(fork=True)
        event["action"] = "edited"
        self.assertEqual(0, self.run_route(event).returncode)
        event["pull_request"]["base"]["ref"] = "master"
        self.assertNotEqual(0, self.run_route(event).returncode)

    def test_missing_deleted_and_malformed_branch_metadata_fail(self):
        for side in ("head", "base"):
            for field in ("repo", "ref", "sha"):
                for value in (None, {}, [], False, ""):
                    with self.subTest(side=side, field=field, value=value):
                        event = pull_event()
                        event["pull_request"][side][field] = value
                        self.assertNotEqual(0, self.run_route(event).returncode)
        for invalid in (None, [], {}, {"pull_request": None}, {"repository": REPOSITORY, "pull_request": []}):
            with self.subTest(event=invalid):
                self.assertNotEqual(0, self.run_route(invalid).returncode)
        self.assertNotEqual(0, self.run_route(None, raw="{malformed JSON").returncode)

    def test_repository_identity_cannot_be_spoofed_by_name(self):
        for location in ("repository", "head", "base"):
            for field, value in (("id", FORK["id"]), ("full_name", FORK["full_name"]), ("id", True), ("id", "123456789")):
                with self.subTest(location=location, field=field, value=value):
                    event = pull_event(head="dev", base="master")
                    repo = event["repository"] if location == "repository" else event["pull_request"][location]["repo"]
                    repo[field] = value
                    self.assertNotEqual(0, self.run_route(event).returncode)
        for variable in ("GITHUB_REPOSITORY", "GITHUB_REPOSITORY_ID"):
            with self.subTest(variable=variable):
                self.assertNotEqual(0, self.run_route(pull_event(), {variable: ""}).returncode)

    def test_contributor_text_is_data_and_is_not_echoed_as_workflow_commands(self):
        with tempfile.TemporaryDirectory(prefix="kavazi-ci-injection-") as directory:
            marker = Path(directory) / "should-not-exist"
            payload = f"$(touch {marker})`touch {marker}`\n::notice::untrusted"
            event = pull_event(head=payload, fork=True)
            event["pull_request"]["title"] = payload
            event["pull_request"]["body"] = payload
            result = self.run_route(event)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertNotIn(payload, result.stdout + result.stderr)
            self.assertFalse(marker.exists())
            event["pull_request"]["base"]["ref"] = "master"
            result = self.run_route(event)
            self.assertNotEqual(0, result.returncode)
            self.assertNotIn(payload, result.stdout + result.stderr)
            self.assertFalse(marker.exists())

    def test_pr_authorship_does_not_grant_merge_authority(self):
        event = pull_event(head="dev", base="master")
        event["sender"] = {"login": "contributor"}
        event["pull_request"]["user"] = {"login": "contributor"}
        self.assertEqual(0, self.run_route(event).returncode)


class AggregateCITests(unittest.TestCase):
    def test_only_a_successful_matrix_passes_the_required_gate(self):
        for result in ("success", "failure", "cancelled", "skipped", "", "Success", "success\n"):
            with self.subTest(result=result):
                completed = subprocess.run(
                    [sys.executable, "-c", workflow_python("validate.yml")],
                    env={**os.environ, "VALIDATION_RESULT": result},
                    capture_output=True, text=True, timeout=5,
                )
                self.assertEqual(result == "success", completed.returncode == 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
