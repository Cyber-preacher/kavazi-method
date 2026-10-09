# Core Kavazi Method

Version 0.1.0 · established 2026-10-09.

Carry the user's intent into working software. Keep the reasoning visible, and let evidence decide what is done.

Kavazi uses an empirical, rational approach: distinguish the outcome you want, the mechanism you built, and the behavior you actually observed. Consider the wider product and system consequences. Preserve requirements, existing work, and dated evidence.

## From input to implementation

The Core governs the method. Develop and read the project documents in this order after [AGENTS.md](AGENTS.md):

| Order | Document | Question it answers |
|---|---|---|
| 1 | [Project Brief](docs/PROJECT_BRIEF.md) | What did the user ask for, and where did each requirement come from? |
| 2 | [Master Architecture](docs/MASTER_ARCHITECTURE.md) | What must the project do, and what rules connect its parts? |
| 3 | [Master Methodology](docs/MASTER_METHODOLOGY.md) | How will we develop it and judge whether it works? |
| 4 | [Master Technical Core](docs/MASTER_TECHNICAL_CORE.md) | Which components, interfaces, data, and algorithms realize that logic? |
| 5 | [Master Implementation Plan](docs/MASTER_IMPLEMENTATION_PLAN.md) | In what sequence will we build it? |
| 6 | Supporting documents, where needed | What further detail has a distinct purpose? |
| 7 | Current phase: plan, methodology, evidence | What are we doing now, how will we check it, and what happened? |

These are the authoritative documents: update their existing paths rather than creating competing masters. They evolve as evidence changes. `.kavazi/config.json` maps their paths and the execution mode. `.kavazi/state.json` owns phase status and next action; the master plan's generated register displays that state.

[The initial proposal](docs/history/initial-proposal.md) records the original research. [The historical skill](docs/history/original-skill.md) preserves the earlier instructions. Both are history; use the current documents above for execution.

## Start with the input you have

A brief can be one sentence or several pages. Preserve the supplied text, then derive a complete project within a stated scope. For example, “create this game fully” needs a playable experience and a clear finish condition, with the missing game rules chosen and recorded by the agent.

Make routine product, design, and technical choices yourself using project context, repository evidence, and relevant primary sources. Label those choices as assumptions, with reasons, significant alternatives, and a trigger for reconsideration. Keep them separate from user requirements and observed facts. Do not invent user decisions or expand into unrelated work.

Revise an agent-derived high-level roadmap when evidence warrants it. Preserve stable phase numbers, history, and the current phase's detail. Changing scope or order explicitly required by the user needs actual user direction.

## Choose how the agent continues

| Mode | Within a phase | After the phase closes |
|---|---|---|
| `autonomous` — default | Derive missing design details, implement, check, and review | Continue into the immediately next phase toward the authorized finished product |
| `phase_checkpoint` | The same autonomous work | Stop; create the successor only after actual human approval is recorded |

Both modes avoid routine design questions and honor later user steering or pause requests. Continue toward usable software; stop at a scaffold or MVP only when that is the requested outcome.

In checkpoint mode, finish acceptance, checks, reviews, and documentation before asking for advancement approval. Capture the actual approval in current-phase evidence and record it with `approve`. Never self-approve. The command stores an attestation; it cannot authenticate the person behind it.

Autonomy operates within real permissions and available tools. Credentials, indispensable external access, missing execution prerequisites, or host time and context limits can prevent further work. Record the concrete limitation and continue independent authorized work where possible.

## Work and learn

1. **Orient:** read the project contracts and current evidence; compare them with the actual checkout.
2. **Frame:** state the outcome and choose a check that can reveal whether the expected behavior holds.
3. **Decide and build:** record consequential choices before or alongside implementation. Keep parallel tasks in the current phase with explicit ownership.
4. **Observe:** run the relevant checks, preserve failures, and state what each result establishes.
5. **Reconcile:** update affected contracts, current work items, evidence, and next action.

A compact dated entry can be enough for a small change. Evidence identifies its stable ID, requirement, environment and baseline, procedure, observation, conclusion, limits, and next action. An unavailable check is **not run**, never passed. Sources can justify a method choice; actual project observations establish whether it worked here.

## Complete one phase before planning the next

Only one created phase may be unfinished. Future phases stay high-level `not_planned` entries: no folders, detailed plans, checklists, methodologies, or evidence stubs, including drafts stored elsewhere.

Each created package contains `IMPLEMENTATION_PLAN.md`, `METHODOLOGY.md`, and `EVIDENCE.md`. Create only the immediately next numbered package after its predecessor fully closes and any required checkpoint approval is recorded.

A phase closes when:

- Its accepted scope is implemented and functional acceptance is observed.
- Required checks pass for the resulting baseline.
- A phase bug hunt and justified refactoring pass are complete.
- A fresh review covers the full phase scope after fixes, with all actionable findings resolved and no new ones.
- All affected phase and master documents are reconciled.

Every fifth stable development phase — 5, 10, 15, and onward — also needs a whole-repository bug hunt, refactoring pass, and fresh review. Cover inherited work and integrations as well as recent changes.

Repeat inspection, fixes, verification, and fresh full-scope review until those conditions hold. Use stable finding IDs and account for coverage. Refactor for a concrete reason while preserving accepted behavior; record when no refactor is warranted. Deferring an actionable finding does not resolve it. Failed or unavailable required checks, unresolved findings, incomplete documents, or indispensable missing prerequisites keep closure open.

Record actual reviewer settings when known. Model preferences are optional project configuration and do not imply an automatic switch.

## Recover from missing or conflicting context

Return to the reading order, locate the current phase and latest evidence, and compare the actual files with the recorded baseline. Use the smallest meaningful check to resolve contradictions. Preserve earlier observations and append corrections.

Later substantive changes invalidate affected acceptance and clean reviews. Reopen or renew the affected work explicitly rather than carrying an old completion claim onto changed files.

The validator checks structure and supported record references. It cannot establish that an entered result is true, an approval came from a human, or a review was thoughtful. Executable product checks and substantive review remain necessary. Adoption stays within the user's authorization and host permissions.
