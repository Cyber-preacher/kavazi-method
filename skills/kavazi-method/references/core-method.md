# Core Kavazi Method

Method version 0.1.0.

Carry intent into implementation, and let evidence decide what is complete. Use an empirical, rational approach while keeping users, the wider product, and system consequences in view. A plan states intent; code defines a mechanism; execution shows what happened under specific conditions.

## The document route

Read applicable agent instructions and Core first. Then create, read, or recover the project in this order:

Actual user input → Project Brief → Master Architecture → Master Methodology → Master Technical Core → Master Implementation Plan → needed supporting documents → current phase package.

Core governs the whole route. Each document has a distinct responsibility:

| Document | Question it answers |
|---|---|
| Project Brief | What did the user ask for, and which choices did the agent infer? |
| Master Architecture | What should the project do, and what rules and boundaries govern it? |
| Master Methodology | How will the project be developed and verified, and why are those methods suitable? |
| Master Technical Core | Which components, interfaces, data, algorithms, failure handling, and checks realize each rule? |
| Master Implementation Plan | In what sequence will the project be built, and what depends on what? |
| Phase implementation plan | What must this phase deliver, and how will acceptance be demonstrated? |
| Phase methodology | Which methods, scenarios, and checks apply to this phase? |
| Phase evidence | What was decided, tried, observed, fixed, reviewed, and accepted? |

In a tool-managed project, `.kavazi/config.json` locates the documents and sets the execution mode. `.kavazi/state.json`, the phase ledger, owns status and next action. The master register displays that ledger; phase documents must not maintain competing statuses.

Preserve the user's product, accepted requirements, established paths, working changes, and dated history. Update existing masters rather than creating competing copies. Keep implemented behavior, proposed design, and historical observations distinct. Additional documents need a distinct purpose. Another project's technology stack, roadmap, platform, or model preference is not a requirement for this one.

## Input and autonomy

Input may be one sentence or several pages. Preserve the supplied text. Define a complete, achievable project within that request, then make routine product, design, and technical choices from repository evidence and relevant primary sources. Continue toward a usable finished product. A scaffold or MVP is sufficient only when it is the user's requested outcome.

Separate explicit user requirements, agent assumptions, and observed facts. For consequential decisions, record alternatives, rationale, wider consequences, and what would make you reconsider. An assumption supplies a missing design choice; it cannot supply a user preference, an execution result, or unrelated scope.

Default `autonomous` mode continues authorized work through fully reviewed sequential phases without routine design questions. `phase_checkpoint` performs the same autonomous work inside each phase, closes it fully, then stops before creating its successor. Actual human approval must be captured in evidence and recorded with `approve` before advancement. Never self-approve. The tool checks that an approval record is structurally supported; it cannot authenticate the human who gave it.

Honor user steering and pause requests in either mode. Permissions, credentials, external prerequisites, and host execution limits still apply. Record concrete blockers and continue independent authorized work in the current phase. Autonomy cannot supply missing observations or unlimited host execution.

## One phase at a time

Only one created phase may be unfinished. Each package contains `IMPLEMENTATION_PLAN.md`, `METHODOLOGY.md`, and `EVIDENCE.md`. Created phases are `planned`, `in_progress`, `blocked`, or `complete`. Future entries remain `not_planned`, with high-level outcomes and dependencies only.

Do not create future folders, detailed plans, checklists, methodologies, or evidence stubs, including drafts saved elsewhere. Parallel work stays inside the current phase with explicit file ownership and shared interfaces. Stable phase numbers are independent of sessions, missions, sprints, and releases.

Before creating the immediate successor:

1. Implement the accepted scope and demonstrate functional acceptance.
2. Pass required checks and the phase review process below. Every fifth phase also needs the whole-repository review.
3. Reconcile the phase package and all affected project documents, including Core, agent instructions, brief, architecture, methodology, Technical Core, roadmap, status, and next action.
4. Record supported completion. Derive the successor from actual results, lessons, and remaining dependencies; honor checkpoint approval when required.

Unresolved findings, failed or unavailable required checks, unfinished relevant documents, and indispensable missing execution prerequisites keep closure open. Deferring accepted work does not complete it. Resolve routine design uncertainty with recorded choices, and continue independent work in the current phase.

An agent-derived high-level roadmap may change when evidence warrants it; preserve stable numbers and history, and record the reason. Changes to explicit user scope or order require actual user direction.

