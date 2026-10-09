# Historical skill wording — archive

Archived during open-source preparation on 2026-10-09. This document records an earlier design and its observations; it does not govern current work. Read the [current Core](../../CORE_KAVAZI_METHOD.md) and [Master Implementation Plan](../MASTER_IMPLEMENTATION_PLAN.md) for the live method and sequence.

Former location: `HISTORICAL_SKILL.md`. Its pre-relocation SHA-256 was `287da45d9c2c049634c12d87f99a97c4897c589f3eb277041c6b7fc94d16fda7`. This archive adds this notice and repairs relative links; historical statements remain as recorded. A statement about missing tools or an undecided license describes that earlier point in development.

---

---
name: kavazi-method
description: Adopt, maintain, or follow the Kavazi Method when the user requests Kavazi or the repository already uses it. Connect canonical architecture, sourced methodology, sequential numbered phases, ongoing decision evidence, and mandatory phase closure reviews. Do not impose this workflow on unrelated repositories or generic development requests.
---

# Kavazi Method

This is the retained historical compatibility entry. For the current operating instructions and tools, follow the [distributable skill](../../skills/kavazi-method/SKILL.md) and the repository's [Core](../../CORE_KAVAZI_METHOD.md). The 2026-10-09 user revision supersedes the earlier document route below: capture user input → Master Architecture → Master Methodology → Master Technical Core → Master Implementation Plan → needed supporting documents → current phase. Default autonomous operation derives missing design decisions and records assumptions; optional phase checkpoints require actual human approval before advancing. The retained sections below preserve the earlier protocol wording and do not override the current Core or selected execution mode.

Use an empirical, rational approach and keep the wider product, users, and system consequences in view. Connect intended outcomes to technical ownership, chosen methods, phased work, and observed results. A plan expresses intent; source code establishes a mechanism; execution evidence supports a bounded behavior claim.

## Scope and entry

- For adoption, establish the document structure and rules below. For an existing Kavazi project, read its root agent instructions and Core Method, locate its canonical masters, and follow the active phase's documents before changing the project.
- Preserve the user's product, existing canonical paths, accepted requirements, source history, and unrelated work. Update existing masters instead of introducing competing copies. Keep current implementation distinct from target design and dated reports.
- Apply the method to the requested work. Creating or editing the method or skill does not itself authorize running a whole-repository audit. An ordinary task inside a phase need not execute its closure gates immediately; formally completing that phase requires them.
- Continue authorized reversible work. A skill invocation does not authorize publication, destructive operations, unrelated redesign, or actions outside existing permissions. If an indispensable decision or execution prerequisite is missing, record the dependency and continue independent work within the current phase.

## Canonical documents

Create or reconcile the masters in this reasoning order. They can evolve as evidence changes; detailed phase packages must be created and executed sequentially.

| Order | Document | Responsibility |
|---|---|---|
| 1 | Core Kavazi Method | Operating rules, document ownership, entry path, closure gates, and recovery when context is lost |
| 2 | Master Architecture | Product rules mapped to technical owners, state, interfaces, lifetimes, data, persistence, runtime flows, and important tradeoffs |
| 3 | Master Methodology | Project-wide approaches, supporting primary sources, project applications, limitations, and suitable verification methods |
| 4 | Master Implementation Plan | Stable numbered development phases, dependencies, current focus, scope, progress, and completion criteria |
| 5 | Current phase package, then the next only after closure | `IMPLEMENTATION_PLAN.md`, `METHODOLOGY.md`, and `EVIDENCE.md` |

Retain an existing detailed architecture companion when it serves a clear purpose. Add or update root `AGENTS.md` instructions linking the Core and this reading order. Explain where an arriving agent can find the current phase and its next action.

For a new repository with no established layout, reasonable defaults are root `CORE_KAVAZI_METHOD.md`, `docs/MASTER_ARCHITECTURE.md`, `docs/MASTER_METHODOLOGY.md`, `docs/MASTER_IMPLEMENTATION_PLAN.md`, and `docs/phases/phase-01/` onward. These are defaults only; preserve established paths. Choose phase count, stack, platforms, and outcomes from the actual project. Do not import another project's roadmap or engine assumptions.

Map old milestones to stable development phase numbers without relabeling inherited work as freshly verified. Phase numbers refer to development phases, not missions, releases, sprints, or the count completed in a session.

For each phase when it becomes eligible for planning:

