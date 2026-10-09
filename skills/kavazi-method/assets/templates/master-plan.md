# Master Implementation Plan — ${project}

Sequence the work needed to deliver the project. Start from [Project Brief](${brief_link}), [Master Architecture](${architecture_link}), [Master Methodology](${methodology_link}), and [Master Technical Core](${technical_core_link}); [Core](${core_link}) governs phase creation and completion.

## Phase register

[The phase ledger](${state_link}) owns status and next action. After valid state changes, refresh this generated block from the repository root:

${sync_command}
${tool_location_note}

${register}

## Initial adoption outcome and dependencies

Initial adoption outcome: ${outcome}

Derive a development sequence from the actual requirements and technical design. Give each phase a high-level outcome and dependencies. Detail only the eligible current phase. Generated documents are starting records; fill and reconcile the project design before relying on it for acceptance.

The [initial adoption package](${current_phase_link}) records starting context. Use `status` or the ledger to find the current phase after advancement.

## Supporting documents and future direction

Add documents only when they have a distinct purpose. Future phases keep high-level outcomes and dependencies, with no folders or detailed drafts. Create only the immediate successor after implemented scope, passing required checks, clean required reviews, and reconciled documents close the current phase. Every fifth phase also requires a whole-repository review.

In `autonomous`, continue authorized sequential work. In `phase_checkpoint`, stop after full closure and wait for actual human approval recorded through `approve` before creating the successor. Never self-approve. Honor later user steering and actual execution limits.
