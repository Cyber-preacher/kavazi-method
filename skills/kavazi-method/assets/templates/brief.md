# Project Brief — ${project}

This is the source of project intent. Preserve what the user actually supplied, then make the missing routine choices needed to build it. Established ${date}; [Core](${core_link}) governs the method.

## Captured user input

Source: ${brief_source}

${brief}

## Requirement derivation and assumptions

Define a complete, achievable outcome within the request, whether the input is one sentence or several pages. Give requirements stable IDs and retain their source. Distinguish these three kinds of statement:

| Kind | Record |
|---|---|
| User requirement | The actual instruction and where it came from |
| Repository observation | What was inspected or observed, with supporting evidence |
| Agent assumption | The inferred choice, reason, alternatives, and what would make you reconsider |

Make routine product, design, and technical choices yourself. If no input was captured, use actual user direction and repository evidence; do not manufacture a quotation or user preference.

## Execution preference

Initial mode: `${execution_mode}`. `.kavazi/config.json` owns the current mode.

In `autonomous`, continue authorized development through fully reviewed phases. In `phase_checkpoint`, work autonomously within the phase, close it fully, then wait for actual human approval before creating the next package. Never self-approve. Honor user steering and pauses; record concrete permission, host, credential, or external prerequisite limits. The host must support continued execution for prompt-and-forget to continue running.

## From intent to implementation

Derive [Master Architecture](${architecture_link}), then [Master Methodology](${methodology_link}), [Master Technical Core](${technical_core_link}), and [Master Implementation Plan](${master_plan_link}). Add supporting documents with a distinct purpose, then detail only the current phase.