- **Implementation plan:** outcome, scope, dependencies, concrete work items, functional acceptance criteria, mandatory closure gates, status, and next action.
- **Methodology:** relevant master methods, uncertainties, success/failure scenarios, measurement conditions, checks, and decision criteria. Define meaningful numerical thresholds before measuring when numerical acceptance applies.
- **Evidence:** append decisions and actual observations during development, including failures, review rounds, and reasons for choices. Seed a new file with the phase's provenance and unresolved baseline; do not invent historical execution results.

Use `not_planned` for high-level future roadmap entries with no package. Eligible created phases use `planned`, `in_progress`, `blocked`, and `complete`, or map equivalent existing statuses explicitly. Functional readiness and formal phase completion are separate claims. Keep the master register and phase plan aligned.

## One phase at a time

Keep the future development sequence at a high level in the Master Implementation Plan: intended outcomes, ordering, dependencies, and open scope decisions. **Do not create or draft a future phase's folder, detailed implementation plan, checklist, methodology, or evidence stub**, including conditional drafts stored elsewhere. A high-level roadmap entry is not a phase package.

Create only the current phase's three documents. Before creating the immediately next numbered phase package, finish the current phase in full:

1. Implement its accepted scope and meet its functional acceptance criteria.
2. Complete its clean phase bug hunt/refactoring gate and, on phases 5, 10, 15, and onward, its clean whole-repository gate.
3. Finish and reconcile all relevant documentation: current phase plan, methodology, evidence and closure record; Core/agent instructions when affected; architecture and detailed companions; master methodology; and master roadmap/status/next action. Resolve contradictory claims and stale links. Documentation cannot substitute for implementation or review evidence.
4. Record supported completion, then derive **only the immediately next phase package** from that actual implementation, evidence, lessons, and remaining dependencies.

An open finding, failed or unavailable required check, unfinished relevant document, or blocked current phase prevents both formal completion and later-phase planning. Do not bypass the blockage by writing the next phase's documentation or delegating future work. Parallelize only current-phase tasks. After creating the next package, it becomes the current phase; do not precreate the package after it.

Optional features, release subsets, and alternative sequencing may remain high-level roadmap intentions. They do not permit silently skipping a numbered phase or marking omitted work complete. Resolve a necessary change of agreed phase sequence or scope through an explicit recorded user decision.

If future packages were created prematurely, first distinguish speculative scaffolding from genuine implementation history, decisions, evidence, and user work. Correct navigation and status so premature drafts cannot authorize later execution. Remove unexecuted scaffolding when the requested correction authorizes its removal, and retain useful high-level intentions in the master roadmap. Do not delete genuine historical work without authorization; preserve its provenance as supporting history and record any unresolved cleanup dependency instead of treating a premature package as active or complete.

## Working cycle

1. **Orient:** inspect the revision and working tree; read the Core, current architecture, methodology, master plan, and current phase package. Record cross-system effects in the current phase and link relevant historical evidence.
2. **Frame:** state the intended outcome, existing behavior, relevant product/source decision, technical owner, dependencies, and smallest useful acceptance check. Separate facts, assumptions, proposals, and unresolved questions.
3. **Decide and implement:** record consequential alternatives and tradeoffs before or alongside the change. Make coherent increments through the relevant input, rule, consequence, and presentation paths. Parallel tasks are allowed only within the current phase and need clear ownership and shared interfaces.
4. **Observe and reconcile:** run checks appropriate to the claim, record actual results and limits, and revise the change or hypothesis when observations disagree. Update architecture or methodology when their contracts change.
5. **Handoff or close:** update evidence, work items, next action, and affected contracts. Before formal closure, finish implementation and functional acceptance, pass all required review gates below, and reconcile all relevant phase and master documents. Only then mark the phase `complete` and create the immediately next phase package from the actual results.

Ground the Master Methodology in relevant research papers, authors' publications, official technical documentation, and experienced practitioners' original work. Verify citations and support each attributed claim. State what the source supports, how the project adapts it, and where its evidence stops. Reputation or a paper's existence does not demonstrate project suitability; do not invent rankings of the world's best developers or scientists.

## Mandatory phase closure gates

Once a phase meets its functional requirements, run a **phase bug hunt and refactoring pass before formal completion**. Review the phase's entire delivered scope and affected integrations against its plan, methodology, architecture, and accepted product rules, including inherited implementation used by the phase.

