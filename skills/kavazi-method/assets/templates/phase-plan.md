# Phase ${number} — ${title}

This plan defines what the current phase must deliver. First read [Core](${core_link}), [Project Brief](${brief_link}), [Master Architecture](${architecture_link}), [Master Methodology](${methodology_link}), [Master Technical Core](${technical_core_link}), and [Master Implementation Plan](${master_plan_link}) in order, then needed supporting documents. Use [phase methodology](METHODOLOGY.md) to choose checks and [evidence](EVIDENCE.md) to record results.

## Outcome and scope

${outcome}

Replace general intent with concrete work items, scope boundaries, dependencies, and acceptance conditions. Make routine missing choices yourself and label assumptions. Record consequential alternatives and wider consequences in evidence. This generated plan does not establish delivery.

## Work and acceptance

- [ ] Reconcile user input, architecture, methods, and technical design.
- [ ] Define scope, dependencies, and checks that distinguish success from failure.
- [ ] Implement the scope and record observed functional acceptance.
- [ ] Select required project check IDs in the ledger and pass them on the resulting state.
- [ ] Complete the phase bug hunt and justify refactors, or record why none is warranted.
- [ ] After fixes, review the entire phase scope afresh; repeat until no new or unresolved actionable findings remain.
- [ ] On every fifth phase, also complete a clean whole-repository review with explicit coverage.
- [ ] Reconcile affected project and phase documents and record supported closure.

## Status, mode, and next action

[The phase ledger](${state_link}) owns status and next action. Configuration owns execution mode. Update the ledger and append dated evidence; `status` reports the current entry. From the repository root, refresh the master register:

${sync_command}
${tool_location_note}

Complete this phase only after acceptance, passing required checks, clean required reviews of the resulting state, and document reconciliation. Open findings, failed or unavailable required checks, indispensable missing prerequisites, and unfinished relevant documents keep closure open. Parallel work stays here; future detailed packages cannot be drafted before closure.

In `autonomous`, continue authorized work through reviewed sequential phases. In `phase_checkpoint`, fully close this phase, then wait for actual human approval recorded with `approve` before creating the successor. Never self-approve. Approval cannot replace acceptance, checks, or review.
