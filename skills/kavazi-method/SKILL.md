---
name: kavazi-method
description: Adopt or follow Kavazi in a requested or already adopted repository. Turn a brief into project design and implementation through sequential phases, recorded evidence, and full reviews, with optional human checkpoints.
license: MIT
---

# Kavazi Method

Carry the user's intent through design, code, and observed results. Use an empirical, rational approach: a plan states intent, code defines a mechanism, and execution shows what happened under specific conditions. Keep the wider product and system consequences in view.

## Enter the project

Read applicable agent instructions and Core, then follow this route:

Project Brief → Master Architecture → Master Methodology → Master Technical Core → Master Implementation Plan → needed supporting documents → current phase's `IMPLEMENTATION_PLAN.md`, `METHODOLOGY.md`, and `EVIDENCE.md`.

Core governs the route. `.kavazi/config.json` locates the documents and sets the execution mode; `.kavazi/state.json` owns phase status and next action. Compare the recorded baseline with the actual checkout. Preserve user work, established paths, accepted requirements, and dated evidence.

For a new adoption, read [adoption](references/adoption.md) and inspect existing project documents before creating their Kavazi counterparts. Preview the integration, then apply it:

```text
python3 <this-skill>/scripts/kavazi.py init --repo <project> --project "Project name" --prompt "Build the requested project" --dry-run
python3 <this-skill>/scripts/kavazi.py init --repo <project> --project "Project name" --prompt "Build the requested project"
```

Replace `<this-skill>` with this skill's actual directory. Use `--brief-file` for a larger specification, or `--mode phase_checkpoint` for human approval between phases. After adoption, the tool lives at `.agents/skills/kavazi-method/scripts/kavazi.py`. Generated documents are starting points: fill them with the project's actual design. Reconcile inherited history explicitly before relying on it.

## Derive the project and choose its execution mode

Preserve the supplied input exactly, whether it is one sentence or several pages. Define a complete, achievable project within that request. Make routine product, design, and technical choices yourself using repository evidence and relevant primary sources. Continue toward a usable finished product; stop at an MVP only when that is the requested outcome.

Keep explicit user requirements, agent assumptions, and observed facts distinct. For consequential choices, record alternatives, reasons, wider consequences, and what would make you reconsider. An assumption supplies a missing design decision; it cannot supply a user preference, a test result, or unrelated scope.

Develop the documents in order. Architecture defines project logic and required behavior. Methodology explains how to develop and verify it. Technical Core connects each requirement to concrete components, interfaces, data, algorithms, failure handling, and checks. The master plan sequences implementation. Add supporting documents when they have a distinct purpose, and detail only the current phase.

In default `autonomous` mode, continue authorized work through fully reviewed phases without routine design questions. In `phase_checkpoint`, do the same work within the phase, close it fully, then stop before creating its successor. Advance only after actual human approval is recorded with `approve`. Never self-approve.

Honor user steering and pauses in either mode. Permissions, credentials, external prerequisites, and host execution limits still apply. Record a concrete blocker and continue independent work in the current phase. Prompt-and-forget depends on the host's ability to keep the agent running.

## Work within one phase

1. Read the requirements, technical owners, current evidence, and actual working tree.
2. Define the intended outcome and the smallest check that can distinguish success from failure.
3. Record consequential decisions before or alongside implementation. Give parallel tasks explicit file ownership within this phase.
4. Run appropriate checks and record actual results, failures, and limits. Update affected contracts when evidence changes them.
5. Bring work items and next action up to date, or complete the closure process below.

Keep records proportionate: a small fix may need one dated entry. Append corrections instead of erasing failures or earlier conclusions. Source inspection, tests, compilation, runtime observations, and measurements support different claims. Record only execution and reviewer settings actually observed. Explain how primary sources apply to this project and where their support ends.

## Close the phase before advancing

Only one created phase may be unfinished. Future entries remain `not_planned`, with high-level outcomes and no folders or detailed drafts, including drafts saved elsewhere. After full closure, create only the immediate successor. Preserve stable numbers and history. You may revise an agent-derived roadmap from evidence; changing explicit user scope or order requires actual user direction.

Completion requires implemented scope, functional acceptance, passing required checks, a phase bug hunt and justified refactoring pass, and reconciled project documents. Phases 5, 10, 15, and onward also require a whole-repository pass covering inherited implementation, integrations, code, assets, tests, tooling, configuration, and documentation.

For each required scope, record coverage and stable finding IDs, fix actionable findings, justify refactors, preserve accepted behavior, and verify the result. Then perform a fresh review of the entire scope. Repeat until no new actionable findings appear, all prior findings are resolved, coverage is accounted for, and required checks pass on the reviewed state. Record when no refactor is warranted. A fifth-phase review can satisfy both scopes only when its evidence explicitly covers both.

Open findings, indispensable missing prerequisites, failed or unavailable required checks, incomplete documents, and stale acceptance keep closure open. Deferral or accepted risk does not resolve an actionable finding. Later substantive changes reopen affected acceptance and review.

Read [the complete Core](references/core-method.md) for review scope, recovery, and inherited-package reconciliation. Read [records](references/records.md) before recording closure or advancing. Structural validation checks the records; actual product checks and thoughtful review establish the result.

## Local commands

```text
python3 .agents/skills/kavazi-method/scripts/kavazi.py status --repo .
python3 .agents/skills/kavazi-method/scripts/kavazi.py check --repo .
python3 .agents/skills/kavazi-method/scripts/kavazi.py doctor --repo .
```

These commands inspect the repository; they never run configured project checks. Run those checks separately. The [record guide](references/records.md) covers `snapshot`, `sync`, `close`, `approve`, and `next`. The tools cannot authenticate a recorded human approval or perform the review described in an evidence entry. Adoption does not authorize publication, destructive actions, unrelated redesign, or permission changes.
