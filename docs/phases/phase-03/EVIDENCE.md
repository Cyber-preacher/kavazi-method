# Phase 3 Evidence

Keep a dated account of decisions, observations, failures, reviews, and corrections. Use [Project Brief](../../PROJECT_BRIEF.md), [Master Technical Core](../../MASTER_TECHNICAL_CORE.md), the [phase plan](IMPLEMENTATION_PLAN.md), and [methodology](METHODOLOGY.md) as context.

## P03-E001 — Package established

- Date: 2026-10-09.
- Context: Kavazi Method; Protected branch workflow and CI.
- Intended outcome: Create the public GitHub repository, prepare contributor branches to dev and same-repository dev to master, restrict merging to David, and verify CI and hosting rules.
- Procedure and observation: Kavazi created the eligible current-phase package. Project-specific design, required checks, implementation, acceptance, and reviews remain to be established from actual context and execution.
- Decision: preserve existing work and dated history. Onboarding establishes no completed development or passing check.
- Limit: creating templates does not demonstrate accepted design, product behavior, or phase closure.
- Next action: read the project documents and actual checkout, make routine missing choices with labeled assumptions, define scope and checks, and append observed results.

## Evidence format

Give entries stable IDs such as `P03-E002` and an actual date. Record the requirement or question, consequential alternatives and decision, rationale, baseline and environment, reproducible procedure, observations, artifacts, failures, conclusion, limits, and follow-up. Keep entries proportionate to the work. Distinguish user requirements, agent choices, and observed facts; append corrections instead of erasing failures.

For reviews, also record full scope and coverage, actual reviewer settings when known, stable finding IDs and statuses, fix or refactor rationale, preserved behavior, verification, and fresh-review result. Keep fifth-phase whole-repository evidence here and link affected history. Enter closure claims only after observations support them.

Evidence IDs must be live visible Markdown headings. Examples inside fences, comments, or raw HTML cannot support closure records.

In checkpoint mode, after full closure add an entry recording actual human approval and its context before using `approve`. Never self-approve or label an agent choice as human approval. The approval record documents direction; it cannot authenticate who gave it.

## P03-E002 — Authorized repository and branch design

Date: 2026-10-09. The user requested contributor branches to dev, dev only to master, owner-only merges for both, and CI on both routes. The user then explicitly authorized creating the repository. Root selected public `Cyber-preacher/kavazi-method`, matching the open-source context, and dev as the default contribution branch. The connected profile and a successful authenticated CLI `GET /user` independently identify `Cyber-preacher`, numeric ID `72062250`. No email or credentials are needed in project records.

This authoring directory is not a Git checkout. An initial sandboxed `gh auth status` reported an invalid token; the authenticated read succeeded with network access, so that report was a restricted-network observation, not evidence that credentials need replacement. `GET /repos/Cyber-preacher/kavazi-method` returned 404 before creation. `GET /apps/github-actions` returned app ID `15368`. Protected environment metadata remains untouched; publication will use a temporary source export.

The previous Phase 02 closure validated at its recorded baseline before any edits. Source `next --dry-run` and `next` created exactly Phase 03 successfully. Earlier phase records retain their accepted history.

Design: exact-user PR-only update bypass, independent no-bypass PR/CI/destructive-update rules, metadata-only trusted route check, read-only merge-candidate CI, and zero formal required approvals so the owner is not required to self-approve. Fork contributions are the default. Rule files describe desired settings; live read-back and workflow observations remain pending. Root owns project records and hosting, branch_ci owns workflows/tests, branch_policy_review owns rules/tests and independent review, branch_docs owns public branch guidance/CODEOWNERS/Dependabot/PR template.

## P03-E003 — Public repository created

Date: 2026-10-09. The authorized `POST /user/repos` succeeded, creating public `https://github.com/Cyber-preacher/kavazi-method`, repository ID `1412079071`, with the authenticated account holding admin access. It is initially empty; the API returned the placeholder default branch main. No main branch was seeded. Source export, master/dev creation, dev default selection, live rules, and CI observations follow. No tagged release or asset upload occurred.