If inherited future packages exist, distinguish unexecuted scaffolding from real implementation, decisions, and user work. Correct navigation and status so speculative content cannot authorize execution. Remove scaffolding only when the requested correction authorizes removal, retaining useful high-level intentions in the roadmap. Preserve genuine history and provenance. Record unresolved migration dependencies instead of relabeling inherited work as verified.

## The working cycle

Read the actual checkout, responsible contracts, current evidence, and next action. Define the intended result, existing behavior, technical owner, dependencies, and smallest check that can distinguish success from failure.

Record consequential decisions before or alongside implementation. Make coherent changes across affected inputs, rules, consequences, and presentation. Run suitable checks, preserve failures, and revise hypotheses when observations disagree. Update project contracts when behavior or methods change. Leave work items, evidence, and next action consistent for the next agent.

Use primary sources for methodological claims: research papers, authors' publications, official documentation, and practitioners' original work. Verify attribution and explain the supported claim, project adaptation, and limits. A published method still needs evidence of suitability here. Set meaningful numerical acceptance thresholds before measuring when applicable.

## Reviews required for closure

After functional requirements are met, inspect the entire delivered phase and affected integrations against its plan, methodology, architecture, and accepted product rules. Include inherited implementation on which it depends. A bug hunt and refactoring pass are required; make refactors only for a concrete reason and preserve accepted behavior.

Phases 5, 10, 15, 20, and onward also require a whole-repository review. Cover earlier phases, source, assets and content, tests, configuration, build and development tooling, documentation, and integrations. Recent changes alone cannot establish this coverage. Record what was inspected and how, including suitable inspection of binary or generated material; a filename list is insufficient.

For each required scope:

1. Inspect the resulting state, requirements, interactions, coverage, and required checks. Give findings stable IDs and distinguish demonstrated problems from hypotheses.
2. Fix actionable findings. Explain refactors and the behavior they preserve. If no refactor is warranted, record the inspected areas and reason.
3. Run required checks and affected regressions; verify earlier fixes. Preserve failures. An unavailable check is `not_run`.
4. Perform a fresh review of the entire required scope, interactions, and prior resolutions. Use an independent reviewer when available and useful. Record the actual reviewer and coverage.
5. Repeat fixes, verification, and fresh review until no new actionable findings appear, all earlier actionable findings are resolved, coverage is accounted for, and required checks pass on the reviewed state.

Do not substitute a fixed number of rounds. Reject a false positive with supporting evidence; deferral, accepted risk, or lower severity does not resolve a real finding. One review can satisfy both fifth-phase scopes only when its evidence explicitly covers both and meets every condition.

Close the phase only after acceptance, clean required reviews, passing checks, and document reconciliation are supported. Record actual reviewer model and effort when known. Optional model preferences do not switch models automatically. A clean review is limited to its state, scope, and procedure. Later substantive edits or findings reopen affected acceptance and review.

## Evidence that can be followed

Give meaningful entries stable IDs and dates. Record the requirement or question, consequential alternatives and decision, rationale, actual baseline and environment, reproducible procedure, observations, artifacts, failures, conclusion, limits, and follow-up. Include inputs, seeds, and tool versions when they matter. Keep the entry proportionate to the work.

For each review round, record scope, coverage, reviewer, finding IDs and statuses, fix or refactor rationale, preserved behavior, verification, and fresh-review result. Keep unresolved findings visible across rounds. Link final clean evidence from the phase plan and closure record. Store whole-repository review rounds in the closing fifth phase and link affected history.

Use live visible Markdown headings for evidence IDs. Examples inside fences, comments, or raw HTML cannot support closure; the tool reads supported plain Markdown rather than rendering all CommonMark forms.

Append corrections or superseding entries instead of erasing failures and earlier conclusions. Source inspection, compilation, tests, runtime observation, measurement, and release checks support different claims. Adoption creates starting records, not a verified execution history.

## Recovery and limits

After context loss, follow the document route, locate current evidence and responsible contracts, and compare the actual checkout with its recorded baseline. Resolve contradictions through requirement provenance and the smallest useful check. Keep unresolved uncertainty visible.

The tool checks links, record structure, phase eligibility, status, and supported references. It cannot prove product behavior, truthful attestations, or thoughtful review. Run product checks separately and inspect evidence substantively.

Apply Kavazi to requested work or an adopted repository. An ordinary task need not immediately close a phase. Editing the method does not authorize an unrelated repository audit. User direction and host permissions govern actions; adoption does not authorize publication, destructive operations, unrelated redesign, or permission changes.
