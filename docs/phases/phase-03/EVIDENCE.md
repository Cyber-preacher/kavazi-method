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