## P03-E004 — Local verification before source upload

Date: 2026-10-09. Root's required suite ran 111 tests in 15.086 seconds: 110 passed and one optional host-prohibited Unix-socket fixture skipped (`/tmp/kavazi-branch-regressions.log`). The required structural check and archive build passed. Nine new tests exercise the exact route and aggregate workflow programs; four policy tests cover actor restriction, target scope, independent safeguards, required checks, and ancestry-preserving merge methods. The independent reviewer ran the same 111 tests in 14.935 seconds with the same result and passed structural validation.

Local review covers route/aggregate code, pinned actions and read-only/no-checkout boundaries, tests, three branch rule payloads, and contribution/sync procedures. The initial documentation described two rulesets despite three files; the author is correcting it to three rulesets in two independent layers. The workflow comment was clarified to trusted base repository. No runtime or policy defect was found locally; live check attachment and server acceptance remain unobserved.

Hosting configuration so far: active Actions event policy ID `6998` permits push, pull_request, and pull_request_target. The API accepted it, so the metadata-only workflow has an explicit event policy. Repository settings enable merge commits, disable squash/rebase/auto-merge and automatic branch deletion, and set default workflow token permission to read with action review approval disabled. No branch content was uploaded at this observation.

## P03-E005 — Workflow publication requires GitHub authorization

Date: 2026-10-09. Root exported 68 selected source files into an isolated temporary Git checkout, excluding protected environment metadata, build output, and caches. Staged-path inspection and `git diff --cached --check` passed. Local initial source commit: `dceb1cae85e9f5d96aa486aa7d4e87e9a09da504`.

The initial push of master was rejected because the authenticated CLI OAuth grant lacks the workflow scope required to publish `.github/workflows/pr-route.yml`. A subsequent branch-list read returned no branches. The connected GitHub app could read repository metadata but its supported workflow content write also returned HTTP 403, Resource not accessible by integration. Neither failure establishes source publication or live CI. Root initiated GitHub's supported device authorization flow requesting the workflow scope, and asked the user to authorize it. No credential or device code is stored in project records.

Local reviewed files, public repository creation, and existing settings remain available. Branch seeding, protection activation, remote CI, and final acceptance depend on that external authorization.

**Staged rule validation:** While workflow authorization is pending, GitHub accepted owner rule ID `24799639` with exact `User` actor `72062250` and `pull_request` bypass, dev safeguard ID `24799646`, and master safeguard ID `24799648`. All three were explicitly submitted with disabled enforcement during bootstrap. Returned safeguards require CI and PR route from app 15368, strict up-to-date history, merge commits, zero formal approvals, and no bypass actors. No actor-role fallback is needed. A scoped credential-marker scan of all 68 selected source files found no private-key blocks or common GitHub/AWS credential patterns; this is a bounded inspection, not a universal secret-detection guarantee.

## P03-E006 — Local review while hosting authorization is pending

Date: 2026-10-09. Independent `oss_audit` inspected both exact embedded workflow programs and tests, all three rulesets, the event policy, CODEOWNERS/Dependabot/PR guidance, canonical and phase records, contributor/promotion/sync instructions, and inherited package/validation interactions. It found no actionable local defect. Static checks resolved local navigation in 32 Markdown files and passed repository validation. All 26 distributed archive members match source; two root builds are byte-identical with SHA-256 `960e283da37f9c470bc179d8b1a164ded4902e43fdb68fd36dc52c9913f2a506`.

Actual reviewer model and effort settings are unobserved. This is local implementation review, not a claim that hosting acceptance or the phase is complete. Device authorization remains pending; branches are unpublished, branch rules staged disabled, and remote CI/check attachment unperformed. Phase 03 stays open with a concrete next action in the ledger.

**Independent resulting checks:** `oss_audit` completed the full suite: 111 tests ran, 110 passed, one host-prohibited socket fixture skipped. Log: `/tmp/kavazi-phase3-audit-dcrek1it/regressions.log`. Its final local review remains clean, with no additional justified refactor. Remote acceptance dependencies remain pending; no closure is recorded.

