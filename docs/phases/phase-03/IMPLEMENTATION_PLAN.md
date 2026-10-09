# Phase 03 — Protected branch workflow and CI

[Master plan](../../MASTER_IMPLEMENTATION_PLAN.md) · [Methods](METHODOLOGY.md) · [Evidence](EVIDENCE.md). `.kavazi/state.json` owns status and next action.

## Outcome and scope

Create `Cyber-preacher/kavazi-method` as the public source repository. Use `dev` as the contribution target and `master` as stable promotion branch. Only David's verified account may merge either protected branch; master accepts only same-repository dev. Prepare and observe CI on contributor-to-dev and dev-to-master PRs. Preserve prior phase history and target-project behavior. The later explicit user request adds the first v0.1.0 release, downloadable asset, and verified public link.

## Work and acceptance

- [x] P03-01: Capture user direction and reconcile design, method, and technical owners.
- [x] P03-02: Implement and test route validation and required CI on both PR targets.
- [x] P03-03: Define exact owner-only update rules independently of mandatory PR/check/no-force/no-delete rules.
- [x] P03-04: Document contribution, promotion, sync, and maintenance; direct Dependabot to dev.
- [ ] P03-05: Create and populate the public repository; establish dev/master, apply settings, and verify remote rules and CI behavior.
- [ ] P03-06: Publish v0.1.0 from accepted master, upload the reproducible archive, and verify the public release and downloaded asset.
- [ ] P03-BH: Inspect the full delivered scope and inherited interactions, resolve findings, justify refactors, and freshly review until clean.
- [ ] P03-HANDOFF: Reconcile records, distinguish local/static checks from remote observations, and record a supported baseline and closure.

Both required local checks must pass. Acceptance includes live rule read-back and observed positive CI on both targets plus an invalid master route rejected by its gate. A test using the owner's credentials cannot establish rejection of another actual user's merge attempt. Do not weaken protections to manufacture a passing result. Keep test PRs clearly identified and preserve production source.
