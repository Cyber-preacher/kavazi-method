# Phase 03 — Protected branch workflow and first release

[Master plan](../../MASTER_IMPLEMENTATION_PLAN.md) · [Methods](METHODOLOGY.md) · [Evidence](EVIDENCE.md). `.kavazi/state.json` owns status and next action.

## Outcome and scope

Create `Cyber-preacher/kavazi-method` as the public source repository. Use `dev` as the contribution target and `master` as stable promotion branch. Only David's verified account may merge either protected branch; master accepts only same-repository dev. Prepare and observe CI on contributor-to-dev and dev-to-master PRs. Preserve prior phase history and target-project behavior. The later explicit user request adds the first v0.1.0 release, downloadable asset, and verified public link.

## Work and acceptance

- [x] P03-01: Capture user direction and reconcile design, method, and technical owners.
- [x] P03-02: Implement and test route validation and required CI on both PR targets.
- [x] P03-03: Define exact owner-only update rules independently of mandatory PR/check/no-force/no-delete rules.
- [x] P03-04: Document contribution, promotion, sync, and maintenance; direct Dependabot to dev.
- [x] P03-05: Create and populate the public repository; establish dev/master, apply settings, and verify remote rules and CI behavior.
- [x] P03-06: Publish v0.1.0 from accepted master, upload the reproducible archive, and verify the public release and downloaded asset.
- [x] P03-BH: Inspect the full delivered scope and inherited interactions, resolve findings, justify refactors, and freshly review until clean.
- [x] P03-HANDOFF: Reconcile records, distinguish local/static checks from remote observations, and record a supported baseline and closure.

Both required local checks must pass. Acceptance includes live rule read-back and observed positive CI on both targets plus an invalid master route rejected by its gate. A test using the owner's credentials cannot establish rejection of another actual user's merge attempt. Do not weaken protections to manufacture a passing result. Keep test PRs clearly identified and preserve production source.

## Verified delivery

Public release: [v0.1.0](https://github.com/Cyber-preacher/kavazi-method/releases/tag/v0.1.0), tagged at accepted master `37931e3220885a38530676748529b891d6b89c87`. The 26-member ZIP and checksum file were downloaded without authentication and match the source-built archive. Owner-only branch rules remain active, qualified CI passed on both PR targets, and invalid promotion probes were closed without merging. Local final checks ran 113 tests: 112 passed and one host-prohibited socket fixture skipped.

The same-head, cross-target probe revealed a GitHub merge-evaluation discrepancy even after the qualified results were green. A fresh evidence-only head passed and merged normally; the host-side cause is unconfirmed. Required checks and owner safeguards were never disabled to force a merge. Another user's actual merge attempt and additional platforms remain unobserved. The ledger owns formal closure.