Every phase whose stable development number is divisible by five—**5, 10, 15, 20, and onward**—also requires a **whole-repository bug hunt and refactoring pass**. This is additional to the phase gate. Review the whole project, including earlier phases and code, assets/content, tests, configuration, build/development tooling, and documentation. The latest diff and the most recent five phases are not the whole-repository scope. Use a coverage inventory and appropriate tools for binary or generated material; reading filenames alone does not establish review of their behavior or contents.

A shared review can satisfy both gates only when its evidence explicitly covers both scopes and all completion conditions. Independent tasks within the current phase may continue while a gate remains open; planning or implementing a later phase may not.

### Review, fix, verify, and review again

For each required review scope:

1. **Inspect:** record scope, revision/dirty state, requirements, coverage, and required checks. Inspect for defects, contract mismatches, integration failures, and justified maintainability improvements. Assign stable IDs to actionable findings and distinguish demonstrated problems from hypotheses.
2. **Fix and refactor:** address actionable findings. Refactoring must have a concrete reason and preserve accepted behavior; document the invariant and verification. Defect fixes restore required behavior and should be identified as fixes. The refactoring pass is mandatory, but a rewrite is not: if no justified refactor is found, record the inspected areas and why no change is warranted.
3. **Verify:** run the required checks and affected regressions against the resulting revision. Verify previous findings' resolutions; rerunning checks does not erase earlier failures. Record checks that fail or cannot run and the missing prerequisite.
4. **Fresh review:** inspect the resulting state across the full required scope again, including interactions and prior finding resolutions, rather than only rereading the patch. Use an independent reviewer when available and useful; otherwise perform a fresh systematic pass. Record the reviewer and actual coverage.
5. **Repeat:** if that review finds any new actionable problem, or earlier actionable findings remain unresolved, return to fixing/refactoring, verification, and another fresh review. Do not substitute an arbitrary round count for the exit condition.

A gate is clean only when **the final fresh review finds no new actionable findings, no earlier actionable findings remain unresolved, coverage is accounted for, and all required checks pass for the reviewed state**. Explain evidence that dismisses a false positive; merely deferring, accepting the risk of, or lowering the severity of an actionable finding does not resolve it. Required unavailable checks keep the gate open and must not be reported as passed or clean. Work needing a missing product decision or permission remains open while independent authorized work within the current phase proceeds.

Only mark the phase complete after implementation and functional acceptance, its clean phase gate, its additional clean whole-repository gate when applicable, and reconciliation of all relevant phase/master documentation are supported by evidence. An apparently clean review is a scoped observation for a revision and procedure, not a guarantee that the repository contains no bugs. Reopen affected acceptance when a later change or finding invalidates it.

## Evidence and review records

Use stable entry IDs and dates, proportionate to the work. Record:

- Context, linked requirement/work item, question or expected result.
- Alternatives, decision, reason, tradeoffs, and wider-system consequences.
- Revision and relevant uncommitted changes, environment, tool versions, inputs, and seed when relevant.
- Reproducible command or manual procedure; actual observations, artifacts, failures, and unavailable checks.
- Conclusion, limits, follow-up owner/action, and trigger for reconsidering the decision.

For each closure review round, additionally record scope/coverage, reviewer, finding IDs and status, why each fix/refactor was made or omitted, preserved behavior, verification results, and the fresh review's outcome. Maintain visibility of unresolved findings across rounds. Link the final clean round from the phase plan and master register. Store whole-repository rounds in the closing fifth phase's `EVIDENCE.md`, with links to affected historical phases rather than competing evidence masters or newly drafted future packages.

Keep prior conclusions and failures; append a dated correction or superseding entry. Source inspection, compilation, tests, user observations, performance measurements, and release checks establish different things. Never present old reports, unavailable artifacts, or unexecuted procedures as fresh observations.

## Recovery and adoption verification

When context is lost, return to the Core, locate the responsible master, read current phase evidence and its next action, then compare the actual checkout with the recorded baseline. Resolve contradictions by requirement provenance and the smallest discriminating check; preserve unresolved uncertainty.

For a documentation-only adoption or methodology update, verify canonical links, current/historical phase packages, sequential eligibility, status agreement, source attribution, and diff consistency. Record the new gate rules as requirements, leaving unperformed bug hunts, refactors, and runtime checks explicitly open. Report the delivered documentation separately from product or phase completion.
