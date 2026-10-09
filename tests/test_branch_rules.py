"""Protect hosting-policy boundaries; these checks do not apply GitHub settings."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BranchRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policies = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in (ROOT / ".github/rulesets").glob("*.json")
        }

    def test_only_dev_and_master_are_restricted(self):
        self.assertEqual(set(self.policies), {"owner-merges", "dev", "master"})
        targets = {
            "owner-merges": {"refs/heads/dev", "refs/heads/master"},
            "dev": {"refs/heads/dev"},
            "master": {"refs/heads/master"},
        }
        for name, policy in self.policies.items():
            with self.subTest(policy=name):
                self.assertEqual(policy["target"], "branch")
                self.assertEqual(policy["enforcement"], "active")
                condition = policy["conditions"]["ref_name"]
                self.assertEqual(set(condition["include"]), targets[name])
                self.assertEqual(condition["exclude"], [])

    def test_owner_can_only_bypass_the_merge_actor_restriction(self):
        owner = self.policies["owner-merges"]
        self.assertEqual(owner["bypass_actors"], [{
            "actor_id": 72062250,
            "actor_type": "User",
            "bypass_mode": "pull_request",
        }])
        self.assertEqual(owner["rules"], [{
            "type": "update",
            "parameters": {"update_allows_fetch_and_merge": False},
        }])
        for branch in ("dev", "master"):
            with self.subTest(branch=branch):
                policy = self.policies[branch]
                self.assertEqual(policy["bypass_actors"], [])
                types = [rule["type"] for rule in policy["rules"]]
                self.assertEqual(len(types), len(set(types)), "Duplicate rules")
                self.assertEqual(set(types), {
                    "deletion", "non_fast_forward", "pull_request",
                    "required_status_checks",
                })

    def test_ci_and_route_are_both_mandatory_from_github_actions(self):
        for branch in ("dev", "master"):
            with self.subTest(branch=branch):
                rules = {rule["type"]: rule for rule in self.policies[branch]["rules"]}
                checks = rules["required_status_checks"]["parameters"]
                self.assertTrue(checks["strict_required_status_checks_policy"])
                self.assertFalse(checks["do_not_enforce_on_create"])
                self.assertEqual(checks["required_status_checks"], [
                    {"context": "CI", "integration_id": 15368},
                    {"context": "PR route", "integration_id": 15368},
                ])

    def test_long_lived_branches_keep_ancestry_without_self_approval(self):
        for branch in ("dev", "master"):
            with self.subTest(branch=branch):
                rules = {rule["type"]: rule for rule in self.policies[branch]["rules"]}
                pr = rules["pull_request"]["parameters"]
                self.assertEqual(pr["allowed_merge_methods"], ["merge"])
                self.assertNotIn("required_linear_history", rules)
                self.assertEqual(pr["required_approving_review_count"], 0)
                self.assertFalse(pr["require_code_owner_review"])
                self.assertFalse(pr["require_last_push_approval"])
                self.assertTrue(pr["required_review_thread_resolution"])
                self.assertTrue(pr["dismiss_stale_reviews_on_push"])


if __name__ == "__main__":
    unittest.main()