## P03-E007 — First release authorized

Date: 2026-10-09. The user requested that the project be released and asked for its link. Root extended the current hosting phase to include version v0.1.0, a stable-source tag, downloadable archive, and actual public release verification. Earlier observations saying no release was requested describe the earlier scope; this explicit direction supersedes that boundary. The package version is already 0.1.0, so no version migration is needed.

A fresh authenticated API response still reports CLI OAuth scopes gist, read:org, repo without workflow. The existing GitHub device authorization process is still pending; no source upload or branch CI success is inferred. Root continues independent release preparation while that external approval remains required.

## P03-E008 — Source, branches, and safeguards published

Date: 2026-10-09. The user confirmed GitHub device authorization. The refresh process completed, and authenticated API headers now include workflow scope. Source upload succeeded at `9c9f662fe2316aafa227ef9b65898cf395e1b12f`. Root created dev from that master revision and selected dev as the default branch.

GitHub activated owner rule `24799639`, dev safeguards `24799646`, and master safeguards `24799648` from the reviewed JSON files. The response retains exact User `72062250` with PR-only bypass only in the update restriction. Independent safety rules have no bypass actors. Private vulnerability reporting was enabled and read back as true. No release has yet been published.

Initial real push CI passed on master (`https://github.com/Cyber-preacher/kavazi-method/actions/runs/37954651399`) and dev (`https://github.com/Cyber-preacher/kavazi-method/actions/runs/37954691758`). The next branch prepares final release-facing guide text and observed hosting records; those guide links name the intended v0.1.0 destination, while actual tag/asset publication remains a subsequent acceptance step. Functional CI on both PR routes and a negative source-route check follow under active rules.

## P03-E009 — Live PR route finding

Date: 2026-10-09. Root opened release-preparation PR 1 to dev and temporary draft PR 2 from the same topic to master. Both share head `ab57085621f47fedf46b75f99fd464393a28a321`. The trusted route run for PR 1 passed (`37954915631`), while PR 2's run correctly failed (`37954919651`). However, `gh pr checks` for both PRs displayed the most recent failing PR route and the same CI results.

**F031 — required-check context collision:** GitHub associates these checks with the commit, so a single context name reused across different targets contaminates route results. Root assigned target-qualified names (`CI / dev`, `CI / master`, `PR route / dev`, `PR route / master`) to separate the mandatory requirements. A short migration must preserve the legacy checks until the trusted default-branch workflow carries the new ones, then update live safeguards and remove the compatibility aliases. The invalid PR is closed without merging. No protection is disabled to bypass this finding, and no release is published before it is resolved and reviewed.

## P03-E010 — Qualified checks activated

Date: 2026-10-09. Root's resulting local suite ran 113 tests in 18.841 seconds: 112 passed, one optional host socket fixture skipped (`/tmp/kavazi-release-f031-tests.log`). Focused workflow tests verify that shared-head PRs receive different target-specific names and that push/PR target names agree. The independent reviewer inspected the migration and found no additional defect: it emits only the actual target's qualified context, never a skipped opposite-target context.

PR 1 at `7bb8b5d1f2e64f9af20fff71b78d56dfe899a53a` passed actual Python 3.10/3.13 checks, legacy CI, qualified CI / dev, and the trusted legacy PR route. Runs: `37955281760` (validation) and `37955278350` (route). Root merged it using the authenticated owner and the expected head SHA through the normal GitHub merge endpoint; no administrative override flag or disabled safeguards were used. Merge revision: `bb6756ec16a3aa56d96849e00681fd5bb0080fd6`.

The existing safeguard rules `24799646` and `24799648` were updated in place, still active, to require CI / dev plus PR route / dev, and CI / master plus PR route / master, respectively. All remain bound to GitHub Actions app 15368; PR, owner, no-force, and no-delete requirements remain active. The trusted default branch now supplies qualified route checks. The next reviewed change removes temporary aliases and renews the same-head positive/negative observation before the stable promotion and release.
